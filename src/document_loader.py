from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader

from config import DOCS_DIR

logger = logging.getLogger(__name__)


def iter_supported_documents(docs_dir: str | Path = DOCS_DIR):
    folder = Path(docs_dir)
    if not folder.exists():
        return []
    supported = {".pdf", ".txt", ".md", ".markdown"}
    return sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in supported])


def extract_pdf_text(file_path: Path):
    reader = PdfReader(str(file_path))
    pages = []
    for page_index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append({"page": page_index, "text": text})
    return pages


def extract_text_from_file(file_path: Path):
    file_type = file_path.suffix.lower()
    if file_type == ".pdf":
        pages = extract_pdf_text(file_path)
        text = "\n\n".join(page["text"] for page in pages if page["text"].strip())
        if not text.strip():
            return []
        return [{"source": file_path.name, "file_type": "pdf", "page": page["page"], "text": page["text"], "section": None} for page in pages if page["text"].strip()]

    if file_type in {".txt", ".md", ".markdown"}:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        blocks = []
        document_id_match = re.search(r"Document ID:\**\s*([A-Z0-9-]+)", content)
        document_id = document_id_match.group(1) if document_id_match else None
        section = document_id
        buffer = []

        def flush_buffer():
            nonlocal buffer
            while buffer:
                paragraph = " ".join(buffer).strip()
                buffer = []
                start = 0
                while start < len(paragraph):
                    hard_end = min(start + 1900, len(paragraph))
                    end = hard_end
                    if hard_end < len(paragraph):
                        boundary = paragraph.rfind(" ", start + 950, hard_end)
                        if boundary > start:
                            end = boundary
                    text = paragraph[start:end].strip()
                    if text:
                        blocks.append({
                            "source": file_path.name,
                            "file_type": file_type.lstrip("."),
                            "page": 1,
                            "text": text,
                            "section": section,
                        })
                    start = end
                    while start < len(paragraph) and paragraph[start].isspace():
                        start += 1

        for line in content.splitlines():
            stripped = line.strip()
            if file_type in {".md", ".markdown"} and stripped.startswith("#"):
                flush_buffer()
                heading = stripped.lstrip("#").strip() or None
                if document_id and heading:
                    section_number = re.match(r"(\d+(?:\.\d+)*)\b", heading)
                    section = f"{document_id} §{section_number.group(1)}" if section_number else f"{document_id} · {heading}"
                else:
                    section = heading or document_id
            elif file_type in {".md", ".markdown"} and stripped.startswith("|"):
                flush_buffer()
                blocks.append({
                    "source": file_path.name,
                    "file_type": file_type.lstrip("."),
                    "page": 1,
                    "text": stripped,
                    "section": section,
                })
            elif not stripped:
                flush_buffer()
            else:
                buffer.append(stripped)
        flush_buffer()
        return blocks

    logger.warning("Unsupported file format encountered: %s", file_path)
    return []


def load_documents(docs_dir: str | Path = DOCS_DIR):
    folder = Path(docs_dir)
    if not folder.exists():
        return []
    documents = []
    for file_path in iter_supported_documents(folder):
        try:
            entries = extract_text_from_file(file_path)
            documents.extend(entries)
        except Exception as exc:  # pragma: no cover - defensive logging path
            logger.warning("Skipping unreadable document %s: %s", file_path.name, exc)
    return documents
