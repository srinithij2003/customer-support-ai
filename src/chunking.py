from __future__ import annotations

from typing import Iterable

from config import CHUNK_OVERLAP, CHUNK_SIZE


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    if not text or not text.strip():
        return []
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size.")
    text = text.strip()
    chunks = []
    start = 0
    while start < len(text):
        hard_end = min(start + chunk_size, len(text))
        end = hard_end
        if hard_end < len(text):
            boundary = text.rfind(" ", start + chunk_size // 2, hard_end)
            if boundary > start:
                end = boundary
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        if end == len(text):
            break
        next_start = max(start + 1, end - overlap)
        if next_start < len(text) and not text[next_start - 1].isspace():
            next_boundary = text.find(" ", next_start, end + 1)
            if next_boundary >= 0:
                next_start = next_boundary + 1
        start = next_start
    return [c.strip() for c in chunks if c.strip()]


def chunk_documents(documents, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    chunks = []
    for index, doc in enumerate(documents):
        text = doc.get("text", "")
        chunk_list = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        for chunk_index, chunk in enumerate(chunk_list, start=1):
            chunks.append({
                "chunk_id": f"{doc.get('source', 'document')}_{index}_{chunk_index}",
                "source": doc.get("source", "unknown"),
                "file_type": doc.get("file_type", "unknown"),
                "page": doc.get("page", 1),
                "section": doc.get("section"),
                "text": chunk,
            })
    return chunks
