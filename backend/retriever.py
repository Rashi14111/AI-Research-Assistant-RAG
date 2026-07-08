"""
Retriever module.

Owns all interactions with ChromaDB: adding chunks, deleting documents,
listing what's currently stored, and running semantic similarity search.
No other module talks to Chroma directly - this keeps the vector-store
logic in one testable place.
"""
import uuid
from typing import Any, Dict, List, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document

from backend.config import settings
from backend.embeddings import get_embeddings


class VectorStoreManager:
    """Thin, focused wrapper around a persistent Chroma collection."""

    def __init__(self) -> None:
        try:
            self._store = Chroma(
                collection_name=settings.chroma_collection_name,
                embedding_function=get_embeddings(),
                persist_directory=str(settings.chroma_persist_dir),
            )
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Failed to initialize ChromaDB: {exc}") from exc

    def add_documents(self, documents: List[Document], doc_id: str, filename: str) -> int:
        """
        Adds chunked LangChain Documents to the vector store.

        Each chunk is tagged with `doc_id` and `filename` metadata so that
        chunks can later be (a) grouped back into a document for listing,
        (b) deleted together, and (c) cited by filename in chat answers.

        Returns the number of chunks stored.
        """
        if not documents:
            return 0

        for doc in documents:
            doc.metadata["doc_id"] = doc_id
            doc.metadata["filename"] = filename

        # Unique IDs per chunk avoid collisions across multiple uploads
        ids = [f"{doc_id}_{i}_{uuid.uuid4().hex[:8]}" for i in range(len(documents))]

        try:
            self._store.add_documents(documents=documents, ids=ids)
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Failed to add documents to ChromaDB: {exc}") from exc

        return len(documents)

    def similarity_search(self, query: str, k: Optional[int] = None) -> List[Document]:
        """Performs semantic similarity search across all stored documents."""
        k = k or settings.retrieval_k
        try:
            return self._store.similarity_search(query, k=k)
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Similarity search failed: {exc}") from exc
        
        
        
    def as_retriever(self, k: Optional[int] = None):
        """
        Returns an MMR-based retriever.

        Max Marginal Relevance (MMR) retrieves highly relevant chunks while
        removing near-duplicate passages. This improves answer quality by
        giving the LLM more diverse context instead of multiple overlapping
        chunks from the same section of the document.
        """
        k = k or settings.retrieval_k

        return self._store.as_retriever(
           search_type="mmr",
           search_kwargs={
               "k": k,                 # Final chunks sent to the LLM
               "fetch_k": 20,          # Retrieve more candidates first
               "lambda_mult": 0.55,    # More diversity (0=diverse, 1=relevance)
            },
        )    



    def delete_document(self, doc_id: str) -> None:
        """Deletes every chunk belonging to a given document id."""
        try:
            self._store.delete(where={"doc_id": doc_id})
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Failed to delete document '{doc_id}': {exc}") from exc

    def list_documents(self) -> List[Dict[str, Any]]:
        """
        Returns a de-duplicated summary of documents currently stored,
        derived by grouping chunk metadata by doc_id.
        """
        try:
            data = self._store.get(include=["metadatas"])
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Failed to list documents: {exc}") from exc

        summary: Dict[str, Dict[str, Any]] = {}
        for meta in data.get("metadatas", []) or []:
            doc_id = meta.get("doc_id")
            if not doc_id:
                continue
            if doc_id not in summary:
                summary[doc_id] = {
                    "doc_id": doc_id,
                    "filename": meta.get("filename", "unknown"),
                    "chunk_count": 0,
                }
            summary[doc_id]["chunk_count"] += 1

        return list(summary.values())

    def is_empty(self) -> bool:
        """Checks whether the vector store currently holds no documents."""
        return len(self.list_documents()) == 0


# Single shared instance used across the app (simple in-process singleton).
vector_store_manager = VectorStoreManager()
