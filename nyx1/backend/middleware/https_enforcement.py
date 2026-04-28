"""NYX Security Middleware — HTTPS enforcement and trusted host validation."""
from __future__ import annotations

import os
from typing import Optional

from fastapi import HTTPException, Request, status

# Environment-based HTTPS enforcement
# Set ENFORCE_HTTPS=true in production
ENFORCE_HTTPS = os.getenv("ENFORCE_HTTPS", "").strip().lower() in {"1", "true", "yes", "on"}

# Trusted hosts for production
TRUSTED_HOSTS_STR = os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1")
TRUSTED_HOSTS = [h.strip() for h in TRUSTED_HOSTS_STR.split(",") if h.strip()]


class HTTPSRedirectMiddleware:
    """Redirect HTTP to HTTPS in production."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        
        # Skip HTTPS check for local development
        if not ENFORCE_HTTPS:
            await self.app(scope, receive, send)
            return

        # Check for HTTPS
        is_https = (
            request.url.scheme == "https"
            or request.headers.get("x-forwarded-proto") == "https"
            or request.headers.get("x-forwarded-ssl") == "on"
        )

        if not is_https:
            # Return 403 instead of redirect to prevent MITM downgrade attacks
            response = HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="HTTPS required. Please use a secure connection.",
            )
            raise response

        await self.app(scope, receive, send)


def check_trusted_host(request: Request) -> None:
    """Validate request comes from a trusted host."""
    host = request.headers.get("host", "").split(":")[0]
    if host not in TRUSTED_HOSTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid host header.",
        )
