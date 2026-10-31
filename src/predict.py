from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from config import ESCALATION_MODEL_PATH, PRIORITY_MODEL_PATH
from src.preprocessing import prepare_ticket_text


def load_model(model_path: str | Path):
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Model artifact not found at {path}. Train the model first using python -m scripts.train.")
    try:
        return joblib.load(path)
    except Exception as exc:  # pragma: no cover - user-facing validation path
        raise ValueError(f"Model artifact at {path} is invalid or corrupted: {exc}") from exc


def _prepare_inference_frame(subject: str, description: str):
    payload = pd.DataFrame([{"subject": subject, "issue_description": description}])
    payload = prepare_ticket_text(payload)
    default_numeric = {"customer_age": 0, "customer_tenure_months": 0, "previous_tickets": 0, "issue_complexity_score": 0}
    default_text = {"category": "unknown", "issue_type_id": "unknown", "product": "unknown", "channel": "unknown", "region": "unknown", "language": "unknown", "customer_gender": "unknown", "subscription_type": "unknown", "customer_segment": "unknown"}
    for col, value in default_numeric.items():
        if col not in payload.columns:
            payload[col] = value
    for col, value in default_text.items():
        if col not in payload.columns:
            payload[col] = value
    return payload


def predict_with_threshold(model, X, threshold: float | None = None, positive_label: str | None = None):
    threshold = getattr(model, "decision_threshold_", None) if threshold is None else threshold
    if threshold is None:
        return model.predict(X)
    classes = list(model.classes_)
    positive_label = positive_label or getattr(model, "positive_label_", "Yes")
    if positive_label not in classes:
        raise ValueError(f"Positive label {positive_label!r} is not present in model classes {classes!r}.")
    probabilities = np.asarray(model.predict_proba(X))
    positive_index = classes.index(positive_label)
    negative_labels = [label for label in classes if label != positive_label]
    if len(negative_labels) != 1:
        raise ValueError("Threshold-based predictions require a binary classifier.")
    return np.where(probabilities[:, positive_index] >= threshold, positive_label, negative_labels[0])


def predict_ticket_priority(subject: str, description: str, model=None):
    payload = _prepare_inference_frame(subject, description)
    if model is None:
        model = load_model(PRIORITY_MODEL_PATH)
    pred = model.predict(payload)[0]
    proba = model.predict_proba(payload)[0] if hasattr(model, "predict_proba") else None
    if proba is not None:
        class_index = list(model.classes_).index(pred)
        confidence = float(np.asarray(proba)[class_index])
    else:
        confidence = None
    classes = list(model.classes_) if hasattr(model, "classes_") else None
    return {"class": str(pred), "confidence": confidence, "probabilities": np.asarray(proba).tolist() if proba is not None else None, "classes": classes}


def predict_ticket_escalation(subject: str, description: str, model=None):
    payload = _prepare_inference_frame(subject, description)
    if model is None:
        model = load_model(ESCALATION_MODEL_PATH)
    pred = predict_with_threshold(model, payload)[0]
    proba = model.predict_proba(payload)[0] if hasattr(model, "predict_proba") else None
    if proba is not None:
        class_index = list(model.classes_).index(pred)
        confidence = float(np.asarray(proba)[class_index])
    else:
        confidence = None
    classes = list(model.classes_) if hasattr(model, "classes_") else None
    return {"class": str(pred), "confidence": confidence, "probabilities": np.asarray(proba).tolist() if proba is not None else None, "classes": classes}
