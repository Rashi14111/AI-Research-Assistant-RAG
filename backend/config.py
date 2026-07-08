"""
Configuration module for the AI Research Assistant backend.

Centralizes all environment variables and application settings in one
place using pydantic-settings. Every other module imports `settings`
from here instead of reading os.environ directly - this keeps
configuration consistent and easy to change.
"""
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings, loaded from environment variables / .env file."""

    # --- Google Gemini API ---------------------------------------------
    google_api_key: str  # Required. Set this in a .env file or environment variable.

    # --- LLM configuration ------------------------------------------------
    llm_model_name: str = "gemini-2.5-flash"
    # "models/embedding-001" was deprecated by Google and now returns a 404
    # on the current API. "models/gemini-embedding-001" is the currently
    # supported general-purpose text embedding model (3072 dims by default,
    # works with standard Google AI Studio API keys).
    embedding_model_name: str = "models/gemini-embedding-001"
    llm_temperature: float = 0.1

    # --- Text splitting configuration --------------------------------------
    chunk_size: int = 700
    chunk_overlap: int = 100

    # --- Retrieval configuration ---------------------------------------------
    retrieval_k: int = 3 # Number of chunks to retrieve per query

    # --- Storage paths --------------------------------------------------------
    # base_dir points to the project root (one level above this backend/ folder)
    base_dir: Path = Path(__file__).resolve().parent.parent
    upload_dir: Path = base_dir / "storage" / "uploads"
    chroma_persist_dir: Path = base_dir / "storage" / "chroma_db"

    # --- ChromaDB ---------------------------------------------------------------
    chroma_collection_name: str = "research_assistant_docs"

    # --- API / CORS ---------------------------------------------------------------
    allowed_origins: List[str] = ["*"]  # Restrict this in real production deployments

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Single shared settings instance used across the whole backend
settings = Settings()

# Ensure required directories exist as soon as the app starts
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
