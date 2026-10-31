from __future__ import annotations

import pandas as pd

from src.predict import load_model, predict_ticket_priority, predict_ticket_escalation
from src.train_models import build_ticket_training_frame, train_classifier


def _build_model_dataset():
    data = pd.DataFrame(
        {
            "subject": [
                "Login issue after password reset",
                "Billing mismatch refund request",
                "App freezes when opening dashboard",
                "Refund not processed after payment",
                "Dashboard loads slowly for new users",
                "Refund for duplicate charge",
            ],
            "issue_description": [
                "I cannot sign in after resetting my password.",
                "My refund request is delayed and invoice mismatched.",
                "The app freezes when loading the dashboard.",
                "My payment was taken twice and no refund appears.",
                "The dashboard loads slowly for all new user accounts.",
                "I was charged twice for the same order.",
            ],
            "category": ["login", "billing", "technical", "billing", "performance", "billing"],
            "product": ["app", "billing", "app", "billing", "app", "billing"],
            "customer_age": [28, 45, 33, 41, 29, 36],
            "customer_tenure_months": [8, 20, 11, 18, 5, 10],
            "priority": ["high", "medium", "high", "high", "medium", "medium"],
            "escalated_to_human": ["yes", "no", "yes", "yes", "no", "yes"],
        }
    )
    return data


def test_empty_ticket_input_is_rejected():
    from src.pipeline import validate_ticket

    try:
        validate_ticket("", "")
        assert False, "Expected ValueError for empty input"
    except ValueError:
        pass


def test_non_empty_tickets_can_be_preprocessed():
    from src.preprocessing import prepare_ticket_text

    df = pd.DataFrame({"subject": ["Login issue"], "issue_description": ["Unable to sign in after reset"]})
    prepared = prepare_ticket_text(df)
    assert "ticket_text" in prepared.columns
    assert prepared["ticket_text"].iloc[0].startswith("Login issue")


def test_safe_features_exclude_both_targets_identifiers_and_outcomes():
    from config import POST_OUTCOME_FIELDS, SAFE_STRUCTURED_FIELDS
    from src.preprocessing import safe_feature_columns

    data = _build_model_dataset()
    data["ticket_id"] = [f"ticket-{index}" for index in range(len(data))]
    data["customer_email"] = [f"customer-{index}@example.com" for index in range(len(data))]
    data["resolved_at"] = pd.Timestamp("2025-01-01")
    data["unexpected_numeric_outcome"] = range(len(data))

    for target in ("priority", "escalated_to_human"):
        features = safe_feature_columns(data, target)
        assert "priority" not in features
        assert "escalated_to_human" not in features
        assert not {"ticket_id", "customer_name", "customer_email", "created_at"} & set(features)
        assert not POST_OUTCOME_FIELDS & set(features)
        assert "unexpected_numeric_outcome" not in features
        assert set(features) <= set(SAFE_STRUCTURED_FIELDS)


def test_string_extension_features_use_categorical_preprocessing():
    from src.preprocessing import make_model_preprocessor

    data = _build_model_dataset().astype({"category": "string", "product": "string"})
    preprocessor = make_model_preprocessor(data, "priority")
    categorical = next(transformer for transformer in preprocessor.transformers if transformer[0] == "categorical")

    assert categorical[2] == ["category", "product"]


def test_grouped_split_keeps_duplicate_descriptions_out_of_both_sides():
    from src.preprocessing import ticket_description_groups
    from src.train_models import split_ticket_data

    data = pd.DataFrame(
        {
            "issue_description": [
                description
                for index in range(30)
                for description in (f"Issue {index}", f"  ISSUE {index}  ")
            ]
        }
    )
    X = pd.DataFrame({"feature": range(len(data))})
    y = pd.Series([str(index % 3) for index in range(30) for _ in range(2)])
    groups = ticket_description_groups(data)

    X_train, X_test, _, _ = split_ticket_data(X, y, groups, random_state=42)

    assert set(groups.iloc[X_train.index]).isdisjoint(set(groups.iloc[X_test.index]))


def test_prediction_pipeline_returns_valid_output_structures():
    data = _build_model_dataset()
    X_priority, y_priority = build_ticket_training_frame(data, "priority")
    X_escalation, y_escalation = build_ticket_training_frame(data, "escalated_to_human")
    priority_model = train_classifier(X_priority, y_priority, "priority")
    escalation_model = train_classifier(X_escalation, y_escalation, "escalated_to_human")

    priority_output = predict_ticket_priority("Login issue", "Cannot sign in after reset", model=priority_model)
    escalation_output = predict_ticket_escalation("Login issue", "Cannot sign in after reset", model=escalation_model)

    assert set(priority_output.keys()) >= {"class", "confidence", "probabilities", "classes"}
    assert set(escalation_output.keys()) >= {"class", "confidence", "probabilities", "classes"}
    assert priority_output["confidence"] is not None
    assert escalation_output["confidence"] is not None


def test_priority_predictions_use_the_actual_trained_class_labels():
    data = _build_model_dataset()
    X, y = build_ticket_training_frame(data, "priority")
    model = train_classifier(X, y, "priority")
    output = predict_ticket_priority("Login issue", "Cannot sign in after reset", model=model)
    assert set(output["classes"]) == set(y.unique())


def test_escalation_predictions_use_the_actual_trained_class_labels():
    data = _build_model_dataset()
    X, y = build_ticket_training_frame(data, "escalated_to_human")
    model = train_classifier(X, y, "escalated_to_human")
    output = predict_ticket_escalation("Billing issue", "Payment was taken twice", model=model)
    assert set(output["classes"]) == set(y.unique())


def test_escalation_inference_uses_saved_positive_class_threshold():
    import numpy as np
    from src.predict import predict_with_threshold

    class ThresholdModel:
        classes_ = np.array(["No", "Yes"])
        decision_threshold_ = 0.7
        positive_label_ = "Yes"

        def predict(self, X):
            return np.array(["Yes"] * len(X))

        def predict_proba(self, X):
            return np.array([[0.4, 0.6], [0.2, 0.8]])

    predictions = predict_with_threshold(ThresholdModel(), pd.DataFrame(index=[0, 1]))

    assert predictions.tolist() == ["No", "Yes"]


def test_saved_pipeline_round_trip_preserves_prediction_contract(tmp_path):
    import joblib

    data = _build_model_dataset()
    X, y = build_ticket_training_frame(data, "escalated_to_human")
    model = train_classifier(X, y, "escalated_to_human")
    model.decision_threshold_ = 0.6
    model.positive_label_ = "yes"
    model_path = tmp_path / "escalation.joblib"
    joblib.dump(model, model_path)

    loaded_model = load_model(model_path)
    prediction = predict_ticket_escalation("Billing issue", "Payment was taken twice", model=loaded_model)

    assert prediction["class"] in set(y)
    assert loaded_model.decision_threshold_ == 0.6


def test_evaluation_reports_thresholded_metrics_and_class_percentages(tmp_path, monkeypatch):
    import numpy as np
    import src.evaluation as evaluation

    class ThresholdModel:
        classes_ = np.array(["No", "Yes"])
        decision_threshold_ = 0.7
        positive_label_ = "Yes"

        def predict(self, X):
            return np.array(["No"] * len(X))

        def predict_proba(self, X):
            return np.array([[0.4, 0.6], [0.1, 0.9], [0.35, 0.65], [0.15, 0.85]])

    monkeypatch.setattr(evaluation, "REPORTS_DIR", tmp_path)
    metrics = evaluation.evaluate_classifier(
        ThresholdModel(), pd.DataFrame(index=range(4)), pd.Series(["No", "No", "Yes", "Yes"])
    )

    assert metrics["confusion_matrix"] == [[1, 1], [1, 1]]
    assert metrics["class_distribution_percentage"] == {"No": 50.0, "Yes": 50.0}
    assert metrics["decision_threshold"] == 0.7


def test_training_rejects_stale_experiment_configuration(tmp_path, monkeypatch):
    import json
    import src.train_models as training

    report_path = tmp_path / "experiment_report.json"
    report_path.write_text(json.dumps({"dataset_rows": 500, "random_seed": 42}), encoding="utf-8")
    monkeypatch.setattr(training, "EXPERIMENT_REPORT_PATH", report_path)

    try:
        training.selected_training_configuration(dataset_rows=1000, random_state=42)
        assert False, "Expected stale experiment settings to be rejected"
    except ValueError as exc:
        assert "does not match" in str(exc)


def test_priority_selector_guards_other_class_recall_while_prioritizing_high_recall():
    from scripts.experiment_models import _select_priority_candidate

    def candidate(name, macro, recalls):
        return {
            "name": name,
            "model_options": {"C": 1.0},
            "validation": {
                "f1_macro": macro,
                "per_class": {
                    label: {"recall": value}
                    for label, value in recalls.items()
                },
            },
        }

    candidates = [
        candidate("best_macro_collapses_urgent", 0.42, {"High": 0.8, "Low": 0.7, "Medium": 0.6, "Urgent": 0.2}),
        candidate("balanced_candidate", 0.413, {"High": 0.3, "Low": 0.7, "Medium": 0.5, "Urgent": 0.4}),
        candidate("high_recall_candidate", 0.412, {"High": 0.5, "Low": 0.7, "Medium": 0.5, "Urgent": 0.4}),
    ]

    selected, recall_floors = _select_priority_candidate(candidates)

    assert selected["name"] == "high_recall_candidate"
    assert recall_floors == {"Low": 0.35, "Medium": 0.35, "Urgent": 0.35}


def test_confidence_fields_are_handled_correctly_when_probabilities_are_available():
    data = _build_model_dataset()
    X, y = build_ticket_training_frame(data, "priority")
    model = train_classifier(X, y, "priority")
    output = predict_ticket_priority("Dashboard issue", "Slow app loading", model=model)
    assert isinstance(output["confidence"], float)
    assert 0.0 <= output["confidence"] <= 1.0
    assert len(output["probabilities"]) == len(output["classes"])


def test_missing_model_artifacts_produce_a_clear_error():
    try:
        load_model("/tmp/definitely_missing_model.joblib")
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError as exc:
        assert "not found" in str(exc).lower()
