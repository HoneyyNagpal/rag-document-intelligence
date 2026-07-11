import logging
from groq import Groq

from app.config import settings

logger = logging.getLogger("llm_service")

SYSTEM_PROMPT = """You are a careful research assistant that answers questions using ONLY the \
document excerpts provided in the context below. Follow these rules strictly:

1. Base your answer only on the given context. Do not use outside knowledge.
2. If the context does not contain enough information to answer, say so plainly instead \
of guessing.
3. When you use a fact from a specific excerpt, refer to it naturally (e.g. "according to \
the section on pricing...").
4. Keep answers focused and avoid padding them with generic filler.
5. If the user's question is unrelated to the documents, politely say the documents don't \
cover that topic.
"""


class LLMService:
    """Wraps the Groq chat completion API with a RAG-specific system prompt.

    Kept deliberately separate from vector_store.py and chat_service.py so
    swapping the LLM provider later (say, to a self-hosted model) only
    means touching this one file.
    """

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    def _build_context_block(self, chunks: list[dict]) -> str:
        blocks = []
        for i, chunk in enumerate(chunks, start=1):
            meta = chunk["metadata"]
            blocks.append(
                f"[Excerpt {i} | {meta['document_name']}, page {meta['page']}]\n{chunk['text']}"
            )
        return "\n\n".join(blocks)

    def _build_messages(self, query: str, chunks: list[dict], history: list[dict]) -> list[dict]:
        context_block = self._build_context_block(chunks)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        for turn in history[-settings.MAX_SESSION_HISTORY:]:
            messages.append({"role": turn["role"], "content": turn["content"]})

        user_message = f"Context:\n{context_block}\n\nQuestion: {query}"
        messages.append({"role": "user", "content": user_message})

        return messages

    def generate(self, query: str, chunks: list[dict], history: list[dict]) -> str:
        if not chunks:
            return "I couldn't find anything relevant to that in the uploaded documents."

        messages = self._build_messages(query, chunks, history)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
            max_tokens=800,
        )
        return response.choices[0].message.content

    def stream(self, query: str, chunks: list[dict], history: list[dict]):
        """Yields text deltas as they arrive from Groq, for SSE responses."""
        if not chunks:
            yield "I couldn't find anything relevant to that in the uploaded documents."
            return

        messages = self._build_messages(query, chunks, history)

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
            max_tokens=800,
            stream=True,
        )

        for event in stream:
            delta = event.choices[0].delta.content
            if delta:
                yield delta


llm_service = LLMService()
