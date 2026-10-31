from __future__ import annotations

import json

from config import EVALUATION_REPORT_PATH, ESCALATION_MODEL_PATH, MAX_TRAIN_ROWS, PRIORITY_MODEL_PATH, RANDOM_SEED
from src.data_loader import load_support_dataset
from src.evaluation import evaluate_models
from src.predict import load_model
from src.preprocessing import ticket_description_groups
from src.train_models import build_ticket_training_frame, split_ticket_data, train_models


def main():
    try:
        priority_model = load_model(PRIORITY_MODEL_PATH)
        escalation_model = load_model(ESCALATION_MODEL_PATH)
    except FileNotFoundError:
        print("Model artifacts were not found. Training them now...")
        train_models()
        priority_model = load_model(PRIORITY_MODEL_PATH)
        escalation_model = load_model(ESCALATION_MODEL_PATH)

    df = load_support_dataset(max_rows=MAX_TRAIN_ROWS).to_pandas()
    X_priority, y_priority = build_ticket_training_frame(df, "priority")
    X_escalation, y_escalation = build_ticket_training_frame(df, "escalated_to_human")
    groups = ticket_description_groups(df)
    Xp_train, Xp_test, yp_train, yp_test = split_ticket_data(
        X_priority, y_priority, groups.loc[X_priority.index], RANDOM_SEED
    )
    Xe_train, Xe_test, ye_train, ye_test = split_ticket_data(
        X_escalation, y_escalation, groups.loc[X_escalation.index], RANDOM_SEED
    )

    priority_train_groups = set(groups.loc[Xp_train.index])
    priority_test_groups = set(groups.loc[Xp_test.index])
    escalation_train_groups = set(groups.loc[Xe_train.index])
    escalation_test_groups = set(groups.loc[Xe_test.index])
    evaluation_metadata = {
        "dataset_rows": int(len(df)),
        "split_strategy": "first fold of StratifiedGroupKFold(n_splits=5, shuffle=True)",
        "group_key": "normalized issue_description",
        "random_seed": RANDOM_SEED,
        "priority": {
            "train_rows": int(len(Xp_train)),
            "test_rows": int(len(Xp_test)),
            "train_description_groups": len(priority_train_groups),
            "test_description_groups": len(priority_test_groups),
            "cross_split_duplicate_groups": len(priority_train_groups & priority_test_groups),
        },
        "escalation": {
            "train_rows": int(len(Xe_train)),
            "test_rows": int(len(Xe_test)),
            "train_description_groups": len(escalation_train_groups),
            "test_description_groups": len(escalation_test_groups),
            "cross_split_duplicate_groups": len(escalation_train_groups & escalation_test_groups),
        },
    }
    payload = evaluate_models(
        priority_model, escalation_model, Xp_test, yp_test, Xe_test, ye_test,
        evaluation_metadata=evaluation_metadata,
    )
    metrics_summary = {}
    for target in ("priority", "escalation"):
        metrics = payload[target]
        metrics_summary[target] = {
            key: metrics[key]
            for key in (
                "accuracy",
                "precision_macro",
                "recall_macro",
                "f1_macro",
                "f1_weighted",
                "class_distribution",
                "class_distribution_percentage",
                "training_seconds",
                "prediction_seconds",
                "decision_threshold",
                "false_positives",
                "false_negatives",
                "false_positive_rate",
                "labels",
                "confusion_matrix",
            )
            if key in metrics
        }
        metrics_summary[target]["per_class"] = {
            label: {
                "precision": class_metrics["precision"],
                "recall": class_metrics["recall"],
                "f1": class_metrics["f1-score"],
                "support": int(class_metrics["support"]),
            }
            for label, class_metrics in metrics["classification_report"].items()
            if label in metrics["labels"]
        }
    metrics_summary["evaluation_metadata"] = evaluation_metadata
    metrics_summary["report_path"] = str(EVALUATION_REPORT_PATH)
    print(json.dumps(metrics_summary, indent=2))


if __name__ == "__main__":
    main()
