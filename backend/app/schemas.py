from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    session_id: str
    query: str = Field(..., min_length=1)
    document_ids: Optional[list[str]] = None


class SourceChunk(BaseModel):
    document_name: str
    chunk_id: str
    page: Optional[int] = None
    snippet: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    session_id: str


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    chunks_created: int
    status: str


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    chunk_count: int
    uploaded_at: str
