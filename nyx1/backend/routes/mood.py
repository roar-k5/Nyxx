"""NYX Mood Routes — weekly insights endpoint."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends

from backend.authentication.auth_routes import get_current_user
from backend.database.mood_analyzer import get_mood_insights, store_mood

router = APIRouter(tags=["mood"])


@router.get("/weekly")
async def mood_weekly(user: Dict[str, Any] = Depends(get_current_user)):
    return await get_mood_insights(user["id"])


@router.post("/store")
async def mood_store(payload: dict, user: Dict[str, Any] = Depends(get_current_user)):
    emotion = payload.get("emotion", "neutral")
    intensity = payload.get("intensity", 0.5)
    await store_mood(user["id"], emotion, intensity)
    return {"status": "stored"}
