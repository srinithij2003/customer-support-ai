from __future__ import annotations

import logging
from pathlib import Path

import faiss
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer

from config import DOCS_INDEX_PATH, DOCS_METADATA_PATH, EMBEDDING_MODEL, VECTOR_STORE_DIR

logger = logging.getLogger(__name__)


class EmbeddingProvider:
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model_name = model_name
        self.model = None

    def get_model(self):
        if self.model is None:
            try:
                self.model = SentenceTransformer(self.model_name)
            except Exception as exc:  # pragma: no cover - network/error path
                raise RuntimeError(
                    f"Could not load the embedding model '{self.model_name}'. "
                    "Check the internet connection or install the model locally."
                ) from exc
        return self.model

    def encode(self, texts):
        if not texts:
            return np.empty((0, 0), dtype="float32")
        encoder = self.get_model()
        embeddings = encoder.encode(list(texts), normalize_embeddings=True, show_progress_bar=False, convert_to_numpy=True)
        return np.asarray(embeddings, dtype="float32")


def build_faiss_index(
    chunks,
    embedding_model_name: str = EMBEDDING_MODEL,
    index_path: str | Path | None = None,
    metadata_path: str | Path | None = None,
):
    if not chunks:
        return None, []
    provider = EmbeddingProvider(model_name=embedding_model_name)
    texts = [chunk["text"] for chunk in chunks]
    embeddings = provider.encode(texts)
    if embeddings.size == 0:
        return None, []
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    resolved_index_path = Path(index_path) if index_path is not None else DOCS_INDEX_PATH
    resolved_metadata_path = Path(metadata_path) if metadata_path is not None else DOCS_METADATA_PATH
    resolved_index_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_metadata_path.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(resolved_index_path))
    joblib.dump(chunks, resolved_metadata_path)
    return index, chunks


def load_faiss_index(index_path: str | Path = DOCS_INDEX_PATH, metadata_path: str | Path = DOCS_METADATA_PATH):
    index_file = Path(index_path)
    metadata_file = Path(metadata_path)
    if not index_file.exists() or not metadata_file.exists():
        return None, []
    try:
        index = faiss.read_index(str(index_file))
        metadata = joblib.load(metadata_file)
        return index, metadata
    except Exception as exc:  # pragma: no cover - corrupted index path
        logger.warning("Failed to load index or metadata: %s", exc)
        return None, []
