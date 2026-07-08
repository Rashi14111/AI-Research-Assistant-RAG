"""
Embeddings module.

Wraps Google Generative AI Embeddings behind a single factory function.
Keeping this in its own module (rather than instantiating embeddings
inline inside retriever.py or rag.py) means the embedding provider can
be swapped later (e.g. to OpenAI or a local model) by editing only
this file.
"""
from functools import lru_cache

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from backend.config import settings


@lru_cache(maxsize=1)
def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """
    Returns a cached (singleton-like) instance of the Google embeddings client.

    lru_cache ensures the embeddings client is created only once and reused
    across the whole application, avoiding redundant client initialization.
    """
    try:
        return GoogleGenerativeAIEmbeddings(
            model=settings.embedding_model_name,
            google_api_key=settings.google_api_key,
        )
    except Exception as exc:  # noqa: BLE001 - surface a clear, actionable error
        raise RuntimeError(
            f"Failed to initialize Google embeddings model "
            f"('{settings.embedding_model_name}'): {exc}"
        ) from exc
