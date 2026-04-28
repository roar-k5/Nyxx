"""NYX Security Logging — structured audit trail for security events."""
from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Configure structured logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")  # 'json' or 'text'


class SecurityLogger:
    """Structured security event logger."""

    def __init__(self):
        self.logger = logging.getLogger("nyx.security")
        self.logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            if LOG_FORMAT == "json":
                handler.setFormatter(logging.Formatter(
                    '%(message)s'
                ))
            else:
                handler.setFormatter(logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                ))
            self.logger.addHandler(handler)

    def _log(self, level: str, event_type: str, details: Dict[str, Any]) -> None:
        """Emit a structured log entry."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "level": level,
            **details,
        }
        if LOG_FORMAT == "json":
            print(json.dumps(entry))
        else:
            getattr(self.logger, level.lower(), self.logger.info)(
                f"[{event_type}] {json.dumps(details)}"
            )

    def auth_login_attempt(self, email: str, success: bool, ip: Optional[str] = None, error: Optional[str] = None) -> None:
        self._log("INFO" if success else "WARNING", "auth_login_attempt", {
            "email": email,
            "success": success,
            "client_ip": ip,
            "error": error,
        })

    def auth_register(self, email: str, success: bool, ip: Optional[str] = None, error: Optional[str] = None) -> None:
        self._log("INFO", "auth_register", {
            "email": email,
            "success": success,
            "client_ip": ip,
            "error": error,
        })

    def auth_token_refresh(self, email: str, success: bool, ip: Optional[str] = None) -> None:
        self._log("INFO", "auth_token_refresh", {
            "email": email,
            "success": success,
            "client_ip": ip,
        })

    def chat_message(self, user_id: str, message_length: int, emotion: str, crisis: bool, ip: Optional[str] = None) -> None:
        self._log("INFO", "chat_message", {
            "user_id": user_id,
            "message_length": message_length,
            "detected_emotion": emotion,
            "crisis_triggered": crisis,
            "client_ip": ip,
        })

    def crisis_detected(self, user_id: str, risk_score: int, ip: Optional[str] = None) -> None:
        self._log("CRITICAL", "crisis_detected", {
            "user_id": user_id,
            "risk_score": risk_score,
            "client_ip": ip,
        })

    def rate_limit_exceeded(self, endpoint: str, client_ip: str, limit: str) -> None:
        self._log("WARNING", "rate_limit_exceeded", {
            "endpoint": endpoint,
            "client_ip": client_ip,
            "limit": limit,
        })

    def prompt_injection_attempt(self, user_id: str, pattern: str, ip: Optional[str] = None) -> None:
        self._log("WARNING", "prompt_injection_attempt", {
            "user_id": user_id,
            "detected_pattern": pattern,
            "client_ip": ip,
        })

    def unauthorized_access(self, endpoint: str, client_ip: Optional[str] = None, reason: Optional[str] = None) -> None:
        self._log("WARNING", "unauthorized_access", {
            "endpoint": endpoint,
            "client_ip": client_ip,
            "reason": reason,
        })

    def db_error(self, operation: str, error: str) -> None:
        self._log("ERROR", "db_error", {
            "operation": operation,
            "error": error,
        })


# Global instance
security_logger = SecurityLogger()
