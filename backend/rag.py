"""
RAG (Retrieval-Augmented Generation) module.

This is the "brain" of the app. It handles:
1. PDF ingestion - loading a PDF and splitting it into chunks.
2. Building a history-aware conversational retrieval chain.
3. Answering questions with grounded, cited responses.
4. Generating suggested starter questions after upload.
5. A lightweight in-memory conversation store (per session_id).
"""
import uuid
from typing import Any, Dict, List, Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever

from backend.config import settings
from backend.retriever import vector_store_manager


# ---------------------------------------------------------------------------
# Conversation history store
# ---------------------------------------------------------------------------
class SessionStore:
    """
    Keeps per-session chat history in memory, keyed by session_id.

    NOTE: This is intentionally simple (a Python dict) for a one-day
    prototype. In a real production system this would be backed by
    Redis or a database so history survives server restarts and scales
    across multiple app instances.
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, List[Dict[str, str]]] = {}

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Returns the raw (role, content) history list for a session."""
        return self._sessions.setdefault(session_id, [])

    def append(self, session_id: str, role: str, content: str) -> None:
        """Appends a single turn to a session's history."""
        self._sessions.setdefault(session_id, []).append({"role": role, "content": content})

    def clear(self, session_id: str) -> None:
        """Wipes history for a given session."""
        self._sessions[session_id] = []

    def as_lc_messages(self, session_id: str) -> List[Any]:
        """Converts stored history into LangChain message objects for the chain."""
        messages: List[Any] = []
        for turn in self.get_history(session_id):
            if turn["role"] == "user":
                messages.append(HumanMessage(content=turn["content"]))
            else:
                messages.append(AIMessage(content=turn["content"]))
        return messages


# Single shared session store used across the app
session_store = SessionStore()


def _get_llm() -> ChatGoogleGenerativeAI:
    """Instantiates the Gemini chat model using configured settings."""
    try:
        return ChatGoogleGenerativeAI(
            model=settings.llm_model_name,
            google_api_key=settings.google_api_key,
            temperature=settings.llm_temperature,
        )
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Failed to initialize Gemini LLM: {exc}") from exc


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------
def process_pdf(file_path: str, original_filename: str) -> Dict[str, Any]:
    """
    Loads a PDF from disk, splits it into overlapping chunks, and stores
    those chunks (as embeddings) in ChromaDB.

    Returns metadata describing the ingested document (doc_id, page/chunk counts)
    so the caller (app.py) can report it back to the frontend.
    """
    doc_id = uuid.uuid4().hex

    try:
        loader = PyPDFLoader(file_path)
        pages: List[Document] = loader.load()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Failed to load PDF '{original_filename}': {exc}") from exc

    if not pages:
        raise ValueError(f"No readable text found in '{original_filename}'.")

    # RecursiveCharacterTextSplitter tries larger separators first (paragraphs,
    # then lines, then sentences) so chunks stay semantically coherent.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(pages)

    chunk_count = vector_store_manager.add_documents(chunks, doc_id=doc_id, filename=original_filename)

    return {
        "doc_id": doc_id,
        "filename": original_filename,
        "page_count": len(pages),
        "chunk_count": chunk_count,
    }


# ---------------------------------------------------------------------------
# Conversational RAG chain
# ---------------------------------------------------------------------------
def _build_qa_prompt() -> ChatPromptTemplate:
    """Builds the prompt used to answer questions using retrieved document context."""

    system_prompt = (
        "You are a senior AI Research Assistant that answers questions about "
        "the user's uploaded documents.\n\n"

        "GROUNDING RULES:\n"
        "- Use ONLY the retrieved context provided below.\n"
        "- Never use outside knowledge, assumptions, or hallucinations.\n"
        "- If the answer is not present in the retrieved context, reply exactly:\n"
        "\"I couldn't find that information in the uploaded documents.\"\n"
        "- If the context only partially answers the question, answer only the "
        "supported portion and clearly state what information is missing.\n"
        "- Synthesize the information instead of copying long passages from the document.\n\n"

        "RESPONSE FORMAT:\n"
        "- Simple factual questions → Answer directly in 1-2 concise sentences.\n"
        "- Summary or overview requests → Return ONLY 4-6 concise bullet points.\n"
        "- Do NOT create headings such as Executive Summary, Key Findings, "
        "Important Details, or Final Takeaway unless the user explicitly asks "
        "for a detailed report.\n"
        "- Skills, technologies, tools, or features → Return grouped bullet lists.\n"
        "- Experience, projects, achievements, or lists → Return concise bullet lists.\n"
        "- Comparison requests → Return a markdown table with clear column headings.\n"
        "- Step-by-step or workflow questions → Return a numbered list.\n\n"

        "STYLE RULES:\n"
        "- Keep answers under 150 words unless the user explicitly asks for more detail.\n"
        "- Be concise, factual, and professional.\n"
        "- Never repeat the same information.\n"
        "- Avoid unnecessary introductions and conclusions.\n"
        "- Prefer bullets over long paragraphs whenever appropriate.\n"
        "- Include only information that directly answers the user's question.\n\n"

        "ENDING:\n"
        "- End every answer with exactly one line:\n"
        "\"Sources Used: based on the retrieved excerpts from your uploaded documents.\"\n"
        "- Do not include filenames, page numbers, or document snippets in this note because the application already displays citations separately.\n\n"

        "Retrieved Context:\n"
        "{context}"
    )

    return ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

def _build_history_aware_retriever(llm: ChatGoogleGenerativeAI):
    """
    Wraps the base retriever so it accounts for chat history.

    Example: if the user first asks "What is the main finding?" and then
    follow-ups with "Why is that significant?", this step rewrites the
    follow-up into a standalone question before running semantic search.
    """
    rewrite_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Given the chat history and the latest user question, rewrite the "
                "latest question into a fully standalone question that can be "
                "understood and searched for without needing the chat history.\n\n"
                "Guidelines:\n"
                "- Resolve pronouns and implicit references (e.g. 'it', 'that', "
                "'this project', 'the second one') using the relevant entities "
                "from the chat history.\n"
                "- Preserve the user's original intent, scope, and level of "
                "detail exactly — do not broaden, narrow, or answer the question.\n"
                "- If the latest question introduces a new topic unrelated to the "
                "prior conversation, return it unchanged.\n"
                "- If the question is already standalone and unambiguous, return "
                "it unchanged.\n"
                "- Keep the rewritten question concise and natural, as if the "
                "user had asked it directly without any prior context.\n"
                "- Do NOT answer the question, add explanations, or include any "
                "text other than the rewritten question itself.",
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    # Reduced from k=4 to k=2 so Gemini receives only the most relevant chunks —
    # this keeps context tighter and responses faster, without touching the
    # underlying vector_store_manager implementation.
    try:
        base_retriever = vector_store_manager.as_retriever(search_kwargs={"k": 2})
    except TypeError:
        # Fallback in case as_retriever() does not accept search_kwargs
        base_retriever = vector_store_manager.as_retriever()
    return create_history_aware_retriever(llm, base_retriever, rewrite_prompt)


def answer_question(session_id: str, question: str) -> Dict[str, Any]:
    """
    Runs the full RAG pipeline for a single user question:

    1. Rewrite the question using chat history (handles follow-ups).
    2. Retrieve the most relevant chunks from ChromaDB.
    3. Generate an answer grounded strictly in those chunks.
    4. Return the answer plus structured source citations.
    5. Persist the turn into the session's conversation history.
    """
    if vector_store_manager.is_empty():
        raise ValueError("No documents have been uploaded yet. Please upload a PDF first.")

    llm = _get_llm()
    history_aware_retriever = _build_history_aware_retriever(llm)
    qa_chain = create_stuff_documents_chain(llm, _build_qa_prompt())
    rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)

    chat_history = session_store.as_lc_messages(session_id)

    try:
        result = rag_chain.invoke({"input": question, "chat_history": chat_history})
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Failed to generate answer: {exc}") from exc

    answer = (result.get("answer") or "").strip()
    source_docs: List[Document] = result.get("context", [])

    # Build clean, frontend-friendly citation objects from the retrieved chunks.
    # Snippets are shortened to ~120 chars, and duplicate sources (same page with
    # near-identical content) are skipped so the Sources section stays clean.
    sources = []
    seen_sources = set()
    for doc in source_docs:
        filename = doc.metadata.get("filename", "unknown")
        page = doc.metadata.get("page", "N/A")
        content = doc.page_content.strip()
        # Use filename + page + a normalized slice of the content to detect
        # near-duplicate chunks retrieved from overlapping splits.
        dedupe_key = (filename, page, content[:120].lower())
        if dedupe_key in seen_sources:
            continue
        seen_sources.add(dedupe_key)
        sources.append(
            {
                "filename": filename,
                "page": page,
                "snippet": content[:120] + ("..." if len(content) > 120 else ""),
            }
        )

    # Persist this turn so future questions in the session have context
    session_store.append(session_id, "user", question)
    session_store.append(session_id, "assistant", answer)

    return {"answer": answer, "sources": sources}


# ---------------------------------------------------------------------------
# Suggested questions
# ---------------------------------------------------------------------------
def generate_suggested_questions(num_questions: int = 4) -> List[str]:
    """
    Generates suggested starter questions based on a sample of the
    stored document content, so users immediately know what to ask
    after uploading.

    This is treated as a "nice-to-have": if it fails for any reason
    (e.g. LLM hiccup), we return an empty list rather than breaking
    the upload flow.
    """
    sample_docs = vector_store_manager.similarity_search(
        query="summary overview main topics key findings", k=4
    )
    if not sample_docs:
        return []

    context = "\n\n".join(doc.page_content[:500] for doc in sample_docs)

    prompt = (
        "Based on the following document excerpts, suggest "
        f"{num_questions} concise, specific questions a researcher might ask "
        "to explore this content. Return ONLY the questions, one per line, "
        "with no numbering or extra commentary.\n\nExcerpts:\n" + context
    )

    try:
        llm = _get_llm()
        response = llm.invoke(prompt)
        questions = [q.strip("-•* ").strip() for q in response.content.split("\n") if q.strip()]
        return questions[:num_questions]
    except Exception:  # noqa: BLE001 - non-critical feature, fail silently
        return []
