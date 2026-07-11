import time
import threading
from app.config import settings


class SessionManager:
    """In-memory store for per-session conversation history.

    This is fine for a single-process deployment and for the scope of this
    project. In a real multi-worker production setup you'd want to move
    this to Redis so history survives restarts and is shared across
    workers, but that felt like overkill here.
    """

    def __init__(self):
        self._sessions: dict[str, list[dict]] = {}
        self._last_seen: dict[str, float] = {}
        self._lock = threading.Lock()

    def get_history(self, session_id: str) -> list[dict]:
        with self._lock:
            return list(self._sessions.get(session_id, []))

    def append_turn(self, session_id: str, role: str, content: str) -> None:
        with self._lock:
            history = self._sessions.setdefault(session_id, [])
            history.append({"role": role, "content": content})
            self._last_seen[session_id] = time.time()

            max_len = settings.MAX_SESSION_HISTORY * 2
            if len(history) > max_len:
                self._sessions[session_id] = history[-max_len:]

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)
            self._last_seen.pop(session_id, None)

    def active_session_count(self) -> int:
        with self._lock:
            return len(self._sessions)


session_manager = SessionManager()
