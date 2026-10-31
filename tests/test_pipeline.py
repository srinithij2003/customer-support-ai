from __future__ import annotations

from src.pipeline import analyze_ticket, validate_ticket


def test_pipeline_handles_missing_rag_index_while_returning_ml_predictions(monkeypatch):
    class DummyModel:
        def predict(self, X):
            return ["high"]

        def predict_proba(self, X):
            return [[0.7, 0.3]]

        @property
        def classes_(self):
            return ["high", "low"]

    monkeypatch.setattr("src.pipeline.load_models", lambda: {"priority": DummyModel(), "escalation": DummyModel()})
    monkeypatch.setattr("src.pipeline.load_documents", lambda *args, **kwargs: [])
    monkeypatch.setattr("src.pipeline.iter_supported_documents", lambda *args, **kwargs: [])

    result = analyze_ticket("Password reset", "I cannot sign in after resetting my password.")
    assert result["priority"]["class"] == "high"
    assert "rag" in result
    assert result["rag"]["available"] is False
    assert "predictions are available" in result["rag"]["message"].lower()
