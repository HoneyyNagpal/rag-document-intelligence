import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import documents, chat
from app.session_manager import session_manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

app = FastAPI(
    title="Document Intelligence API",
    description="RAG backend for querying uploaded PDFs with source-cited answers.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    return {"service": "rag-document-intelligence", "status": "running"}


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "active_sessions": session_manager.active_session_count(),
    }
