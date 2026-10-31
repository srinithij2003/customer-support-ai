from __future__ import annotations

from pathlib import Path

from src.chunking import chunk_documents
from src.document_loader import extract_text_from_file, load_documents


def test_empty_document_collections_do_not_crash_the_application(tmp_path):
    assert load_documents(tmp_path) == []


def test_document_chunking_preserves_metadata():
    documents = [{"source": "manual.txt", "file_type": "txt", "page": 2, "section": "FAQ", "text": "A very long troubleshooting text that should be chunked into smaller pieces for retrieval and metadata tracking."}]
    chunks = chunk_documents(documents, chunk_size=80, overlap=20)
    assert chunks
    assert chunks[0]["source"] == "manual.txt"
    assert chunks[0]["page"] == 2
    assert chunks[0]["section"] == "FAQ"


def test_text_chunks_do_not_split_words_at_character_boundaries():
    from src.chunking import chunk_text

    text = "alpha " * 40 + "uninterruptedword " + "omega " * 40
    chunks = chunk_text(text, chunk_size=80, overlap=20)

    assert len(chunks) > 1
    source_words = set(text.split())
    assert all(word in source_words for chunk in chunks for word in chunk.split())
    assert any("uninterruptedword" in chunk for chunk in chunks)


def test_chunk_text_rejects_invalid_size_and_overlap():
    import pytest
    from src.chunking import chunk_text

    with pytest.raises(ValueError):
        chunk_text("some content", chunk_size=0)
    with pytest.raises(ValueError):
        chunk_text("some content", chunk_size=10, overlap=10)


def test_unsupported_document_formats_are_handled_correctly(tmp_path):
    file_path = tmp_path / "notes.csv"
    file_path.write_text("a,b\n1,2\n", encoding="utf-8")
    assert extract_text_from_file(file_path) == []


def test_markdown_cloudcart_document_ids_are_included_in_section_citations(tmp_path):
    file_path = tmp_path / "guide.md"
    file_path.write_text(
        "# CloudCart Guide\n\n"
        "**Document ID:** CC-DOC-04 · **Version:** 1.0\n\n"
        "## 5.2 Duplicate payments\n\n"
        "Check whether both payments were captured before issuing a refund.\n",
        encoding="utf-8",
    )

    documents = extract_text_from_file(file_path)

    duplicate_payment_section = next(item for item in documents if "both payments" in item["text"])
    assert duplicate_payment_section["section"] == "CC-DOC-04 §5.2"


def test_markdown_tables_remain_separate_passages_and_long_blocks_keep_whole_words(tmp_path):
    file_path = tmp_path / "guide.md"
    repeated = "checkout-payment-process " * 100
    file_path.write_text(
        "# Checkout\n\n"
        f"{repeated}\n\n"
        "| Priority | Meaning |\n"
        "|---|---|\n"
        "| Critical | Checkout unavailable for all shoppers |\n",
        encoding="utf-8",
    )

    documents = extract_text_from_file(file_path)

    assert any("| Critical | Checkout unavailable for all shoppers |" == item["text"] for item in documents)
    source_words = set(repeated.split())
    assert all(
        set(item["text"].split()) <= source_words
        for item in documents
        if "checkout-payment-process" in item["text"]
    )
