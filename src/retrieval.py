from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

from config import DOCS_INDEX_PATH, DOCS_METADATA_PATH, EMBEDDING_MODEL, FAISS_TOP_K, SIMILARITY_THRESHOLD
from src.embeddings import EmbeddingProvider, load_faiss_index

logger = logging.getLogger(__name__)


def search_documents(
    query: str,
    top_k: int = FAISS_TOP_K,
    threshold: float = SIMILARITY_THRESHOLD,
    index_path=None,
    metadata_path=None,
):
    if not query or not query.strip():
        return []
    index, metadata = load_faiss_index(
        index_path or DOCS_INDEX_PATH,
        metadata_path or DOCS_METADATA_PATH,
    )
    if index is None or len(metadata) == 0:
        return []
    provider = EmbeddingProvider(model_name=EMBEDDING_MODEL)
    query_embedding = provider.encode([query])[0]
    if query_embedding.size == 0:
        return []
    query_embedding = np.asarray(query_embedding, dtype="float32").reshape(1, -1)
    scores, indices = index.search(query_embedding, min(top_k, len(metadata)))
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        candidate = metadata[int(idx)]
        similarity = float(score)
        if similarity < threshold:
            continue
        results.append({
            "text": candidate.get("text", ""),
            "source": candidate.get("source", "unknown"),
            "file_type": candidate.get("file_type", "unknown"),
            "page": candidate.get("page", 1),
            "section": candidate.get("section"),
            "score": similarity,
            "chunk_id": candidate.get("chunk_id"),
        })
    return results
