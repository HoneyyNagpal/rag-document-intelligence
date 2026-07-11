import os
import uuid
import logging
from datetime import datetime

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import settings

logger = logging.getLogger("document_processor")


class DocumentProcessor:
    """Handles turning an uploaded PDF into clean, embeddable chunks.

    LangChain's PyPDFLoader gives us one Document per page, which is a
    reasonable starting unit, but pages are a bad chunk boundary on their
    own -- paragraphs get cut off mid-sentence right at page breaks. So we
    run everything through RecursiveCharacterTextSplitter afterwards to get
    chunks that respect natural text boundaries (paragraphs, then
    sentences, then words) while still tagging each chunk with the page it
    came from for citation purposes.
    """

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def save_upload(self, file_bytes: bytes, original_filename: str) -> tuple[str, str]:
        document_id = str(uuid.uuid4())[:8]
        safe_name = original_filename.replace(" ", "_")
        stored_path = os.path.join(settings.UPLOAD_DIR, f"{document_id}_{safe_name}")

        with open(stored_path, "wb") as f:
            f.write(file_bytes)

        return document_id, stored_path

    def load_and_chunk(self, file_path: str, document_id: str, filename: str) -> list[dict]:
        loader = PyPDFLoader(file_path)
        pages = loader.load()

        if not pages:
            raise ValueError("No extractable text found in this PDF. It might be a scanned image.")

        raw_chunks = self.splitter.split_documents(pages)

        processed = []
        for i, chunk in enumerate(raw_chunks):
            page_number = chunk.metadata.get("page", 0) + 1
            processed.append({
                "id": f"{document_id}_chunk_{i}",
                "text": chunk.page_content.strip(),
                "metadata": {
                    "document_id": document_id,
                    "document_name": filename,
                    "page": page_number,
                    "chunk_index": i,
                    "uploaded_at": datetime.utcnow().isoformat(),
                },
            })

        logger.info(f"Split '{filename}' into {len(processed)} chunks from {len(pages)} pages")
        return processed
