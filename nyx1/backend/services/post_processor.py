import re
from typing import Any, Dict, Optional

UNSAFE_PATTERNS = [
    re.compile(r"here(?:'s| is) how to (?:kill|hurt) yourself", re.IGNORECASE),
    re.compile(r"step(?:-| )by(?:-| )step .*self[- ]harm", re.IGNORECASE),
    re.compile(r"detailed instructions .*weapon", re.IGNORECASE),
]


def post_process_response(response: str, risk: Optional[Dict[str, Any]] = None) -> str:
    risk = risk or {}
    safe_response = (response or "").strip()

    if not safe_response:
        safe_response = "I am here with you. Tell me what is going on, one small piece at a time."

    if any(pattern.search(safe_response) for pattern in UNSAFE_PATTERNS):
        safe_response = (
            "I cannot help with instructions that could cause harm. I can stay with you, "
            "help you slow things down, and support you in reaching someone safe right now."
        )

    if risk.get("crisis"):
        crisis_note = (
            " If you might hurt yourself or someone else, contact local emergency services now "
            "or reach out to a trusted person who can stay with you."
        )
        if "emergency" not in safe_response.lower():
            safe_response += crisis_note
    elif risk.get("level") in {"high", "medium"}:
        support_note = (
            " This is not a substitute for professional support, but I can help you think "
            "through the next small step."
        )
        if "professional support" not in safe_response.lower():
            safe_response += support_note

    return safe_response
