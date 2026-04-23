"""NYX Mood Analyzer — aggregates emotion history from chat messages."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from backend.database.sqlite_fallback import get_db_sync


async def store_mood(user_id: str, emotion: str, intensity: float = 0.5) -> None:
    """Store a mood snapshot for a user."""
    db = get_db_sync()
    if db is None:
        return

    if hasattr(db, "moods"):
        await db.moods.insert_one({
            "user_id": user_id,
            "emotion": emotion,
            "intensity": intensity,
            "created_at": datetime.now(timezone.utc),
        })
    else:
        now = datetime.now(timezone.utc).isoformat()
        db.execute(
            "INSERT INTO moods (user_id, emotion, intensity, created_at) VALUES (?, ?, ?, ?)",
            (user_id, emotion, intensity, now),
        )
        db.commit()


async def get_mood_insights(user_id: str) -> Dict[str, Any]:
    """Return emotion stats and trend for the user."""
    db = get_db_sync()
    if db is None:
        return {"emotion": "neutral", "trend": "no_data", "stats": {}}

    since = datetime.now(timezone.utc) - timedelta(days=7)
    moods: List[Dict[str, Any]] = []

    if hasattr(db, "moods"):
        cursor = db.moods.find({"user_id": user_id, "created_at": {"$gte": since}})
        moods = await cursor.to_list(length=500)
    else:
        cursor = db.execute(
            "SELECT emotion FROM moods WHERE user_id = ? AND created_at >= ?",
            (user_id, since.isoformat()),
        )
        moods = [{"emotion": row["emotion"]} for row in cursor.fetchall()]

    if not moods:
        return {"emotion": "neutral", "trend": "no_data", "stats": {}}

    emotions = [m["emotion"] for m in moods]
    counts = Counter(emotions)
    dominant = counts.most_common(1)[0][0]

    half = len(moods) // 2
    first = Counter(emotions[:half])
    second = Counter(emotions[half:])
    first_top = first.most_common(1)[0][0] if first else "neutral"
    second_top = second.most_common(1)[0][0] if second else "neutral"

    if second_top in {"happy", "calm", "neutral"} and first_top in {"sad", "anxious", "distressed", "angry"}:
        trend = "improving"
    elif second_top in {"sad", "anxious", "distressed", "angry"} and first_top in {"happy", "calm", "neutral"}:
        trend = "declining"
    else:
        trend = "stable"

    total = len(moods)
    stats = {emotion: {"count": count, "percentage": round(count / total * 100, 1)} for emotion, count in counts.items()}

    return {
        "emotion": dominant,
        "trend": trend,
        "stats": stats,
        "total_entries": total,
        "period_days": 7,
    }
