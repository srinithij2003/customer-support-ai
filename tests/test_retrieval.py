from __future__ import annotations

import numpy as np

from src.response_generator import build_grounded_response
from src.retrieval import search_documents


def test_retrieval_returns_valid_source_metadata(monkeypatch):
    fake_index = type("FakeIndex", (), {"search": lambda self, query, k: (np.array([[0.92]], dtype="float32"), np.array([[0]], dtype="int64"))})()
    metadata = [{"text": "Follow troubleshooting guide.", "source": "manual.pdf", "file_type": "pdf", "page": 3, "section": "Troubleshooting", "chunk_id": "chunk-1"}]

    monkeypatch.setattr("src.retrieval.load_faiss_index", lambda *args, **kwargs: (fake_index, metadata))
    monkeypatch.setattr("src.retrieval.EmbeddingProvider.encode", lambda self, texts: np.array([[1.0, 0.0]], dtype="float32"))

    result = search_documents("reset password", top_k=1, threshold=0.1)
    assert result[0]["source"] == "manual.pdf"
    assert result[0]["page"] == 3
    assert result[0]["section"] == "Troubleshooting"


def test_retrieval_with_no_relevant_results_triggers_the_fallback():
    response = build_grounded_response("We need support on an unsupported item.", [])
    assert response["mode"] == "unsupported"
    assert "supporting information" in response["response"].lower()


def test_unsupported_questions_do_not_receive_fabricated_product_instructions():
    response = build_grounded_response("Explain the warranty policy for our custom hardware.", [])
    assert "no product instructions were inferred" in response["response"].lower()


def test_weakly_related_passage_is_not_included_in_grounded_answer():
    passages = [
        {
            "text": "A password reset link expires after 30 minutes. Request a new reset link.",
            "source": "account.md",
            "page": 1,
            "section": "CC-DOC-01 §5.2",
            "score": 0.8,
            "chunk_id": "account-reset-1",
        },
        {
            "text": "Support priority is High when a core function is badly affected for many shoppers.",
            "source": "support.md",
            "page": 1,
            "section": "CC-DOC-07 §2",
            "score": 0.6,
            "chunk_id": "support-priority-1",
        },
    ]

    response = build_grounded_response("My password reset link expired. How can I reset my password?", passages)

    assert response["mode"] == "extractive"
    assert len(response["supporting_sources"]) == 1
    assert response["supporting_sources"][0]["source"] == "account.md"
    assert "Support priority" not in response["response"]
