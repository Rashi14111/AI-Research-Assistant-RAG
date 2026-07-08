"""
api.py
------
Thin HTTP client for the FastAPI backend. This is the ONLY module that
talks to the network - every other module calls functions from here
and receives a plain dict back, so UI code never has to deal with
`requests` exceptions directly.

Every function returns a dict of the shape:
    {"ok": True,  "data": <parsed json>}
    {"ok": False, "error": "<human-readable message>"}

Backend base URL is configurable from this single variable:
"""
import os
from typing import Any, Dict, List, Tuple

import requests

# ---------------------------------------------------------------------------
# Single configurable variable for the backend location.
# Override by setting the BACKEND_API_URL environment variable before
# launching Streamlit, e.g.:
#   BACKEND_API_URL=http://localhost:8000 streamlit run frontend/app.py
# ---------------------------------------------------------------------------
BASE_URL: str = os.getenv("BACKEND_API_URL", "http://localhost:8000")

# Reasonable timeouts: uploads/chat can take longer because they call the
# Gemini API server-side, so they get a longer allowance than simple GETs.
_SHORT_TIMEOUT = 10
_UPLOAD_TIMEOUT = 120
_CHAT_TIMEOUT = 60


def _handle_response(response: requests.Response) -> Dict[str, Any]:
    """
    Normalizes a requests.Response into the standard {ok, data|error} shape.
    Handles FastAPI's typical error payload format ({"detail": ...}).
    """
    try:
        response.raise_for_status()
        return {"ok": True, "data": response.json()}
    except requests.exceptions.HTTPError:
        # Try to extract FastAPI's structured error detail, fall back to raw text
        try:
            payload = response.json()
            detail = payload.get("detail", response.text)
        except ValueError:
            detail = response.text
        return {"ok": False, "error": f"{detail}"}
    except ValueError:
        return {"ok": False, "error": "The server returned an invalid response."}


def _request(method: str, path: str, **kwargs) -> Dict[str, Any]:
    """
    Central request wrapper. Every network call in this module funnels
    through here so connection/timeout errors are handled in one place.
    """
    url = f"{BASE_URL}{path}"
    try:
        response = requests.request(method, url, **kwargs)
        return _handle_response(response)
    except requests.exceptions.ConnectionError:
        return {
            "ok": False,
            "error": (
                f"Could not connect to the backend at {BASE_URL}. "
                "Make sure the FastAPI server is running."
            ),
        }
    except requests.exceptions.Timeout:
        return {"ok": False, "error": "The request timed out. Please try again."}
    except requests.exceptions.RequestException as exc:  # noqa: BLE001
        return {"ok": False, "error": f"Unexpected network error: {exc}"}


# ---------------------------------------------------------------------------
# System
# ---------------------------------------------------------------------------
def check_health() -> Dict[str, Any]:
    """Calls GET /health to check whether the backend is reachable."""
    return _request("GET", "/health", timeout=_SHORT_TIMEOUT)


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------
def upload_pdfs(files: List[Tuple[str, bytes]]) -> Dict[str, Any]:
    """
    Uploads one or more PDFs to POST /upload.

    `files` is a list of (filename, file_bytes) tuples, matching what
    Streamlit's file_uploader gives us after calling .getvalue().
    """
    if not files:
        return {"ok": False, "error": "No files selected."}

    multipart_payload = [
        ("files", (filename, file_bytes, "application/pdf"))
        for filename, file_bytes in files
    ]
    return _request("POST", "/upload", files=multipart_payload, timeout=_UPLOAD_TIMEOUT)


def list_documents() -> Dict[str, Any]:
    """Calls GET /documents to fetch all currently stored documents."""
    return _request("GET", "/documents", timeout=_SHORT_TIMEOUT)


def delete_document(doc_id: str) -> Dict[str, Any]:
    """Calls DELETE /documents/{doc_id} to remove a document and its chunks."""
    return _request("DELETE", f"/documents/{doc_id}", timeout=_SHORT_TIMEOUT)


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------
def send_chat_message(session_id: str, question: str) -> Dict[str, Any]:
    """Calls POST /chat to get a RAG-grounded answer with citations."""
    payload = {"session_id": session_id, "question": question}
    return _request("POST", "/chat", json=payload, timeout=_CHAT_TIMEOUT)


def get_history(session_id: str) -> Dict[str, Any]:
    """Calls GET /history/{session_id} to fetch stored conversation history."""
    return _request("GET", f"/history/{session_id}", timeout=_SHORT_TIMEOUT)


def clear_history(session_id: str) -> Dict[str, Any]:
    """Calls DELETE /history/{session_id} to wipe conversation history."""
    return _request("DELETE", f"/history/{session_id}", timeout=_SHORT_TIMEOUT)


def export_history(session_id: str) -> Dict[str, Any]:
    """Calls GET /export/{session_id} to fetch history in an exportable format."""
    return _request("GET", f"/export/{session_id}", timeout=_SHORT_TIMEOUT)
