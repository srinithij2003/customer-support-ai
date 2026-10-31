from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score

from config import EVALUATION_REPORT_PATH, REPORTS_DIR
from src.predict import predict_with_threshold


def evaluate_classifier(model, X_test, y_test, label_names=None):
    y_true = pd.Series(y_test).astype(str)
    prediction_start = perf_counter()
    y_pred = pd.Series(predict_with_threshold(model, X_test)).astype(str)
    prediction_seconds = perf_counter() - prediction_start
    labels = label_names if label_names is not None else sorted(set(y_true.unique()) | set(y_pred.unique()))
    acc = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average="macro", zero_division=0)
    recall = recall_score(y_true, y_pred, average="macro", zero_division=0)
    f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    class_report = classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.imshow(cm, interpolation="nearest", cmap="Blues")
    ax.set_title("Confusion Matrix")
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45)
    ax.set_yticklabels(labels)
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, cm[i, j], ha="center", va="center", color="black")
    fig.tight_layout()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(REPORTS_DIR / f"confusion_matrix_{'_'.join(labels[:2]) if labels else 'model'}.png", dpi=150)
    plt.close(fig)

    metrics = {
        "accuracy": float(acc),
        "precision_macro": float(precision),
        "recall_macro": float(recall),
        "f1_macro": float(f1),
        "f1_weighted": float(weighted_f1),
        "classification_report": class_report,
        "confusion_matrix": cm.tolist(),
        "labels": labels,
        "class_distribution": y_true.value_counts().to_dict(),
        "class_distribution_percentage": (y_true.value_counts(normalize=True) * 100).round(4).to_dict(),
        "training_seconds": getattr(model, "training_seconds_", None),
        "prediction_seconds": prediction_seconds,
        "decision_threshold": getattr(model, "decision_threshold_", None),
    }
    if len(labels) == 2 and "Yes" in labels and "No" in labels:
        no_index, yes_index = labels.index("No"), labels.index("Yes")
        metrics["false_positives"] = int(cm[no_index, yes_index])
        metrics["false_negatives"] = int(cm[yes_index, no_index])
        metrics["false_positive_rate"] = float(cm[no_index, yes_index] / max(1, cm[no_index].sum()))
    return metrics


def save_evaluation_report(metrics_by_model: dict, report_path: str | Path = EVALUATION_REPORT_PATH):
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metrics_by_model, indent=2, default=str), encoding="utf-8")
    return str(path)


def evaluate_models(priority_model, escalation_model, Xp_test, yp_test, Xe_test, ye_test, evaluation_metadata=None):
    priority_metrics = evaluate_classifier(priority_model, Xp_test, yp_test)
    escalation_metrics = evaluate_classifier(escalation_model, Xe_test, ye_test)
    payload = {
        "priority": priority_metrics,
        "escalation": escalation_metrics,
    }
    if evaluation_metadata is not None:
        payload["evaluation_metadata"] = evaluation_metadata
    save_evaluation_report(payload)
    return payload
