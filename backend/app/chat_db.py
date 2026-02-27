"""
chat_db.py -- SQLite-backed chat session storage for InsightX.

Tables
------
  sessions:  id (TEXT PK), title (TEXT), created_at (TEXT), updated_at (TEXT)
  messages:  id (INTEGER PK), session_id (TEXT FK), role (TEXT), content (TEXT),
             sql_text (TEXT), data_json (TEXT), created_at (TEXT)
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DB_DIR / "chat_history.db"


def _conn() -> sqlite3.Connection:
    """Return a connection with row_factory set to sqlite3.Row."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create tables if they don't exist."""
    with _conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id         TEXT PRIMARY KEY,
                title      TEXT NOT NULL DEFAULT 'New chat',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                role       TEXT NOT NULL,          -- 'user' | 'assistant'
                content    TEXT NOT NULL DEFAULT '',
                sql_text   TEXT DEFAULT '',
                data_json  TEXT DEFAULT '{}',
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_messages_session
                ON messages(session_id);
        """)


# ── Sessions ──────────────────────────────────────────────────────────────────

def create_session(title: str = "New chat") -> dict:
    now = datetime.now(timezone.utc).isoformat()
    sid = uuid.uuid4().hex[:12]
    with _conn() as conn:
        conn.execute(
            "INSERT INTO sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (sid, title, now, now),
        )
    return {"id": sid, "title": title, "created_at": now, "updated_at": now}


def list_sessions(limit: int = 50) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT id, title, created_at, updated_at FROM sessions ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def delete_session(session_id: str) -> bool:
    with _conn() as conn:
        cur = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    return cur.rowcount > 0


def update_session_title(session_id: str, title: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with _conn() as conn:
        conn.execute(
            "UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?",
            (title, now, session_id),
        )


def _touch_session(session_id: str) -> None:
    """Bump updated_at for a session."""
    now = datetime.now(timezone.utc).isoformat()
    with _conn() as conn:
        conn.execute(
            "UPDATE sessions SET updated_at = ? WHERE id = ?",
            (now, session_id),
        )


# ── Messages ──────────────────────────────────────────────────────────────────

def add_message(
    session_id: str,
    role: str,
    content: str,
    sql_text: str = "",
    data_json: str = "{}",
) -> int:
    now = datetime.now(timezone.utc).isoformat()
    with _conn() as conn:
        cur = conn.execute(
            """INSERT INTO messages (session_id, role, content, sql_text, data_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (session_id, role, content, sql_text, data_json, now),
        )
        # Bump session updated_at in the SAME connection (avoids database-locked)
        conn.execute(
            "UPDATE sessions SET updated_at = ? WHERE id = ?",
            (now, session_id),
        )
    return cur.lastrowid  # type: ignore


def get_messages(session_id: str) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            """SELECT id, role, content, sql_text, data_json, created_at
               FROM messages WHERE session_id = ? ORDER BY id ASC""",
            (session_id,),
        ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["data"] = json.loads(d.pop("data_json"))
        except (json.JSONDecodeError, KeyError):
            d["data"] = {}
            d.pop("data_json", None)
        result.append(d)
    return result


def auto_title(session_id: str, first_question: str) -> None:
    """Set session title from the first user question (truncated)."""
    title = first_question.strip()[:60]
    if len(first_question.strip()) > 60:
        title += "..."
    update_session_title(session_id, title)
