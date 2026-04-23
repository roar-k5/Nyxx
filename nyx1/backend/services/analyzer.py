import json
import os
import re
from typing import Any, Dict, Optional

from groq import AsyncGroq

from backend.config import env as _env

DEFAULT_ANALYSIS: Dict[str, Any] = {
    "emotion": "neutral",
    "intent": "conversation",
    "riskSignals": [],
    "summary": "",
}


def _client() -> Optional[AsyncGroq]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return AsyncGroq(api_key=api_key)


def _extract_json(content: str) -> Optional[Dict[str, Any]]:
    if not content:
        return None

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", content)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None


async def analyze_message(message: str) -> Dict[str, Any]:
    client = _client()
    if client is None:
        return DEFAULT_ANALYSIS.copy()

    try:
        completion = await client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Analyze the user message and return STRICT JSON only. "
                        "No markdown and no extra text. Schema: "
                        '{"emotion":"neutral|sad|angry|anxious|happy|lonely|confused|distressed",'
                        '"intent":"conversation|support|question|venting|crisis|other",'
                        '"riskSignals":["string"],"summary":"string"}.'
                    ),
                },
                {"role": "user", "content": message or ""},
            ],
        )
    except Exception as exc:
        print(f"Analyzer failed: {exc}")
        return DEFAULT_ANALYSIS.copy()

    content = completion.choices[0].message.content or ""
    parsed = _extract_json(content) or {}
    result = {**DEFAULT_ANALYSIS, **parsed}

    if not isinstance(result.get("riskSignals"), list):
        result["riskSignals"] = []

    return result
