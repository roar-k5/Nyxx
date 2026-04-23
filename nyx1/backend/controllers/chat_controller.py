import asyncio
import os
from typing import Any, Dict, List, Optional

from fastapi import Request
from groq import AsyncGroq
from pydantic import BaseModel, Field

from backend.config import env as _env
from backend.models.message import save_message
from backend.services.analyzer import analyze_message
from backend.services.post_processor import post_process_response
from backend.services.prompt_builder import build_prompt
from backend.services.risk_engine import evaluate_risk


class HistoryMessage(BaseModel):
    role: str = Field(default="user")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: List[HistoryMessage] = Field(default_factory=list)


def _client() -> Optional[AsyncGroq]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return AsyncGroq(api_key=api_key)


async def _generate_response(messages: List[Dict[str, str]]) -> str:
    client = _client()
    if client is None:
        return "NYXX is not configured yet. Add GROQ_API_KEY to the backend environment, then try again."

    try:
        completion = await client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=0.7,
            max_tokens=500,
            messages=messages,
        )
    except Exception as exc:
        print(f"Groq response generation failed: {exc}")
        return "I am having trouble connecting right now, but I am still here. Try again in a moment."

    return completion.choices[0].message.content or ""


async def send_message(payload: ChatRequest, request: Request) -> Dict[str, Any]:
    try:
        message = payload.message.strip()
        history = [item.model_dump() for item in payload.history]

        analysis = await analyze_message(message)
        risk = evaluate_risk(message, analysis)
        prompt = build_prompt(message=message, history=history, analysis=analysis, risk=risk)
        raw_response = await _generate_response(prompt)
        response = post_process_response(raw_response, risk)

        database = getattr(request.app.state, "database", None)
        await asyncio.gather(
            save_message(database, "user", message, analysis.get("emotion", "neutral"), bool(risk.get("crisis"))),
            save_message(database, "assistant", response, analysis.get("emotion", "neutral"), bool(risk.get("crisis"))),
            return_exceptions=True,
        )

        return {
            "response": response,
            "emotion": analysis.get("emotion", "neutral"),
            "crisis": bool(risk.get("crisis")),
        }
    except Exception as exc:
        print(f"Chat flow failed: {exc}")
        return {
            "response": "Something went wrong while NYXX was responding. Please try again.",
            "emotion": "neutral",
            "crisis": False,
        }
