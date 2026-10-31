from __future__ import annotations

import json
import argparse
from time import perf_counter

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.utils.class_weight import compute_class_weight

from config import EXPERIMENT_REPORT_PATH, MAX_TRAIN_ROWS, RANDOM_SEED
from src.data_loader import load_support_dataset
from src.preprocessing import ticket_description_groups
from src.train_models import build_ticket_training_frame, split_ticket_data, train_classifier


def _metrics(y_true, predictions, labels):
    report = classification_report(y_true, predictions, labels=labels, output_dict=True, zero_division=0)
    counts = pd.Series(y_true).value_counts().reindex(labels, fill_value=0)
    return {
        "rows": int(len(y_true)),
        "class_counts": {label: int(counts[label]) for label in labels},
        "class_percentages": {label: round(float(counts[label] / len(y_true) * 100), 4) for label in labels},
        "accuracy": float(accuracy_score(y_true, predictions)),
        "precision_macro": float(precision_score(y_true, predictions, labels=labels, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, predictions, labels=labels, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_true, predictions, labels=labels, average="macro", zero_division=0)),
        "f1_weighted": float(f1_score(y_true, predictions, labels=labels, average="weighted", zero_division=0)),
        "per_class": {
            label: {
                "precision": report[label]["precision"],
                "recall": report[label]["recall"],
                "f1": report[label]["f1-score"],
                "support": int(report[label]["support"]),
            }
            for label in labels
        },
        "confusion_matrix": confusion_matrix(y_true, predictions, labels=labels).tolist(),
        "confusion_matrix_labels": labels,
    }


def _grouped_train_validation(X, y, groups, seed):
    X_train, X_validation, y_train, y_validation = split_ticket_data(X, y, groups, seed)
    overlap = set(groups.loc[X_train.index]) & set(groups.loc[X_validation.index])
    if overlap:
        raise RuntimeError(f"Grouped validation leakage detected for {len(overlap)} descriptions.")
    return X_train, X_validation, y_train, y_validation


def _select_priority_candidate(priority_results):
    recall_floors = {"Low": 0.35, "Medium": 0.35, "Urgent": 0.35}
    best_macro = max(result["validation"]["f1_macro"] for result in priority_results)
    eligible = [
        result for result in priority_results
        if result["validation"]["f1_macro"] >= best_macro - 0.01
        and all(
            result["validation"]["per_class"][label]["recall"] >= floor
            for label, floor in recall_floors.items()
        )
    ]
    if not eligible:
        eligible = [result for result in priority_results if result["name"] == "word_balanced_C1"]
    selected = max(
        eligible,
        key=lambda result: (
            result["validation"]["per_class"]["High"]["recall"],
            result["validation"]["f1_macro"],
        ),
    )
    return selected, recall_floors


def _fit_score(name, X_train, y_train, X_validation, y_validation, target, model_options, thresholds=None):
    start = perf_counter()
    model = train_classifier(X_train, y_train, target, **model_options)
    training_seconds = perf_counter() - start
    labels = sorted(pd.Series(y_train).unique())
    if thresholds is None:
        predictions = model.predict(X_validation)
        return {
            "name": name,
            "model_options": model_options,
            "training_seconds": training_seconds,
            "validation": _metrics(y_validation, predictions, labels),
        }

    probabilities = model.predict_proba(X_validation)
    classes = list(model.classes_)
    positive_index = classes.index("Yes")
    rows = []
    for threshold in thresholds:
        predictions = np.where(probabilities[:, positive_index] >= threshold, "Yes", "No")
        scores = _metrics(y_validation, predictions, ["No", "Yes"])
        scores["threshold"] = float(threshold)
        scores["false_positives"] = int(scores["confusion_matrix"][0][1])
        scores["false_negatives"] = int(scores["confusion_matrix"][1][0])
        scores["positive_class_precision"] = scores["per_class"]["Yes"]["precision"]
        scores["positive_class_recall"] = scores["per_class"]["Yes"]["recall"]
        scores["false_positive_rate"] = scores["false_positives"] / max(1, scores["class_counts"]["No"])
        rows.append(scores)
    return {
        "name": name,
        "model_options": model_options,
        "training_seconds": training_seconds,
        "threshold_results": rows,
    }


def run_experiments(max_rows: int = MAX_TRAIN_ROWS, random_state: int = RANDOM_SEED):
    df = load_support_dataset(max_rows=max_rows).to_pandas()
    groups_all = ticket_description_groups(df)
    priority_X, priority_y = build_ticket_training_frame(df, "priority")
    escalation_X, escalation_y = build_ticket_training_frame(df, "escalated_to_human")

    priority_outer_train, _, priority_y_outer_train, _ = split_ticket_data(
        priority_X, priority_y, groups_all.loc[priority_X.index], random_state
    )
    priority_groups = groups_all.loc[priority_outer_train.index]
    Xp_train, Xp_validation, yp_train, yp_validation = _grouped_train_validation(
        priority_outer_train, priority_y_outer_train, priority_groups, random_state + 1
    )

    balanced_weights = compute_class_weight(
        class_weight="balanced", classes=np.array(sorted(yp_train.unique())), y=yp_train
    )
    custom_weights = {
        label: float(weight)
        for label, weight in zip(sorted(yp_train.unique()), balanced_weights)
    }
    priority_candidates = [
        ("word_unweighted_C1", {"class_weight": None, "C": 1.0}),
        ("word_balanced_C1", {"class_weight": "balanced", "C": 1.0}),
        ("word_balanced_C0_5", {"class_weight": "balanced", "C": 0.5}),
        ("word_balanced_C2", {"class_weight": "balanced", "C": 2.0}),
        ("word_balanced_C4", {"class_weight": "balanced", "C": 4.0}),
        *[
            (
                f"word_custom_high_{scale:g}x_C1",
                {
                    "class_weight": {
                        **custom_weights,
                        "High": custom_weights["High"] * scale,
                    },
                    "C": 1.0,
                },
            )
            for scale in (1.15, 1.3, 1.5)
        ],
        (
            "word_char_balanced_C1",
            {
                "class_weight": "balanced",
                "C": 1.0,
                "word_tfidf_config": {"min_df": 2, "max_features": 200_000},
                "char_tfidf_config": {"max_features": 80_000, "min_df": 3},
            },
        ),
    ]
    priority_results = [
        _fit_score(name, Xp_train, yp_train, Xp_validation, yp_validation, "priority", options)
        for name, options in priority_candidates
    ]
    priority_selected, recall_floors = _select_priority_candidate(priority_results)

    escalation_outer_train, _, escalation_y_outer_train, _ = split_ticket_data(
        escalation_X, escalation_y, groups_all.loc[escalation_X.index], random_state
    )
    escalation_groups = groups_all.loc[escalation_outer_train.index]
    Xe_train, Xe_validation, ye_train, ye_validation = _grouped_train_validation(
        escalation_outer_train, escalation_y_outer_train, escalation_groups, random_state + 1
    )
    threshold_grid = np.round(np.linspace(0.20, 0.80, 61), 3)
    escalation_results = [
        _fit_score(
            name,
            Xe_train,
            ye_train,
            Xe_validation,
            ye_validation,
            "escalated_to_human",
            options,
            thresholds=threshold_grid,
        )
        for name, options in [
            ("word_unweighted_C1", {"class_weight": None, "C": 1.0}),
            ("word_balanced_C1", {"class_weight": "balanced", "C": 1.0}),
        ]
    ]
    balanced_default = next(result for result in escalation_results if result["name"] == "word_balanced_C1")
    baseline_threshold = min(balanced_default["threshold_results"], key=lambda result: abs(result["threshold"] - 0.5))
    precision_floor = max(0.70, baseline_threshold["positive_class_precision"] - 0.05)
    fpr_ceiling = baseline_threshold["false_positive_rate"] + 0.03
    eligible_thresholds = [
        (model_result, threshold_result)
        for model_result in escalation_results
        for threshold_result in model_result["threshold_results"]
        if threshold_result["positive_class_precision"] >= precision_floor
        and threshold_result["false_positive_rate"] <= fpr_ceiling
    ]
    if eligible_thresholds:
        selected_model, selected_threshold = max(
            eligible_thresholds,
            key=lambda pair: (
                pair[1]["positive_class_recall"],
                pair[1]["f1_macro"],
                pair[1]["positive_class_precision"],
            ),
        )
    else:
        selected_model, selected_threshold = next(
            (model_result, baseline_threshold)
            for model_result in escalation_results
            if model_result["name"] == "word_balanced_C1"
        )

    report = {
        "dataset_rows": int(len(df)),
        "random_seed": random_state,
        "outer_test_fold": "first fold of StratifiedGroupKFold(n_splits=5), normalized issue_description groups",
        "validation_fold": "first fold of StratifiedGroupKFold(n_splits=5) inside outer training partition; seed + 1",
        "selection_rule": {
            "priority": "Require at least 0.35 validation recall for Low, Medium, and Urgent; among candidates within 0.01 macro-F1 of the best validation result, choose the highest High recall.",
            "escalation": "Maximize Yes recall with Yes precision at least 0.05 below balanced-0.5 validation precision and false-positive rate at most 0.03 above balanced-0.5 validation FPR.",
            "escalation_precision_floor": precision_floor,
            "escalation_false_positive_rate_ceiling": fpr_ceiling,
            "priority_other_class_recall_floors": recall_floors,
        },
        "priority": {
            "train_rows": int(len(Xp_train)),
            "validation_rows": int(len(Xp_validation)),
            "validation_class_counts": yp_validation.value_counts().to_dict(),
            "candidates": priority_results,
            "selected": {
                "name": priority_selected["name"],
                "model_options": priority_selected["model_options"],
                "validation": priority_selected["validation"],
            },
        },
        "escalation": {
            "train_rows": int(len(Xe_train)),
            "validation_rows": int(len(Xe_validation)),
            "validation_class_counts": ye_validation.value_counts().to_dict(),
            "threshold_candidates": escalation_results,
            "selected": {
                "name": selected_model["name"],
                "model_options": selected_model["model_options"],
                "threshold": selected_threshold["threshold"],
                "validation": selected_threshold,
            },
        },
    }
    EXPERIMENT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXPERIMENT_REPORT_PATH.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(json.dumps({
        "report_path": str(EXPERIMENT_REPORT_PATH),
        "priority_selected": report["priority"]["selected"],
        "escalation_selected": report["escalation"]["selected"],
        "selection_rule": report["selection_rule"],
    }, indent=2))
    return report


def reselect_from_report():
    report = json.loads(EXPERIMENT_REPORT_PATH.read_text(encoding="utf-8"))
    selected, recall_floors = _select_priority_candidate(report["priority"]["candidates"])
    report["priority"]["selected"] = {
        "name": selected["name"],
        "model_options": selected["model_options"],
        "validation": selected["validation"],
    }
    report["selection_rule"]["priority"] = (
        "Require at least 0.35 validation recall for Low, Medium, and Urgent; "
        "among candidates within 0.01 macro-F1 of the best validation result, choose the highest High recall."
    )
    report["selection_rule"]["priority_other_class_recall_floors"] = recall_floors
    EXPERIMENT_REPORT_PATH.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description="Run grouped training-only model selection experiments.")
    parser.add_argument("--rows", type=int, default=MAX_TRAIN_ROWS, help="Hugging Face training rows to sample.")
    parser.add_argument("--seed", type=int, default=RANDOM_SEED, help="Fixed random seed for grouped splits.")
    parser.add_argument("--reselect", action="store_true", help="Reapply the selection rule to an existing report without refitting candidates.")
    args = parser.parse_args()
    if args.reselect:
        report = reselect_from_report()
        print(json.dumps({
            "report_path": str(EXPERIMENT_REPORT_PATH),
            "priority_selected": report["priority"]["selected"],
            "escalation_selected": report["escalation"]["selected"],
            "selection_rule": report["selection_rule"],
        }, indent=2))
    else:
        run_experiments(max_rows=args.rows, random_state=args.seed)


if __name__ == "__main__":
    main()