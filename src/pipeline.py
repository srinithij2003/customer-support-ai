from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

import pandas as pd

from config import DOCS_DIR, DOCS_INDEX_PATH, DOCS_METADATA_PATH, ESCALATION_MODEL_PATH, PRIORITY_MODEL_PATH
from src.chunking import chunk_documents
from src.document_loader import iter_supported_documents, load_documents
from src.embeddings import build_faiss_index, load_faiss_index
from src.predict import load_model, predict_ticket_escalation, predict_ticket_priority
from src.response_generator import build_grounded_response
from src.retrieval import search_documents

logger = logging.getLogger(__name__)


def validate_ticket(subject: str, description: str):
    combined = (subject or "") + " " + (description or "")
    if not combined.strip():
        raise ValueError("Ticket subject and description cannot both be empty. Please enter a problem description first.")
    warnings = []
    if len(combined.strip()) < 12:
        warnings.append("The ticket is very brief. Predictions may be unreliable because the issue description lacks detail.")
    return warnings


@lru_cache(maxsize=1)
def load_models():
    return {
        "priority": load_model(PRIORITY_MODEL_PATH),
        "escalation": load_model(ESCALATION_MODEL_PATH),
    }


def _remove_index_files(index_path, metadata_path):
    for path in (index_path, metadata_path):
        try:
            Path(path).unlink(missing_ok=True)
        except OSError as exc:  # pragma: no cover - depends on filesystem permissions
            logger.warning("Could not remove stale document index file %s: %s", path, exc)


def build_document_index(
    docs_dir: str | Path = DOCS_DIR,
    chunk_size: int = 700,
    overlap: int = 100,
    index_path: str | Path = DOCS_INDEX_PATH,
    metadata_path: str | Path = DOCS_METADATA_PATH,
):
    supported_files = iter_supported_documents(docs_dir)
    documents = load_documents(docs_dir)
    if not documents:
        _remove_index_files(index_path, metadata_path)
        if supported_files:
            message = "Supported document files were found, but no readable text could be extracted. Check that the files are valid and contain selectable text."
        else:
            message = "No supported product documents were found. Add PDF, TXT, or Markdown files to the docs directory."
        return {"available": False, "message": message, "passages": [], "documents": 0, "chunks": 0}
    chunks = chunk_documents(documents, chunk_size=chunk_size, overlap=overlap)
    if not chunks:
        _remove_index_files(index_path, metadata_path)
        return {"available": False, "message": "No usable document chunks were generated from the supplied files.", "passages": [], "documents": len(documents), "chunks": 0}
    try:
        index, metadata = build_faiss_index(chunks, index_path=index_path, metadata_path=metadata_path)
    except Exception as exc:  # pragma: no cover - embedding/model/runtime failures
        logger.warning("Documentation indexing failed: %s", exc)
        _remove_index_files(index_path, metadata_path)
        return {
            "available": False,
            "message": "Documentation text was extracted, but embedding or index creation failed. Check the embedding model and retry.",
            "passages": [],
            "documents": len(documents),
            "chunks": len(chunks),
        }
    if index is None or not metadata:
        _remove_index_files(index_path, metadata_path)
        return {"available": False, "message": "The documentation index could not be built from the extracted content.", "passages": [], "documents": len(documents), "chunks": len(chunks)}
    sources = sorted({chunk.get("source", "unknown") for chunk in metadata})
    return {
        "available": True,
        "message": f"Indexed {len(documents)} document sections into {len(metadata)} searchable passages.",
        "passages": metadata[:3],
        "documents": len(sources),
        "chunks": len(metadata),
    }


def analyze_ticket(
    subject: str,
    description: str,
    docs_dir: str | Path = DOCS_DIR,
    index_path: str | Path = DOCS_INDEX_PATH,
    metadata_path: str | Path = DOCS_METADATA_PATH,
):
    warnings = validate_ticket(subject, description)
    models = load_models()
    priority_prediction = predict_ticket_priority(subject, description, model=models["priority"])
    escalation_prediction = predict_ticket_escalation(subject, description, model=models["escalation"])

    query = (subject + " " + description).strip()
    supported_files = iter_supported_documents(docs_dir)
    documents = load_documents(docs_dir)
    rag = {
        "available": False,
        "message": "No supported product documentation is available. Predictions are available; add PDF, TXT, or Markdown files and rebuild the index for grounded responses.",
        "passages": [],
        "response": build_grounded_response(query, []),
        "supporting_sources": [],
    }
    if supported_files and not documents:
        rag["message"] = "Supported files exist, but no readable text was extracted. Correct or replace the files, then rebuild the index."
    elif documents:
        try:
            index, metadata = load_faiss_index(index_path, metadata_path)
            current_sources = {document.get("source") for document in documents}
            indexed_sources = {item.get("source") for item in metadata}
            if index is None or not metadata:
                rag["message"] = "Product documentation is present but has not been indexed. Rebuild the documentation index before asking questions."
            elif not indexed_sources or indexed_sources != current_sources:
                rag["message"] = "The documentation index does not match the files currently in docs. Rebuild the index before asking questions."
            else:
                passages = search_documents(
                    query,
                    top_k=5,
                    threshold=0.25,
                    index_path=index_path,
                    metadata_path=metadata_path,
                )
                response = build_grounded_response(query, passages)
                rag.update({
                    "available": True,
                    "message": "Relevant passages retrieved." if passages else "No passages met the retrieval threshold.",
                    "passages": passages,
                    "response": response,
                    "supporting_sources": response.get("supporting_sources", []),
                })
                if response.get("mode") == "unsupported":
                    rag["message"] = "The available documentation does not sufficiently support an answer to this ticket."
        except Exception as exc:  # pragma: no cover - defensive path
            logger.warning("Embedding retrieval failed: %s", exc)
            rag["message"] = "Documentation retrieval is unavailable right now. No answer was inferred."

    summary = (
        f"Priority: {priority_prediction['class']} | Escalation: {escalation_prediction['class']} | "
        f"Evidence available: {'yes' if rag.get('available') else 'no'}"
    )
    return {
        "priority": priority_prediction,
        "escalation": escalation_prediction,
        "rag": rag,
        "summary": summary,
        "warnings": warnings,
    }
