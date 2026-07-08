"""
components.py
-------------
Reusable, presentation-only UI building blocks for the AI Research
Assistant. Every function here either renders markup/widgets or
returns a simple value describing what the user did (e.g. "delete was
clicked", "this suggested question was clicked"). None of these
functions call the API directly - that orchestration lives in app.py.
"""
import time
from typing import Any, Dict, List, Optional

import streamlit as st


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
def render_header(backend_online: bool) -> None:
    """Renders the sticky-feeling top header with brand and live status pill."""
    status_class = "status-online" if backend_online else "status-offline"
    status_text = "Backend online" if backend_online else "Backend unreachable"

    st.markdown(
        f"""
        <div class="app-header">
            <div class="brand">
                <div class="brand-icon">🧠</div>
                <div class="brand-text">
                    <h1>AI Research Assistant</h1>
                    <span>RAG-powered document intelligence</span>
                </div>
            </div>
            <div class="status-pill">
                <span class="status-dot {status_class}"></span>
                {status_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Landing / hero (shown before any documents are uploaded)
# ---------------------------------------------------------------------------
def render_hero() -> None:
    """Renders the landing hero shown when no documents have been uploaded yet."""
    st.markdown(
        """
        <div class="hero-wrap">
            <div class="hero-badge">✨ Retrieval-Augmented Generation</div>
            <h1>Chat with your research, instantly.</h1>
            <p class="subtitle">
                Upload PDF papers, reports, or notes and ask questions in plain English.
                Every answer is grounded in your documents and backed by verifiable
                source citations.
            </p>
        </div>
        <div class="feature-grid">
            <div class="feature-card">
                <div class="icon">📄</div>
                <h4>Multi-document upload</h4>
                <p>Drop in several PDFs at once and they're chunked, embedded, and
                indexed automatically.</p>
            </div>
            <div class="feature-card">
                <div class="icon">🔍</div>
                <h4>Grounded answers</h4>
                <p>Responses are generated only from your documents, with citations
                you can expand and verify.</p>
            </div>
            <div class="feature-card">
                <div class="icon">💬</div>
                <h4>Conversational memory</h4>
                <p>Ask follow-up questions naturally - the assistant remembers the
                context of your session.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color:#94A3B8; margin-top:1.5rem;'>"
        "👈 Upload a PDF from the sidebar to get started"
        "</p>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Document cards (sidebar)
# ---------------------------------------------------------------------------
def render_document_card(doc: Dict[str, Any]) -> bool:
    """
    Renders a single uploaded-document card with a delete button.
    Returns True if the user clicked delete on this card.
    """
    filename = doc.get("filename", "Unknown file")
    chunk_count = doc.get("chunk_count", 0)
    doc_id = doc.get("doc_id", "")

    with st.container():
        st.markdown(
            f"""
            <div class="app-card">
                <p class="doc-card-title">📄 {filename}</p>
                <p class="doc-card-meta">{chunk_count} chunks indexed</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        delete_clicked = st.button(
            "🗑️ Remove", key=f"delete_{doc_id}", use_container_width=True
        )
    return delete_clicked


# ---------------------------------------------------------------------------
# Suggested questions
# ---------------------------------------------------------------------------
def render_suggested_questions(questions: List[str]) -> Optional[str]:
    """
    Renders suggested starter questions as clickable chips.
    Returns the text of the question clicked, or None.
    """
    if not questions:
        return None

    st.markdown("**✨ Suggested questions**")
    clicked_question: Optional[str] = None

    cols = st.columns(2)
    for idx, question in enumerate(questions):
        col = cols[idx % 2]
        with col:
            if st.button(question, key=f"suggested_{idx}", use_container_width=True):
                clicked_question = question

    return clicked_question


# ---------------------------------------------------------------------------
# Chat messages
# ---------------------------------------------------------------------------
def render_sources(sources: List[Dict[str, Any]]) -> None:
    """Renders source citations inside an expandable card list."""
    if not sources:
        return

    with st.expander(f"📚 Sources ({len(sources)})"):
        for source in sources:
            filename = source.get("filename", "unknown")
            page = source.get("page", "N/A")
            snippet = source.get("snippet", "")
            st.markdown(
                f"""
                <div class="source-card">
                    <div class="source-meta">📄 {filename} · Page {page}</div>
                    <div class="source-snippet">{snippet}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_chat_message(
    role: str, content: str, sources: Optional[List[Dict[str, Any]]] = None
) -> None:
    """Renders a single, already-complete chat message (no animation)."""
    avatar = "🧑‍💻" if role == "user" else "🧠"
    with st.chat_message(role, avatar=avatar):
        st.markdown(content)
        if role == "assistant" and sources:
            render_sources(sources)


def render_streaming_message(content: str, sources: Optional[List[Dict[str, Any]]] = None) -> None:
    """
    Renders an assistant message with a simulated typing animation.
    The backend returns the full answer in one response, so we simulate
    a streaming feel by progressively revealing the text client-side.
    """
    with st.chat_message("assistant", avatar="🧠"):
        placeholder = st.empty()
        displayed = ""
        # Reveal a few characters at a time for a smooth, fast typing effect
        step = max(1, len(content) // 120)
        for i in range(0, len(content), step):
            displayed = content[: i + step]
            placeholder.markdown(displayed + "▌")
            time.sleep(0.012)
        placeholder.markdown(content)
        if sources:
            render_sources(sources)


# ---------------------------------------------------------------------------
# Empty states
# ---------------------------------------------------------------------------
def render_empty_chat_state() -> None:
    """Shown when documents exist but no conversation has started yet."""
    st.markdown(
        """
        <div class="empty-chat">
            <div class="icon">💬</div>
            <p>Your documents are ready. Ask a question below to start the conversation.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sidebar section label helper
# ---------------------------------------------------------------------------
def render_sidebar_label(text: str) -> None:
    """Renders a small uppercase section label used to group sidebar controls."""
    st.markdown(f'<p class="sidebar-label">{text}</p>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
def render_footer() -> None:
    """Renders the footer with technology badges."""
    badges = ["FastAPI", "LangChain", "ChromaDB", "Google Gemini 2.5 Flash", "Streamlit"]
    badge_html = "".join(f'<span class="tech-badge">{b}</span>' for b in badges)
    st.markdown(
        f"""
        <div class="app-footer">
            <p class="caption">Built as a Retrieval-Augmented Generation prototype</p>
            <div class="tech-badge-row">{badge_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
