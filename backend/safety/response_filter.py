"""NYX Safety Layer — response filtering."""
from __future__ import annotations

import re
from typing import Any, Dict, Optional

UNSAFE_PATTERNS = [
    re.compile(r"here(?:'s| is) how to (?:kill|hurt) yourself", re.IGNORECASE),
    re.compile(r"step(?:-| )by(?:-| )step .*self[- ]harm", re.IGNORECASE),
    re.compile(r"detailed instructions .*weapon", re.IGNORECASE),
    re.compile(r"how to (?:commit|plan) suicide", re.IGNORECASE),
    re.compile(r"overdose (?:guide|steps|amount)", re.IGNORECASE),
]

SAFE_RESPONSE = (
    "I cannot provide instructions that could cause harm. "
    "I can stay with you, help you slow things down, and support you in reaching someone safe."
)


def filter_response(response: str, risk: Optional[Dict[str, Any]] = None) -> str:
    """Sanitize assistant response based on risk and unsafe patterns."""
    risk = risk or {}
    safe = (response or "").strip()

    if not safe:
        safe = "I am here with you. Tell me what is going on, one small piece at a time."

    if any(p.search(safe) for p in UNSAFE_PATTERNS):
        safe = SAFE_RESPONSE

    if risk.get("crisis"):
        crisis_note = (
            " If you might hurt yourself or someone else, contact local emergency services now "
            "or reach out to a trusted person who can stay with you."
        )
        if "emergency" not in safe.lower():
            safe += crisis_note
    elif risk.get("level") in {"high", "medium"}:
        support_note = (
            " This is not a substitute for professional support, but I can help you think "
            "through the next small step."
        )
        if "professional support" not in safe.lower():
            safe += support_note

    return safe
