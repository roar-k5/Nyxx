from fastapi import APIRouter, Request, Depends, HTTPException

from backend.controllers.chat_controller import ChatRequest, send_message
from backend.middleware.rate_limiter import chat_limiter, rate_limit
from backend.authentication.auth_routes import get_current_user

router = APIRouter()


@router.post("/send")
async def send_chat_message(payload: ChatRequest, request: Request, user=Depends(get_current_user)):
    # Validate history size to prevent abuse
    if len(payload.history) > 50:
        raise HTTPException(status_code=400, detail="History too large. Maximum 50 messages allowed.")
    chat_limiter.raise_if_limited(request)
    return await send_message(payload, request)
