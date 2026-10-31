from __future__ import annotations

import streamlit as st

from config import DOCS_DIR
from src.pipeline import analyze_ticket, build_document_index, validate_ticket

st.set_page_config(page_title="AI Customer Support Assistant", layout="wide")
st.title("AI Customer Support Assistant")

with st.sidebar:
    st.write("Customer support assistant")
    st.write("This tool predicts ticket priority and escalation risk and checks documentation for grounded support guidance.")
    st.caption("Add product PDF, TXT, or Markdown files to docs/ and rebuild the index after document changes.")
    if st.button("Rebuild documentation index", use_container_width=True):
        with st.spinner("Extracting documents and building the search index..."):
            index_result = build_document_index(DOCS_DIR)
        if index_result["available"]:
            st.success(index_result["message"])
        else:
            st.warning(index_result["message"])

with st.form("ticket_form"):
    subject = st.text_input("Ticket subject")
    description = st.text_area("Ticket description", height=220)
    submitted = st.form_submit_button("Analyse Ticket")

if submitted:
    try:
        warnings = validate_ticket(subject, description)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    if warnings:
        for warning in warnings:
            st.warning(warning)

    try:
        result = analyze_ticket(subject, description, docs_dir=DOCS_DIR)
    except Exception as exc:
        st.error(f"Prediction failed: {exc}")
        st.stop()

    st.subheader("Prediction results")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Priority", result["priority"]["class"], delta=f"Confidence: {result['priority']['confidence']:.3f}" if result["priority"]["confidence"] is not None else "No probability")
    with col2:
        st.metric("Escalation", result["escalation"]["class"], delta=f"Confidence: {result['escalation']['confidence']:.3f}" if result["escalation"]["confidence"] is not None else "No probability")

    st.caption("Predictions are model estimates based on past support data and are not guaranteed outcomes. Always keep a human support agent responsible for the final decision.")

    st.subheader("Documentation-grounded response")
    rag = result.get("rag", {})
    if rag.get("available"):
        response = rag.get("response", {})
        if response.get("mode") == "unsupported":
            st.warning(rag.get("message", "The available documentation does not sufficiently support an answer."))
        else:
            st.success(rag.get("message", "Relevant passages retrieved."))
        st.markdown("**Retrieved evidence**")
        if rag.get("passages"):
            for citation_number, passage in enumerate(rag.get("passages", [])[:5], start=1):
                st.markdown(
                    f"**[{citation_number}] {passage.get('source', 'unknown')}** | "
                    f"Page {passage.get('page', 'n/a')} | Section: {passage.get('section') or 'n/a'} | "
                    f"Similarity: {passage.get('score', 0.0):.3f}"
                )
                st.write(passage.get("text", ""))
        else:
            st.caption("No passage met the retrieval threshold.")
        if isinstance(response, dict):
            st.markdown("**Suggested response**")
            st.write(response.get("response", "No response could be generated."))
            st.caption(f"Mode: {response.get('mode', 'unknown')}")
            if response.get("supporting_sources"):
                st.markdown("**Citations**")
                for citation_number, citation in enumerate(response["supporting_sources"], start=1):
                    location = []
                    if citation.get("page") not in (None, "n/a"):
                        location.append(f"page {citation['page']}")
                    if citation.get("section"):
                        location.append(f"section {citation['section']}")
                    if citation.get("chunk_id"):
                        location.append(f"passage {citation['chunk_id']}")
                    st.caption(f"[{citation_number}] {citation.get('source', 'unknown')}" + (f", {', '.join(location)}" if location else ""))
        else:
            st.write(response or "The available documentation does not sufficiently support an answer.")
    else:
        st.info(rag.get("message", "Documentation retrieval is unavailable. No product answer was inferred."))

    st.subheader("Final review")
    st.warning("AI-generated predictions and responses are decision-support suggestions. A human support agent must verify the evidence and make the final decision.")
    st.write(result.get("summary", "Analysis complete."))
