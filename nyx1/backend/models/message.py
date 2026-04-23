from datetime import datetime, timezone
from typing import Any, Dict, Optional


async def save_message(
    database: Optional[Any],
    role: str,
    content: str,
    emotion: str = "neutral",
    crisis: bool = False,
) -> Optional[str]:
    if database is None:
        return None

    document: Dict[str, Any] = {
        "role": role,
        "content": content,
        "emotion": emotion,
        "crisis": crisis,
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    }

    result = await database.messages.insert_one(document)
    return str(result.inserted_id)
