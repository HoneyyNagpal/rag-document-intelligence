# RAG-Based Document Intelligence System

A full-stack Retrieval-Augmented Generation app for chatting with your own PDFs. Upload a document, ask questions in plain English, and get answers that are grounded in the actual text — with page-level source citations so you can verify every claim instead of just trusting the model.

I built this after getting tired of skimming long PDFs for one specific answer. The goal was something that actually cites where an answer came from, rather than just confidently making things up.

**Why this stack**

LangChain handles the document splitting logic so I didn't have to hand-roll a text chunker. ChromaDB is the vector store — it's local-first, persists to disk, and doesn't need a separate database server to stand up for a project this size. Groq is doing inference because their LPU-based API is genuinely fast for a chat-first UX; waiting 8 seconds per response kills the feel of a "real-time" assistant. FastAPI streams tokens back over Server-Sent Events so the frontend can render partial answers as they're generated, the same way ChatGPT does.

**What it does**

- Upload one or more PDFs, which get split into overlapping chunks and embedded with a sentence-transformers model
- Ask questions and get streamed, source-cited answers back in a chat UI
- Filter which documents a question should be answered against
- Session-level conversation memory, so follow-up questions like "what about the second clause" work
- Delete documents and their vectors from the index at any time

**Project layout**

```
rag-document-intelligence/
  backend/
    app/
      main.py              FastAPI app + CORS setup
      config.py             environment settings
      document_processor.py PDF loading and chunking
      vector_store.py       ChromaDB wrapper
      llm_service.py        Groq client + prompt engineering
      chat_service.py       ties retrieval and generation together
      session_manager.py    in-memory chat history per session
      routers/
        documents.py         upload / list / delete endpoints
        chat.py               chat + SSE streaming endpoints
    requirements.txt
    Dockerfile
  frontend/
    src/
      App.jsx
      components/
        Sidebar.jsx          upload + document list
        ChatWindow.jsx       message list + streaming input
        MessageBubble.jsx    renders markdown + source chips
        TypingIndicator.jsx
      api/client.js          fetch wrapper incl. SSE parsing
    Dockerfile
  docker-compose.yml
```

**Running it locally**

Backend:

```
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then paste in your GROQ_API_KEY
uvicorn app.main:app --reload
```

Frontend:

```
cd frontend
npm install
npm run dev
```

The frontend expects the backend on `localhost:8000` (see the proxy config in `vite.config.js`).

**Running it with Docker**

```
cp backend/.env.example backend/.env   # add your GROQ_API_KEY
docker compose up --build
```

Backend comes up on `:8000`, frontend on `:5173`.

**How the pipeline actually works**

1. A PDF is uploaded and saved to disk, then loaded page-by-page with `PyPDFLoader`.
2. Pages get run through `RecursiveCharacterTextSplitter` (1000 chars, 150 overlap) so chunks respect paragraph and sentence boundaries instead of cutting mid-thought.
3. Each chunk is embedded with `all-MiniLM-L6-v2` and upserted into a Chroma collection, tagged with document id, filename, and page number.
4. On a query, the top-k most similar chunks are retrieved (cosine similarity) and stitched into a context block.
5. That context, plus recent conversation history, gets sent to Groq with a system prompt that instructs the model to answer only from the given excerpts and admit when it doesn't know.
6. The response streams back token-by-token over SSE and the frontend renders it live, along with the source chunks used.

**Known limitations**

- Scanned/image-only PDFs won't extract text since there's no OCR step yet
- Session memory is in-process, so it resets if the backend restarts — fine for a demo, not for production
- No auth on the API right now, so don't expose this publicly as-is

**Possible next steps**

- Add OCR fallback (Tesseract) for scanned documents
- Move session memory to Redis for multi-worker deployments
- Support more file types (docx, txt, markdown)
- Add a re-ranking step before sending chunks to the LLM
