from __future__ import annotations

import re

_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "can", "do", "does", "for", "from",
    "how", "i", "in", "is", "it", "me", "my", "of", "on", "or", "our", "please",
    "should", "the", "to", "we", "what", "when", "where", "which", "with", "you", "your",
}


def _content_terms(text: str):
    return {
        token
        for token in re.findall(r"[a-z0-9]+", (text or "").casefold())
        if len(token) > 2 and token not in _STOP_WORDS
    }


def _passage_supports_query(query: str, passage) -> bool:
    query_terms = _content_terms(query)
    if len(query_terms) < 2:
        return False
    evidence_terms = _content_terms(passage.get("text", ""))
    matched_terms = query_terms & evidence_terms
    return len(matched_terms) >= 2 and len(matched_terms) / len(query_terms) >= 0.2


def _relevant_excerpt(query: str, text: str) -> str:
    query_terms = _content_terms(query)
    pieces = re.split(r"(?<=[.!?])\s+|\n+", (text or "").strip())
    ranked = []
    for position, piece in enumerate(pieces):
        candidate = piece.strip(" -*\t")
        terms = _content_terms(candidate)
        overlap = query_terms & terms
        if len(overlap) >= 2 and len(overlap) / max(1, len(query_terms)) >= 0.2:
            ranked.append((len(overlap), -position, candidate))
    if not ranked:
        return (text or "").strip()[:360]
    ranked.sort(reverse=True)
    excerpts = []
    seen = set()
    for _, _, candidate in ranked:
        key = candidate.casefold()
        if key in seen:
            continue
        seen.add(key)
        excerpts.append(candidate)
        if len(excerpts) == 2:
            break
    return " ".join(excerpts)[:500]


def extractive_fallback(passages, query: str = ""):
    if not passages:
        return {
            "response": "No supporting documentation was found for this ticket. Please add product documentation and rebuild the index.",
            "supporting_sources": [],
            "evidence_used": [],
            "mode": "unsupported",
        }
    evidence = []
    for passage in passages:
        if not passage.get("text", "").strip() or not passage.get("source"):
            continue
        excerpt = _relevant_excerpt(query, passage.get("text", "")) if query else passage["text"].strip()
        if not excerpt:
            continue
        evidence.append({
            "source": passage.get("source", "unknown"),
            "page": passage.get("page", "n/a"),
            "section": passage.get("section"),
            "text": excerpt,
            "score": passage.get("score"),
            "chunk_id": passage.get("chunk_id"),
        })
    if not evidence:
        return {
            "response": "The available documentation does not contain sufficient supporting information for this question. No product instructions were inferred beyond the supplied documentation.",
            "supporting_sources": [],
            "evidence_used": [],
            "mode": "unsupported",
        }
    cited_passages = []
    cited_evidence = []
    remaining = 1200
    for item in evidence[:3]:
        citation_number = len(cited_evidence) + 1
        citation_marker = f" [{citation_number}]"
        separator = " " if cited_passages else ""
        available_text = remaining - len(separator) - len(citation_marker)
        if available_text <= 0:
            break
        excerpt = item["text"][:available_text].rstrip()
        if not excerpt:
            continue
        cited_passages.append(f"{excerpt}{citation_marker}")
        cited_evidence.append(item)
        remaining -= len(separator) + len(excerpt) + len(citation_marker)
    summary = " ".join(cited_passages)
    return {
        "response": summary[:1200],
        "supporting_sources": cited_evidence,
        "evidence_used": cited_evidence,
        "mode": "extractive",
    }


def build_grounded_response(query: str, passages):
    supported_passages = [passage for passage in passages if _passage_supports_query(query, passage)]
    if not supported_passages:
        return {
            "response": "The available documentation does not contain sufficient supporting information for this question. No product instructions were inferred beyond the supplied documentation.",
            "supporting_sources": [],
            "evidence_used": [],
            "mode": "unsupported",
        }
    return extractive_fallback(supported_passages, query=query)
