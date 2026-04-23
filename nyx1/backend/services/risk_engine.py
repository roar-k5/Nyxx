from typing import Any, Dict, List, Optional

CRISIS_KEYWORDS = [
    "suicide",
    "kill myself",
    "end my life",
    "self harm",
    "self-harm",
    "hurt myself",
    "want to die",
    "overdose",
    "cut myself",
    "can't go on",
    "cannot go on",
]

HIGH_RISK_KEYWORDS = [
    "hopeless",
    "worthless",
    "no reason to live",
    "goodbye forever",
    "i have a plan",
    "i have the pills",
]


def _includes_any(text: str, keywords: List[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def evaluate_risk(message: str, analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    analysis = analysis or {}
    normalized = (message or "").lower()
    risk_signals = analysis.get("riskSignals") if isinstance(analysis.get("riskSignals"), list) else []
    intent = str(analysis.get("intent", "")).lower()

    crisis = (
        _includes_any(normalized, CRISIS_KEYWORDS)
        or intent == "crisis"
        or any("crisis" in str(signal).lower() for signal in risk_signals)
    )

    if crisis:
        return {
            "level": "crisis",
            "crisis": True,
            "reasons": ["crisis_language_detected", *risk_signals],
        }

    if _includes_any(normalized, HIGH_RISK_KEYWORDS) or risk_signals:
        return {
            "level": "high",
            "crisis": False,
            "reasons": risk_signals or ["high_risk_language_detected"],
        }

    if analysis.get("emotion") in {"sad", "anxious", "distressed", "lonely"}:
        return {
            "level": "medium",
            "crisis": False,
            "reasons": ["emotional_distress_detected"],
        }

    return {"level": "low", "crisis": False, "reasons": []}
