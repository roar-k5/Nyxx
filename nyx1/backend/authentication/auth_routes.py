"""NYX Authentication — FastAPI routes."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from backend.authentication.auth_controller import get_current_user_from_db, login_user, register_user
from backend.authentication.auth_model import UserLogin, UserRegister
from backend.authentication.jwt_utils import decode_token
from backend.middleware.rate_limiter import auth_limiter

router = APIRouter(tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    email: str | None = payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = await get_current_user_from_db(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def _get_client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


@router.post("/register")
async def register(payload: UserRegister, request: Request):
    auth_limiter.raise_if_limited(request)
    client_ip = _get_client_ip(request)
    result = await register_user(payload, client_ip)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
    return result


@router.post("/login")
async def login(payload: UserLogin, request: Request):
    auth_limiter.raise_if_limited(request)
    client_ip = _get_client_ip(request)
    result = await login_user(payload, client_ip)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=result["error"])
    return result


@router.get("/me")
async def me(user: Dict[str, Any] = Depends(get_current_user)):
    return {"user": user}
