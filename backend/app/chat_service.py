import logging
from app.vector_store import vector_store
from app.llm_service import llm_service
from app.session_manager import session_manager
from app.schemas import SourceChunk

logger = logging.getLogger("chat_service")


class ChatService:
    """Orchestrates the retrieve-then-generate flow for a single query."""

    def answer(self, session_id: str, query: str, document_ids: list[str] = None) -> dict:
        history = session_manager.get_history(session_id)
        chunks = vector_store.query(query, document_ids=document_ids)

        answer_text = llm_service.generate(query, chunks, history)

        session_manager.append_turn(session_id, "user", query)
        session_manager.append_turn(session_id, "assistant", answer_text)

        sources = [
            SourceChunk(
                document_name=c["metadata"]["document_name"],
                chunk_id=c["chunk_id"],
                page=c["metadata"].get("page"),
                snippet=c["text"][:220] + ("..." if len(c["text"]) > 220 else ""),
                score=c["score"],
            )
            for c in chunks
        ]

        return {"answer": answer_text, "sources": sources}

    def stream_answer(self, session_id: str, query: str, document_ids: list[str] = None):
        """Generator used by the SSE endpoint. Yields raw text chunks and
        stores the full answer in session history once streaming finishes."""
        history = session_manager.get_history(session_id)
        chunks = vector_store.query(query, document_ids=document_ids)

        session_manager.append_turn(session_id, "user", query)

        full_answer = []
        for delta in llm_service.stream(query, chunks, history):
            full_answer.append(delta)
            yield delta

        session_manager.append_turn(session_id, "assistant", "".join(full_answer))


chat_service = ChatService()
