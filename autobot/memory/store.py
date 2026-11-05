import sqlite3
from datetime import datetime, timezone
from pathlib import Path

class MemoryStore:
    """SQLite store for conversation messages and application events."""
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL,
                role TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL,
                payload TEXT NOT NULL, created_at TEXT NOT NULL)""")

    def add_message(self, session_id: str, role: str, content: str) -> None:
        with self._connect() as db:
            db.execute("INSERT INTO messages(session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                       (session_id, role, content, datetime.now(timezone.utc).isoformat()))

    def recent_messages(self, session_id: str = "default", limit: int = 30) -> list[dict]:
        with self._connect() as db:
            rows = db.execute("SELECT role, content, created_at FROM messages "
                              "WHERE session_id = ? ORDER BY id DESC LIMIT ?", (session_id, limit)).fetchall()
        return [dict(row) for row in reversed(rows)]

    def add_event(self, kind: str, payload: str) -> None:
        with self._connect() as db:
            db.execute("INSERT INTO events(kind, payload, created_at) VALUES (?, ?, ?)",
                       (kind, payload, datetime.now(timezone.utc).isoformat()))
