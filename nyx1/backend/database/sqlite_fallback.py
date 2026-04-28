"""NYX Database Layer — SQLite fallback when MongoDB is unavailable."""
from __future__ import annotations

import os
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.database.db import get_db as get_mongo_db

# Store SQLite outside the project directory to prevent accidental exposure
# In production, set SQLITE_PATH to a secure location (e.g., /var/lib/nyx/nyx.sqlite)
_SQLITE_PATH = os.getenv("SQLITE_PATH", os.path.join(os.path.dirname(__file__), "nyx.sqlite"))
_sqlite_conn: Optional[sqlite3.Connection] = None
_sqlite_lock = threading.Lock()


def _get_sqlite() -> sqlite3.Connection:
    global _sqlite_conn
    if _sqlite_conn is None:
        with _sqlite_lock:
            if _sqlite_conn is None:
                # Ensure directory exists
                os.makedirs(os.path.dirname(_SQLITE_PATH), exist_ok=True)
                _sqlite_conn = sqlite3.connect(_SQLITE_PATH, check_same_thread=False)
                _sqlite_conn.row_factory = sqlite3.Row
                _init_tables()
    return _sqlite_conn


def _init_tables() -> None:
    conn = _sqlite_conn
    if conn is None:
        return
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            hashed_password TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS moods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            emotion TEXT NOT NULL,
            intensity REAL NOT NULL DEFAULT 0.5,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            emotion TEXT,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_moods_user ON moods(user_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user_id, created_at);
        """
    )
    conn.commit()


async def get_db() -> Any:
    """Return MongoDB if available, otherwise SQLite."""
    mongo = await get_mongo_db()
    if mongo is not None:
        return mongo
    return _get_sqlite()


def get_db_sync() -> Any:
    """Synchronous variant."""
    return _get_sqlite()


async def close_db() -> None:
    """Close all DB connections."""
    global _sqlite_conn
    from backend.database.db import close_db as close_mongo
    await close_mongo()
    if _sqlite_conn:
        with _sqlite_lock:
            if _sqlite_conn:
                _sqlite_conn.close()
                _sqlite_conn = None
