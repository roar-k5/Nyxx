"""NYX Safety Layer — crisis detection without real helpline numbers."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

CRISIS_KEYWORDS: List[str] = [
    "suicide", "kill myself", "end my life", "self harm", "self-harm",
    "hurt myself", "want to die", "overdose", "cut myself",
    "can't go on", "cannot go on", "no reason to live",
]

HIGH_RISK_KEYWORDS: List[str] = [
    "hopeless", "worthless", "goodbye forever", "i have a plan",
    "i have the pills", "i want to disappear",
]


def detect_crisis(message: str, analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return crisis assessment without real helpline numbers."""
    text = (message or "").lower()
    analysis = analysis or {}
    risk_signals = analysis.get("riskSignals") if isinstance(analysis.get("riskSignals"), list) else []
    intent = str(analysis.get("intent", "")).lower()

    crisis = (
        any(kw in text for kw in CRISIS_KEYWORDS)
        or intent == "crisis"
        or any("crisis" in str(s).lower() for s in risk_signals)
    )

    high_risk = any(kw in text for kw in HIGH_RISK_KEYWORDS)

    if crisis:
        return {
            "level": "crisis",
            "crisis": True,
            "reasons": ["crisis_language_detected"] + [str(s) for s in risk_signals],
            "message": (
                "You matter. If you are in immediate danger, please contact local emergency services "
                "or a trusted person near you right now."
            ),
        }

    if high_risk:
        return {
            "level": "high",
            "crisis": False,
            "reasons": ["high_risk_language_detected"] + [str(s) for s in risk_signals],
            "message": (
                "It sounds like things are really heavy right now. "
                "Talking to someone you trust can make a difference."
            ),
        }

    return {"level": "low", "crisis": False, "reasons": [], "message": ""}
