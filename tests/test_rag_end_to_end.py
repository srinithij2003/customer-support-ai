from __future__ import annotations

import hashlib
import re

import numpy as np

from src.embeddings import EmbeddingProvider
from src.pipeline import analyze_ticket, build_document_index


class DummyModel:
    classes_ = np.array(["No", "Yes"])

    def predict(self, X):
        return np.array(["No"])

    def predict_proba(self, X):
        return np.array([[0.8, 0.2]])


def _deterministic_embeddings(texts):
    vectors = np.zeros((len(texts), 128), dtype=np.float32)
    for row_index, text in enumerate(texts):
        for token in re.findall(r"[a-z0-9]+", text.casefold()):
            bucket = int.from_bytes(hashlib.sha256(token.encode("utf-8")).digest()[:4], "little") % vectors.shape[1]
            vectors[row_index, bucket] += 1.0
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.maximum(norms, 1e-12)


def _write_text_pdf(path, text):
    escaped_text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 12 Tf 72 720 Td ({escaped_text}) Tj ET".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_number, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{object_number} 0 obj\n".encode("ascii"))
        pdf.extend(body + b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    path.write_bytes(pdf)


def _patch_test_services(monkeypatch, index_path, metadata_path):
    monkeypatch.setattr(EmbeddingProvider, "encode", lambda self, texts: _deterministic_embeddings(texts))
    monkeypatch.setattr(
        "src.pipeline.load_models",
        lambda: {"priority": DummyModel(), "escalation": DummyModel()},
    )


def test_real_text_and_markdown_ingestion_retrieval_citations_and_abstention(tmp_path, monkeypatch):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "account-guide.md").write_text(
        "# Password reset\n\n"
        "To reset a password, open Account Security and choose Reset Password. "
        "A verification code is sent to the registered email address.\n\n"
        "If the code has expired, request a new verification code from Account Security.\n\n"
        "# Billing\n\n"
        "To review a duplicate charge, open Billing History and select the transaction.",
        encoding="utf-8",
    )
    (docs_dir / "support-notes.txt").write_text(
        "Password reset codes expire after ten minutes. Do not share verification codes with anyone.\n\n"
        "For billing questions, include the transaction date when contacting support.",
        encoding="utf-8",
    )
    _write_text_pdf(docs_dir / "device-guide.pdf", "Restart the device by holding the power button for five seconds.")
    index_path = tmp_path / "index" / "docs.faiss"
    metadata_path = tmp_path / "index" / "docs.joblib"
    _patch_test_services(monkeypatch, index_path, metadata_path)

    build_result = build_document_index(docs_dir, chunk_size=120, overlap=20, index_path=index_path, metadata_path=metadata_path)
    assert build_result["available"] is True
    assert build_result["documents"] == 3
    assert build_result["chunks"] >= 3

    result = analyze_ticket(
        "Password reset",
        "The verification code expired while I tried to reset my password.",
        docs_dir=docs_dir,
        index_path=index_path,
        metadata_path=metadata_path,
    )
    rag = result["rag"]
    assert rag["available"] is True
    assert rag["response"]["mode"] == "extractive"
    assert "[1]" in rag["response"]["response"]
    assert rag["response"]["supporting_sources"]
    assert all(citation["source"] in {"account-guide.md", "support-notes.txt", "device-guide.pdf"} for citation in rag["response"]["supporting_sources"])
    assert all(citation["text"] and citation["chunk_id"] for citation in rag["response"]["supporting_sources"])
    assert any(citation["section"] == "Password reset" for citation in rag["response"]["supporting_sources"])

    pdf_result = analyze_ticket(
        "Device restart",
        "How long should I hold the power button to restart the device?",
        docs_dir=docs_dir,
        index_path=index_path,
        metadata_path=metadata_path,
    )["rag"]["response"]
    assert pdf_result["mode"] == "extractive"
    assert pdf_result["supporting_sources"][0]["source"] == "device-guide.pdf"
    assert pdf_result["supporting_sources"][0]["page"] == 1

    multi_passage = analyze_ticket(
        "Password reset",
        "The verification code expired. How do I request a new password reset code?",
        docs_dir=docs_dir,
        index_path=index_path,
        metadata_path=metadata_path,
    )["rag"]["response"]
    assert multi_passage["mode"] == "extractive"
    assert len(multi_passage["supporting_sources"]) >= 2

    unsupported = analyze_ticket(
        "Underwater aircraft warranty",
        "What is the warranty for the underwater aircraft navigation module?",
        docs_dir=docs_dir,
        index_path=index_path,
        metadata_path=metadata_path,
    )["rag"]
    assert unsupported["response"]["mode"] == "unsupported"
    assert unsupported["response"]["supporting_sources"] == []
    assert "does not sufficiently support" in unsupported["message"].lower()


def test_empty_document_directory_clears_stale_index_and_keeps_predictions(monkeypatch, tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    index_path = tmp_path / "index.faiss"
    metadata_path = tmp_path / "metadata.joblib"
    index_path.write_bytes(b"old index")
    metadata_path.write_bytes(b"old metadata")
    _patch_test_services(monkeypatch, index_path, metadata_path)

    build_result = build_document_index(docs_dir, index_path=index_path, metadata_path=metadata_path)
    assert build_result["available"] is False
    assert not index_path.exists()
    assert not metadata_path.exists()

    result = analyze_ticket(
        "Password reset",
        "I cannot reset my password.",
        docs_dir=docs_dir,
        index_path=index_path,
        metadata_path=metadata_path,
    )
    assert result["priority"]["class"] == "No"
    assert result["rag"]["response"]["mode"] == "unsupported"
    assert "no supported product documentation" in result["rag"]["message"].lower()


def test_invalid_supported_files_are_reported_and_do_not_leave_stale_index(monkeypatch, tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "broken.pdf").write_bytes(b"this is not a PDF")
    (docs_dir / "empty.md").write_text("# Empty section\n\n", encoding="utf-8")
    index_path = tmp_path / "index.faiss"
    metadata_path = tmp_path / "metadata.joblib"
    index_path.write_bytes(b"old index")
    metadata_path.write_bytes(b"old metadata")
    _patch_test_services(monkeypatch, index_path, metadata_path)

    result = build_document_index(docs_dir, index_path=index_path, metadata_path=metadata_path)

    assert result["available"] is False
    assert "no readable text" in result["message"].lower()
    assert not index_path.exists()
    assert not metadata_path.exists()


def test_embedding_failure_is_reported_and_clears_stale_index(monkeypatch, tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "guide.txt").write_text("Reset passwords from Account Security.", encoding="utf-8")
    index_path = tmp_path / "index.faiss"
    metadata_path = tmp_path / "metadata.joblib"
    index_path.write_bytes(b"old index")
    metadata_path.write_bytes(b"old metadata")
    monkeypatch.setattr("src.pipeline.build_faiss_index", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("embedding unavailable")))

    result = build_document_index(docs_dir, index_path=index_path, metadata_path=metadata_path)

    assert result["available"] is False
    assert "embedding or index creation failed" in result["message"].lower()
    assert not index_path.exists()
    assert not metadata_path.exists()
