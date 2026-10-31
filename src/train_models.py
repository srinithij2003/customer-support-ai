from __future__ import annotations

import json
from time import perf_counter
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline

from config import (
    DATASET_SUMMARY_PATH,
    ESCALATION_DECISION_THRESHOLD,
    ESCALATION_MODEL_CONFIG,
    ESCALATION_MODEL_PATH,
    EXPERIMENT_REPORT_PATH,
    MAX_TRAIN_ROWS,
    PRIORITY_MODEL_CONFIG,
    PRIORITY_MODEL_PATH,
    RANDOM_SEED,
    REPORTS_DIR,
)
from src.data_loader import build_dataset_summary, load_support_dataset
from src.preprocessing import make_model_preprocessor, prepare_ticket_text, safe_feature_columns, ticket_description_groups


def build_ticket_training_frame(df: pd.DataFrame, target_name: str):
    df = prepare_ticket_text(df.copy())
    if target_name not in df.columns:
        raise ValueError(f"Target column '{target_name}' not found in dataset. Available columns: {list(df.columns)}")
    df = df.dropna(subset=[target_name]).copy()
    df[target_name] = df[target_name].fillna("missing").astype(str)
    if "ticket_text" not in df.columns:
        raise ValueError("Ticket text column was not created during preprocessing.")
    feature_columns = safe_feature_columns(df, target_name)
    selected = feature_columns + ["ticket_text"]
    X = df[selected]
    y = df[target_name].astype(str)
    return X, y


def train_classifier(
    X,
    y,
    target_name: str,
    class_weight: str | dict | None = "balanced",
    C: float = 1.0,
    word_tfidf_config: dict | None = None,
    char_tfidf_config: dict | None = None,
):
    model = LogisticRegression(max_iter=2500, solver="lbfgs", class_weight=class_weight, C=C)
    preprocessor = make_model_preprocessor(
        pd.concat([X, pd.Series(y, name=target_name)], axis=1),
        target_name,
        word_tfidf_config=word_tfidf_config,
        char_tfidf_config=char_tfidf_config,
    )
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", model),
    ])
    pipeline.fit(X, y)
    return pipeline


def split_ticket_data(X, y, groups, random_state: int = RANDOM_SEED):
    group_values = pd.Series(groups, index=X.index).astype(str)
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=random_state)
    train_indices, test_indices = next(splitter.split(X, y, groups=group_values))
    return (
        X.iloc[train_indices],
        X.iloc[test_indices],
        y.iloc[train_indices],
        y.iloc[test_indices],
    )


def selected_training_configuration(dataset_rows: int, random_state: int):
    if not EXPERIMENT_REPORT_PATH.exists():
        return PRIORITY_MODEL_CONFIG, ESCALATION_MODEL_CONFIG, ESCALATION_DECISION_THRESHOLD
    experiment = json.loads(EXPERIMENT_REPORT_PATH.read_text(encoding="utf-8"))
    if experiment.get("dataset_rows") != dataset_rows or experiment.get("random_seed") != random_state:
        raise ValueError(
            "The experiment report does not match this training dataset size and random seed. "
            "Rerun `python -m scripts.experiment_models` with matching settings first."
        )
    priority = experiment.get("priority", {}).get("selected", {}).get("model_options", PRIORITY_MODEL_CONFIG)
    escalation = experiment.get("escalation", {}).get("selected", {})
    escalation_options = escalation.get("model_options", ESCALATION_MODEL_CONFIG)
    threshold = float(escalation.get("threshold", ESCALATION_DECISION_THRESHOLD))
    return priority, escalation_options, threshold


def train_models(max_rows: int = MAX_TRAIN_ROWS, random_state: int = RANDOM_SEED):
    dataset = load_support_dataset(max_rows=max_rows)
    df = dataset.to_pandas()
    if "priority" not in df.columns or "escalated_to_human" not in df.columns:
        raise ValueError("Dataset does not contain the expected target columns: 'priority' and 'escalated_to_human'.")
    build_dataset_summary(df, DATASET_SUMMARY_PATH)

    X_priority, y_priority = build_ticket_training_frame(df, "priority")
    X_escalation, y_escalation = build_ticket_training_frame(df, "escalated_to_human")
    description_groups = ticket_description_groups(df)

    Xp_train, Xp_test, yp_train, yp_test = split_ticket_data(
        X_priority, y_priority, description_groups.loc[X_priority.index], random_state
    )
    Xe_train, Xe_test, ye_train, ye_test = split_ticket_data(
        X_escalation, y_escalation, description_groups.loc[X_escalation.index], random_state
    )

    priority_config, escalation_config, escalation_threshold = selected_training_configuration(len(df), random_state)
    priority_start = perf_counter()
    priority_pipeline = train_classifier(Xp_train, yp_train, "priority", **priority_config)
    priority_training_seconds = perf_counter() - priority_start
    priority_pipeline.training_seconds_ = priority_training_seconds
    escalation_start = perf_counter()
    escalation_pipeline = train_classifier(Xe_train, ye_train, "escalated_to_human", **escalation_config)
    escalation_training_seconds = perf_counter() - escalation_start
    escalation_pipeline.training_seconds_ = escalation_training_seconds
    escalation_pipeline.decision_threshold_ = escalation_threshold
    escalation_pipeline.positive_label_ = "Yes"

    PRIORITY_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    ESCALATION_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(priority_pipeline, PRIORITY_MODEL_PATH)
    joblib.dump(escalation_pipeline, ESCALATION_MODEL_PATH)

    summary = {
        "priority_model": str(PRIORITY_MODEL_PATH),
        "escalation_model": str(ESCALATION_MODEL_PATH),
        "train_rows": int(len(df)),
        "priority_distribution": y_priority.value_counts().to_dict(),
        "escalation_distribution": y_escalation.value_counts().to_dict(),
        "evaluation_split": "first fold of StratifiedGroupKFold(n_splits=5), grouped by normalized issue_description",
        "priority_train_rows": int(len(Xp_train)),
        "priority_test_rows": int(len(Xp_test)),
        "escalation_train_rows": int(len(Xe_train)),
        "escalation_test_rows": int(len(Xe_test)),
        "priority_model_config": priority_config,
        "escalation_model_config": escalation_config,
        "escalation_decision_threshold": escalation_threshold,
        "priority_training_seconds": priority_training_seconds,
        "escalation_training_seconds": escalation_training_seconds,
    }
    (REPORTS_DIR / "model_summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return {
        "priority_model": priority_pipeline,
        "escalation_model": escalation_pipeline,
        "priority_test": (Xp_test, yp_test),
        "escalation_test": (Xe_test, ye_test),
        "priority_training_seconds": priority_training_seconds,
        "escalation_training_seconds": escalation_training_seconds,
    }


if __name__ == "__main__":
    train_models()
