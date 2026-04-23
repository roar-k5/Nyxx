from typing import Any, Dict, List, Optional

from backend.config.prompts import (
    NYXX_CORE_PROMPT,
    NYXX_CRISIS_PROMPT,
    NYXX_EMOTION_GUIDANCE,
    NYXX_ENGAGEMENT_GUIDANCE,
    NYXX_GREETING_PROMPT,
    NYXX_OFFTOPIC_PROMPT,
)

GREETING_WORDS = {"hi", "hii", "hiii", "hello", "hey", "yo", "sup", "namaste"}
OFFTOPIC_KEYWORDS = {
    "cricket",
    "football",
    "sports",
    "news",
    "politics",
    "movie",
    "stock",
    "weather",
    "trivia",
    "medicine",
    "medication",
    "tablet",
    "dose",
    "dosage",
    "prescription",
}


def _normalize_history(history: Any) -> List[Dict[str, str]]:
    if not isinstance(history, list):
        return []

    messages: List[Dict[str, str]] = []
    for item in history:
        if not isinstance(item, dict) or not isinstance(item.get("content"), str):
            continue
        role = item.get("role") if item.get("role") in {"user", "assistant", "system"} else "user"
        messages.append({"role": role, "content": item["content"][:2000]})

    return messages[-5:]


def _is_greeting(message: str) -> bool:
    words = {word.strip(".,!? ").lower() for word in message.split()}
    return bool(words) and len(words) <= 4 and bool(words & GREETING_WORDS)


def _is_offtopic(message: str, analysis: Dict[str, Any]) -> bool:
    normalized = (message or "").lower()
    intent = str(analysis.get("intent", "")).lower()
    return intent == "other" or any(keyword in normalized for keyword in OFFTOPIC_KEYWORDS)


def _engagement_key(message: str) -> str:
    words = (message or "").split()
    lowered = (message or "").lower()

    if len(words) <= 3:
        return "short_reply"
    if any(phrase in lowered for phrase in ("i can't", "i cannot", "stuck", "don't know what to do")):
        return "stuck"
    if len(words) > 18:
        return "opening_up"
    if any(phrase in lowered for phrase in ("tired", "exhausted", "drained")):
        return "low_energy"
    return "default"


def build_prompt(
    message: str,
    history: Any = None,
    analysis: Optional[Dict[str, Any]] = None,
    risk: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, str]]:
    analysis = analysis or {}
    risk = risk or {}
    emotion = str(analysis.get("emotion", "neutral")).lower()
    guidance = [
        NYXX_CORE_PROMPT,
        NYXX_EMOTION_GUIDANCE.get(emotion, NYXX_EMOTION_GUIDANCE["neutral"]),
        NYXX_ENGAGEMENT_GUIDANCE[_engagement_key(message)],
    ]

    if _is_greeting(message):
        guidance.append(NYXX_GREETING_PROMPT)

    if risk.get("crisis"):
        guidance.append(NYXX_CRISIS_PROMPT)

    if _is_offtopic(message, analysis):
        guidance.append(NYXX_OFFTOPIC_PROMPT)

    guidance.append(f"Detected emotion: {analysis.get('emotion', 'neutral')}.")
    guidance.append(f"Risk level: {risk.get('level', 'low')}. Crisis: {bool(risk.get('crisis'))}.")

    system_prompt = "\n\n".join(guidance)

    return [
        {"role": "system", "content": system_prompt},
        *_normalize_history(history),
        {"role": "user", "content": message or ""},
    ]
