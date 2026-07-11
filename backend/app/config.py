import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central place for all environment-driven settings.

    Keeping this in one file instead of scattering os.getenv() calls
    all over the codebase makes it a lot easier to see what the app
    actually depends on at runtime.
    """

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_store")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "document_chunks")

    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 150))

    TOP_K: int = int(os.getenv("TOP_K", 4))

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")

    MAX_SESSION_HISTORY: int = int(os.getenv("MAX_SESSION_HISTORY", 12))

    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")


settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
