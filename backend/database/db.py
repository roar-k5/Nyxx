"""NYX Database Layer — reusable MongoDB instance (Atlas-ready)."""
from __future__ import annotations

import os
import ssl
from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_mongo_client: Optional[AsyncIOMotorClient] = None
_mongo_db: Optional[AsyncIOMotorDatabase] = None


def _build_mongo_client(uri: str) -> AsyncIOMotorClient:
    """Build MongoDB client with Atlas-compatible TLS settings."""
    # Atlas requires TLS - auto-detect from URI
    is_atlas = "mongodb+srv" in uri or "ssl=true" in uri or "tls=true" in uri

    if is_atlas:
        # Atlas: TLS enabled, strict certificate validation
        return AsyncIOMotorClient(
            uri,
            serverSelectionTimeoutMS=5000,
            tls=True,
            tlsAllowInvalidCertificates=False,
            retryWrites=True,
            w="majority",
        )
    else:
        # Self-hosted / local: use URI as-is
        return AsyncIOMotorClient(uri, serverSelectionTimeoutMS=3000)


async def get_db() -> Optional[AsyncIOMotorDatabase]:
    """Return the shared database handle (initialises lazily if needed)."""
    global _mongo_client, _mongo_db

    if _mongo_db is not None:
        return _mongo_db

    uri = os.getenv("MONGO_URI")
    if not uri:
        return None

    try:
        _mongo_client = _build_mongo_client(uri)
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
