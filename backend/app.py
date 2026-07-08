"""
FastAPI application entry point.

Exposes REST endpoints for:
- Uploading and ingesting PDF documents
- Chatting with the uploaded documents (RAG)
- Listing / deleting documents
- Managing and exporting conversation history

Run with:  uvicorn backend.app:app --reload
"""
import shutil
import uuid
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.config import settings
from backend.rag import answer_question, generate_suggested_questions, process_pdf, session_store
from backend.retriever import vector_store_manager

from backend.config import settings

print("Loaded API Key:", settings.google_api_key[:10] + "...")

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI Research Assistant API",
    description="A RAG-powered backend for chatting with uploaded PDF documents.",
    version="1.0.0",
)

# CORS is needed so the Streamlit frontend (a different process/port) can call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / response schemas (Pydantic models give us free validation + docs)
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique id identifying the chat session/user.")
    question: str = Field(..., description="The user's question about the uploaded documents.")


class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]


class MessageResponse(BaseModel):
    message: str


# ---------------------------------------------------------------------------
# System endpoints
# ---------------------------------------------------------------------------
@app.get("/health", response_model=MessageResponse, tags=["System"])
def health_check() -> MessageResponse:
    """Simple health check used to verify the API is running."""
    return MessageResponse(message="ok")


# ---------------------------------------------------------------------------
# Document upload & ingestion
# ---------------------------------------------------------------------------
@app.post("/upload", tags=["Documents"])
async def upload_documents(files: List[UploadFile] = File(...)) -> JSONResponse:
    """
    Accepts one or more PDF files, saves them to disk, splits them into
    chunks, embeds those chunks, and stores them in ChromaDB.

    Returns a per-file ingestion summary, any per-file errors, and a
    set of suggested starter questions based on the newly uploaded content.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded.")

    results = []
    errors = []

    for upload_file in files:
        if not upload_file.filename or not upload_file.filename.lower().endswith(".pdf"):
            errors.append({"filename": upload_file.filename, "error": "Only PDF files are supported."})
            continue

        # Save with a unique prefix so identically-named files never collide on disk
        safe_name = f"{uuid.uuid4().hex}_{upload_file.filename}"
        dest_path: Path = settings.upload_dir / safe_name

        try:
            with dest_path.open("wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)

            summary = process_pdf(str(dest_path), upload_file.filename)
            results.append(summary)
        except Exception as exc:  # noqa: BLE001 - report per-file, don't abort the whole batch
            errors.append({"filename": upload_file.filename, "error": str(exc)})
        finally:
            upload_file.file.close()

    if not results and errors:
        # Every single file failed - this is a genuine client-facing error
        raise HTTPException(status_code=422, detail={"errors": errors})

    suggested_questions = generate_suggested_questions()

    return JSONResponse(
        content={
            "uploaded": results,
            "errors": errors,
            "suggested_questions": suggested_questions,
        }
    )


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------
@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat(request: ChatRequest) -> ChatResponse:
    """Answers a user's question using retrieval-augmented generation."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        result = answer_question(request.session_id, request.question)
        return ChatResponse(**result)
    except ValueError as exc:
        # Expected "business" errors, e.g. no documents uploaded yet
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Internal error while answering: {exc}") from exc


# ---------------------------------------------------------------------------
# Document management
# ---------------------------------------------------------------------------
@app.get("/documents", tags=["Documents"])
def list_documents() -> dict:
    """Lists all documents currently stored in the vector database."""
    try:
        return {"documents": vector_store_manager.list_documents()}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.delete("/documents/{doc_id}", response_model=MessageResponse, tags=["Documents"])
def delete_document(doc_id: str) -> MessageResponse:
    """Deletes a document and all of its chunks from ChromaDB."""
    try:
        vector_store_manager.delete_document(doc_id)
        return MessageResponse(message=f"Document '{doc_id}' deleted successfully.")
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Conversation history
# ---------------------------------------------------------------------------
@app.get("/history/{session_id}", tags=["Chat"])
def get_history(session_id: str) -> dict:
    """Returns the full chat history for a given session."""
    return {"history": session_store.get_history(session_id)}


@app.delete("/history/{session_id}", response_model=MessageResponse, tags=["Chat"])
def clear_history(session_id: str) -> MessageResponse:
    """Clears the chat history for a given session."""
    session_store.clear(session_id)
    return MessageResponse(message=f"History cleared for session '{session_id}'.")


@app.get("/export/{session_id}", tags=["Chat"])
def export_history(session_id: str) -> dict:
    """
    Returns the chat history in a structured, exportable format.
    The frontend is responsible for turning this into a downloadable file
    (e.g. .txt or .json) via Streamlit's download button.
    """
    history = session_store.get_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="No chat history found for this session.")
    return {"session_id": session_id, "history": history}
