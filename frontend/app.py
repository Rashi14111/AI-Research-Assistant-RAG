"""
app.py
------
Main entry point for the AI Research Assistant frontend.

Run with:
    streamlit run frontend/app.py

This module owns all state management and API orchestration. It is
intentionally the only place that mixes `api.py` calls with
`components.py` rendering - both of those modules stay decoupled from
each other so each can be tested/reasoned about independently.
"""
import uuid
from typing import Any, Dict, List, Optional

import streamlit as st

import api
import components
from styles import inject_custom_css

# ---------------------------------------------------------------------------
# Page configuration - must be the very first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()


# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
def init_session_state() -> None:
    """
    Sets up all session_state keys used across the app.

    The session_id is persisted in the URL's query params so that a
    browser refresh keeps the same conversation session instead of
    silently starting a new one.
    """
    if "session_id" not in st.session_state:
        existing_sid = st.query_params.get("sid")
        if existing_sid:
            st.session_state.session_id = existing_sid
        else:
            new_sid = str(uuid.uuid4())
            st.session_state.session_id = new_sid
            st.query_params["sid"] = new_sid

    st.session_state.setdefault("messages", [])  # [{"role", "content", "sources"}]
    st.session_state.setdefault("documents", [])
    st.session_state.setdefault("suggested_questions", [])
    st.session_state.setdefault("export_data", None)
    st.session_state.setdefault("documents_loaded", False)


# ---------------------------------------------------------------------------
# Data refresh helpers
# ---------------------------------------------------------------------------
def refresh_documents(show_error: bool = True) -> None:
    """Fetches the latest document list from the backend into session_state."""
    result = api.list_documents()
    if result["ok"]:
        st.session_state.documents = result["data"].get("documents", [])
    elif show_error:
        st.toast(f"❌ Could not load documents: {result['error']}", icon="❌")


@st.cache_data(ttl=5, show_spinner=False)
def _cached_health_check() -> Dict[str, Any]:
    """Caches the health check briefly so every rerun doesn't hammer the backend."""
    return api.check_health()


def format_transcript(export_payload: Dict[str, Any]) -> str:
    """Formats the /export payload into a clean, human-readable .txt transcript."""
    lines: List[str] = ["AI Research Assistant - Conversation Export", "=" * 50, ""]
    for turn in export_payload.get("history", []):
        speaker = "You" if turn.get("role") == "user" else "Assistant"
        lines.append(f"{speaker}: {turn.get('content', '')}")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core chat handling
# ---------------------------------------------------------------------------
def handle_new_question(question: str) -> None:
    """
    Processes a new user question end-to-end:
    renders it immediately, calls the backend, animates the reply,
    persists both turns to session_state, then reruns for a clean state.
    """
    question = question.strip()
    if not question:
        return

    # Show the user's message right away for instant feedback
    components.render_chat_message("user", question)
    st.session_state.messages.append({"role": "user", "content": question, "sources": None})

    with st.spinner("🧠 Thinking through your documents..."):
        result = api.send_chat_message(st.session_state.session_id, question)

    if result["ok"]:
        answer = result["data"].get("answer", "")
        sources = result["data"].get("sources", [])
        components.render_streaming_message(answer, sources)
        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "sources": sources}
        )
    else:
        error_message = f"⚠️ {result['error']}"
        components.render_chat_message("assistant", error_message)
        st.session_state.messages.append(
            {"role": "assistant", "content": error_message, "sources": None}
        )
        st.toast(f"❌ {result['error']}", icon="❌")

    st.rerun()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def render_sidebar() -> None:
    """Renders the entire sidebar: upload, document management, conversation tools."""
    with st.sidebar:
        st.markdown("### 📎 Document Library")

        # --- Upload section --------------------------------------------------
        components.render_sidebar_label("Upload PDFs")
        uploaded_files = st.file_uploader(
            "Drop PDF files here",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        if uploaded_files:
            if st.button("📤 Upload & Process", type="primary", use_container_width=True):
                files_payload = [(f.name, f.getvalue()) for f in uploaded_files]

                with st.status("Processing documents...", expanded=True) as status:
                    st.write("⬆️ Uploading files to the server")
                    progress_bar = st.progress(10)

                    st.write("✂️ Splitting into chunks & embedding")
                    progress_bar.progress(45)

                    result = api.upload_pdfs(files_payload)
                    progress_bar.progress(85)

                    if result["ok"]:
                        data = result["data"]
                        uploaded = data.get("uploaded", [])
                        errors = data.get("errors", [])
                        st.session_state.suggested_questions = data.get(
                            "suggested_questions", []
                        )

                        progress_bar.progress(100)
                        st.write("💾 Stored in ChromaDB")

                        if uploaded:
                            status.update(
                                label=f"✅ Processed {len(uploaded)} document(s)",
                                state="complete",
                            )
                            st.toast(
                                f"✅ {len(uploaded)} document(s) indexed successfully",
                                icon="✅",
                            )
                        if errors:
                            status.update(
                                label=f"⚠️ Completed with {len(errors)} error(s)",
                                state="error" if not uploaded else "complete",
                            )
                            for err in errors:
                                st.toast(
                                    f"⚠️ {err.get('filename', 'file')}: {err.get('error', '')}",
                                    icon="⚠️",
                                )

                        refresh_documents(show_error=False)
                        st.rerun()
                    else:
                        status.update(label="❌ Upload failed", state="error")
                        st.toast(f"❌ {result['error']}", icon="❌")

        # --- Document list -----------------------------------------------------
        components.render_sidebar_label("Your documents")
        if st.session_state.documents:
            for doc in st.session_state.documents:
                if components.render_document_card(doc):
                    delete_result = api.delete_document(doc["doc_id"])
                    if delete_result["ok"]:
                        st.toast(f"🗑️ Removed {doc['filename']}", icon="🗑️")
                        refresh_documents(show_error=False)
                        st.rerun()
                    else:
                        st.toast(f"❌ {delete_result['error']}", icon="❌")
        else:
            st.caption("No documents uploaded yet.")

        # --- Session metrics -----------------------------------------------------
        components.render_sidebar_label("Session overview")
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric("Documents", len(st.session_state.documents))
        with metric_col2:
            user_turns = sum(1 for m in st.session_state.messages if m["role"] == "user")
            st.metric("Messages", user_turns)

        # --- Conversation tools -----------------------------------------------
        components.render_sidebar_label("Conversation")

        if st.button("📥 Export Conversation", use_container_width=True):
            export_result = api.export_history(st.session_state.session_id)
            if export_result["ok"]:
                st.session_state.export_data = export_result["data"]
                st.toast("Export ready — download below", icon="📥")
            else:
                st.toast(f"❌ {export_result['error']}", icon="❌")

        if st.session_state.export_data:
            st.download_button(
                "⬇️ Download transcript (.txt)",
                data=format_transcript(st.session_state.export_data),
                file_name=f"chat_export_{st.session_state.session_id[:8]}.txt",
                mime="text/plain",
                use_container_width=True,
            )

        if st.button("🧹 Clear Conversation", use_container_width=True):
            clear_result = api.clear_history(st.session_state.session_id)
            if clear_result["ok"]:
                st.session_state.messages = []
                st.session_state.export_data = None
                st.toast("Conversation cleared", icon="🧹")
                st.rerun()
            else:
                st.toast(f"❌ {clear_result['error']}", icon="❌")


# ---------------------------------------------------------------------------
# Main content area
# ---------------------------------------------------------------------------
def render_main_content(backend_online: bool) -> None:
    """Renders the header, hero/chat area, and footer."""
    components.render_header(backend_online)

    has_documents = len(st.session_state.documents) > 0
    has_messages = len(st.session_state.messages) > 0

    if not has_documents:
        # Landing / empty-state screen before any document has been uploaded
        components.render_hero()
        render_footer_section()
        return

    # Render existing conversation history (static, already-typed messages)
    for message in st.session_state.messages:
        components.render_chat_message(
            message["role"], message["content"], message.get("sources")
        )

    clicked_suggestion: Optional[str] = None
    if not has_messages:
        if st.session_state.suggested_questions:
            clicked_suggestion = components.render_suggested_questions(
                st.session_state.suggested_questions
            )
        else:
            components.render_empty_chat_state()

    # Chat input is always available once at least one document is indexed
    prompt = st.chat_input("Ask a question about your documents...")

    if clicked_suggestion:
        handle_new_question(clicked_suggestion)
    elif prompt:
        handle_new_question(prompt)

    render_footer_section()


def render_footer_section() -> None:
    """Renders the footer with technology badges at the bottom of the page."""
    components.render_footer()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    """Application entry point - wires together state, data, and layout."""
    init_session_state()

    # Load the document list once per browser session on first run
    if not st.session_state.documents_loaded:
        refresh_documents(show_error=False)
        st.session_state.documents_loaded = True

    health_result = _cached_health_check()
    backend_online = health_result.get("ok", False)

    if not backend_online:
        st.error(
            f"⚠️ Cannot reach the backend at **{api.BASE_URL}**. "
            "Start the FastAPI server, then refresh this page.",
            icon="🔌",
        )

    render_sidebar()
    render_main_content(backend_online)


if __name__ == "__main__":
    main()
