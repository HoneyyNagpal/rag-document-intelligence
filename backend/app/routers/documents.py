import logging
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.document_processor import DocumentProcessor
from app.vector_store import vector_store
from app.schemas import UploadResponse, DocumentInfo

logger = logging.getLogger("documents_router")
router = APIRouter(prefix="/documents", tags=["documents"])

processor = DocumentProcessor()

ALLOWED_EXTENSIONS = {".pdf"}


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF files are supported right now.")

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    document_id, stored_path = processor.save_upload(file_bytes, file.filename)

    try:
        chunks = processor.load_and_chunk(stored_path, document_id, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        logger.exception("Failed to process uploaded PDF")
        raise HTTPException(status_code=500, detail="Failed to process this PDF.")

    vector_store.add_chunks(chunks)

    return UploadResponse(
        document_id=document_id,
        filename=file.filename,
        chunks_created=len(chunks),
        status="indexed",
    )


@router.get("", response_model=list[DocumentInfo])
async def list_documents():
    docs = vector_store.list_documents()
    return list(docs.values())


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    vector_store.delete_document(document_id)
    return {"status": "deleted", "document_id": document_id}
