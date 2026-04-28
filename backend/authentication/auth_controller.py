"""NYX Authentication — business logic."""
from __future__ import annotations

from typing import Any, Dict

from passlib.context import CryptContext

from backend.authentication.auth_model import UserLogin, UserRegister
from backend.authentication.jwt_utils import create_access_token
from backend.authentication.password_validator import validate_password
from backend.database.sqlite_fallback import get_db
from backend.middleware.security_logging import security_logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


async def register_user(payload: UserRegister, client_ip: str | None = None) -> Dict[str, Any]:
    # Validate password strength
    is_valid, error_msg = validate_password(payload.password)
    if not is_valid:
        security_logger.auth_register(payload.email, False, client_ip, error_msg)
        return {"error": error_msg}

    # Prefer MongoDB; fall back to SQLite only when explicitly allowed
    db = await get_db()
    if db is None:
        security_logger.auth_register(payload.email, False, client_ip, "Database not available")
        return {"error": "Database not available"}

    # Check if user already exists
    if hasattr(db, "users"):
        # MongoDB
        existing = await db.users.find_one({"email": payload.email})
        if existing:
            security_logger.auth_register(payload.email, False, client_ip, "Email already registered")
            return {"error": "Email already registered"}
        user_doc = {
            "email": payload.email,
            "name": payload.name,
            "hashed_password": hash_password(payload.password),
        }
        result = await db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)
    else:
        # SQLite
        cursor = db.execute("SELECT id FROM users WHERE email = ?", (payload.email,))
        if cursor.fetchone():
            security_logger.auth_register(payload.email, False, client_ip, "Email already registered")
            return {"error": "Email already registered"}
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        cursor = db.execute(
            "INSERT INTO users (email, name, hashed_password, created_at) VALUES (?, ?, ?, ?)",
            (payload.email, payload.name, hash_password(payload.password), now),
        )
        db.commit()
        user_id = str(cursor.lastrowid)

    token = create_access_token({"sub": payload.email, "user_id": user_id})
    security_logger.auth_register(payload.email, True, client_ip)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "email": payload.email, "name": payload.name},
    }


async def login_user(payload: UserLogin, client_ip: str | None = None) -> Dict[str, Any]:
    # Prefer MongoDB; fall back to SQLite only when explicitly allowed
    db = await get_db()
    if db is None:
        security_logger.auth_login_attempt(payload.email, False, client_ip, "Database not available")
        return {"error": "Database not available"}

    user = None
    if hasattr(db, "users"):
        # MongoDB
        user = await db.users.find_one({"email": payload.email})
        if not user or not verify_password(payload.password, user.get("hashed_password", "")):
            security_logger.auth_login_attempt(payload.email, False, client_ip, "Invalid credentials")
            return {"error": "Invalid email or password"}
        user_id = str(user["_id"])
        name = user.get("name", "")
    else:
        # SQLite
        cursor = db.execute("SELECT id, email, name, hashed_password FROM users WHERE email = ?", (payload.email,))
        row = cursor.fetchone()
        if not row or not verify_password(payload.password, row["hashed_password"]):
            security_logger.auth_login_attempt(payload.email, False, client_ip, "Invalid credentials")
            return {"error": "Invalid email or password"}
        user_id = str(row["id"])
        name = row["name"] or ""

    token = create_access_token({"sub": payload.email, "user_id": user_id})
    security_logger.auth_login_attempt(payload.email, True, client_ip)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "email": payload.email, "name": name},
    }


async def get_current_user_from_db(email: str) -> Dict[str, Any] | None:
    # Prefer MongoDB; fall back to SQLite only when explicitly allowed
    db = await get_db()
    if db is None:
        return None

    if hasattr(db, "users"):
        user = await db.users.find_one({"email": email})
        if user:
            return {"id": str(user["_id"]), "email": user["email"], "name": user.get("name", "")}
    else:
        cursor = db.execute("SELECT id, email, name FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            return {"id": str(row["id"]), "email": row["email"], "name": row["name"] or ""}
    return None
