"""NYX Database Layer — reusable MongoDB instance."""
from __future__ import annotations

import os
from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_mongo_client: Optional[AsyncIOMotorClient] = None
_mongo_db: Optional[AsyncIOMotorDatabase] = None


async def get_db() -> Optional[AsyncIOMotorDatabase]:
    """Return the shared database handle (initialises lazily if needed)."""
    global _mongo_client, _mongo_db

    if _mongo_db is not None:
        return _mongo_db

    uri = os.getenv("MONGO_URI")
    if not uri:
        return None

    try:
        _mongo_client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=3000)
        await _mongo_client.admin.command("ping")
        _mongo_db = _mongo_client.get_default_database(default="nyx")
        print("MongoDB connected.")
    except Exception as e:
        print(f"MongoDB connection failed: {e}. Running without DB.")
        _mongo_client = None
        _mongo_db = None
    return _mongo_db


def get_db_sync() -> Optional[AsyncIOMotorDatabase]:
    """Synchronous variant for use inside sync contexts (returns the cached handle)."""
    return _mongo_db


async def close_db() -> None:
    """Gracefully close the client — call on shutdown."""
    global _mongo_client, _mongo_db
    if _mongo_client:
        _mongo_client.close()
    _mongo_client = None
    _mongo_db = None
