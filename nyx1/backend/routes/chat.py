from fastapi import APIRouter, Request

from backend.controllers.chat_controller import ChatRequest, send_message

router = APIRouter()


@router.post("/send")
async def send_chat_message(payload: ChatRequest, request: Request):
    return await send_message(payload, request)
