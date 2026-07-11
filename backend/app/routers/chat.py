import json
import logging
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas import ChatRequest, ChatResponse
from app.chat_service import chat_service
from app.session_manager import session_manager

logger = logging.getLogger("chat_router")
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    result = chat_service.answer(request.session_id, request.query, request.document_ids)
    return ChatResponse(answer=result["answer"], sources=result["sources"], session_id=request.session_id)


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    def event_generator():
        try:
            for delta in chat_service.stream_answer(request.session_id, request.query, request.document_ids):
                payload = json.dumps({"delta": delta})
                yield f"data: {payload}\n\n"
        except Exception:
            logger.exception("Error while streaming chat response")
            error_payload = json.dumps({"error": "Something went wrong while generating a response."})
            yield f"data: {error_payload}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    session_manager.clear(session_id)
    return {"status": "cleared", "session_id": session_id}
