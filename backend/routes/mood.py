"""NYX Mood Routes — weekly insights endpoint."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

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
    # Validate emotion against allowed set
    allowed_emotions = {"anxious", "sad", "angry", "hopeless", "overwhelmed", "neutral", "hopeful", "grateful"}
    if emotion not in allowed_emotions:
        raise HTTPException(status_code=400, detail=f"Invalid emotion. Allowed: {', '.join(allowed_emotions)}")
    # Validate intensity range
    try:
        intensity = float(intensity)
        if not 0.0 <= intensity <= 1.0:
            raise ValueError
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Intensity must be a float between 0.0 and 1.0")
    await store_mood(user["id"], emotion, intensity)
    return {"status": "stored"}
