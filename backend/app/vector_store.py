import logging
import chromadb
from chromadb.utils import embedding_functions

from app.config import settings

logger = logging.getLogger("vector_store")


class VectorStore:
    """Thin wrapper around a persistent ChromaDB collection.

    Chroma is doing the heavy lifting here (HNSW index under the hood),
    this class just keeps embedding + upsert + query logic in one place
    so the rest of the app doesn't need to know Chroma's API shape.
    """

    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)

        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=settings.EMBEDDING_MODEL
        )

        self.collection = self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, chunks: list[dict]) -> None:
        if not chunks:
            return

        self.collection.upsert(
            ids=[c["id"] for c in chunks],
            documents=[c["text"] for c in chunks],
            metadatas=[c["metadata"] for c in chunks],
        )
        logger.info(f"Upserted {len(chunks)} chunks into '{settings.COLLECTION_NAME}'")

    def query(self, query_text: str, top_k: int = None, document_ids: list[str] = None) -> list[dict]:
        top_k = top_k or settings.TOP_K

        where_filter = None
        if document_ids:
            where_filter = {"document_id": {"$in": document_ids}}

        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k,
            where=where_filter,
        )

        hits = []
        if not results["ids"] or not results["ids"][0]:
            return hits

        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i]
            hits.append({
                "chunk_id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": round(1 - distance, 4),
            })

        return hits

    def list_documents(self) -> dict:
        all_items = self.collection.get()
        docs = {}
        for meta in all_items["metadatas"]:
            doc_id = meta["document_id"]
            if doc_id not in docs:
                docs[doc_id] = {
                    "document_id": doc_id,
                    "filename": meta["document_name"],
                    "chunk_count": 0,
                    "uploaded_at": meta.get("uploaded_at", ""),
                }
            docs[doc_id]["chunk_count"] += 1
        return docs

    def delete_document(self, document_id: str) -> None:
        self.collection.delete(where={"document_id": document_id})
        logger.info(f"Deleted all chunks for document {document_id}")


vector_store = VectorStore()
