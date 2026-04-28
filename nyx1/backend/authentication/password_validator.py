"""NYX Authentication — password validation and strength checking."""
from __future__ import annotations

import re
from typing import Tuple


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must not exceed 128 characters"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_=+\[\];'/\\`~]", password):
        return False, "Password must contain at least one special character"
    
    # Check for common weak patterns
    common_patterns = [
        r"^password",
        r"^123456",
        r"^qwerty",
        r"^abc123",
        r"^letmein",
        r"^welcome",
        r"^admin",
    ]
    
    lower_password = password.lower()
    for pattern in common_patterns:
        if re.search(pattern, lower_password):
            return False, "Password is too common or easily guessable"
    
    return True, ""
