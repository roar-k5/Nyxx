"""NYX Safety Layer — LLM prompt injection filter."""
from __future__ import annotations

import re
from typing import List, Optional

# Known prompt injection patterns
INJECTION_PATTERNS: List[re.Pattern] = [
    re.compile(r"ignore\s+(all\s+)?previous\s+(instructions?|commands?|prompts?)", re.IGNORECASE),
    re.compile(r"ignore\s+above\s+(instructions?|commands?|prompts?)", re.IGNORECASE),
    re.compile(r"forget\s+(everything|all)\s+(you\s+)?(were\s+)?told", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(a\s+)?\w+", re.IGNORECASE),
    re.compile(r"new\s+(role|persona|identity)", re.IGNORECASE),
    re.compile(r"act\s+as\s+(a\s+)?\w+", re.IGNORECASE),
    re.compile(r"pretend\s+to\s+be\s+(a\s+)?\w+", re.IGNORECASE),
    re.compile(r"system\s*:\s*", re.IGNORECASE),
    re.compile(r"user\s*:\s*", re.IGNORECASE),
    re.compile(r"assistant\s*:\s*", re.IGNORECASE),
    re.compile(r"\{\{.*?\}\}", re.IGNORECASE),  # Template injection
    re.compile(r"\[%\s*.*\s*%\]", re.IGNORECASE),  # Template injection
    re.compile(r"jailbreak", re.IGNORECASE),
    re.compile(r"DAN\s*mode", re.IGNORECASE),
    re.compile(r"developer\s*mode", re.IGNORECASE),
    re.compile(r"sudo\s+", re.IGNORECASE),
    re.compile(r"root\s+access", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(safety|ethical|guideline|policy)", re.IGNORECASE),
    re.compile(r"bypass\s+(all\s+)?(safety|filter|restriction)", re.IGNORECASE),
    re.compile(r"\n\s*\n\s*(system|user|assistant)\s*[:\-]\s*", re.IGNORECASE),  # Role injection
]

# Maximum allowed special characters ratio (to catch encoding tricks)
MAX_SPECIAL_RATIO = 0.4


def sanitize_for_llm(text: str) -> str:
    """
    Sanitize user input before sending to LLM.
    
    Returns cleaned text. Raises ValueError if injection detected.
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Check for injection patterns
    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            raise ValueError(
                "Potentially unsafe input detected. Please rephrase your message."
            )
    
    # Check for excessive special characters (encoding tricks)
    special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
    if len(text) > 0 and special_chars / len(text) > MAX_SPECIAL_RATIO:
        raise ValueError(
            "Input contains too many special characters. Please use plain text."
        )
    
    # Remove null bytes and control characters
    text = text.replace("\x00", "")
    text = "".join(c for c in text if ord(c) >= 32 or c in "\n\r\t")
    
    # Normalize excessive whitespace
    text = " ".join(text.split())
    
    return text


def is_safe_for_llm(text: str) -> tuple[bool, Optional[str]]:
    """
    Check if text is safe for LLM without raising.
    
    Returns:
        Tuple of (is_safe, error_message)
    """
    try:
        sanitize_for_llm(text)
        return True, None
    except ValueError as e:
        return False, str(e)
