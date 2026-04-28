"""NYX Rate Limiting — in-memory sliding window rate limiter."""
from __future__ import annotations

import os
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from fastapi import HTTPException, Request, status


@dataclass
class _Bucket:
    requests: List[float] = field(default_factory=list)


class RateLimiter:
    """Simple in-memory rate limiter. Use Redis in production."""

    def __init__(
        self,
        requests_per_minute: int = 60,
        burst: int = 10,
        block_duration: int = 300,
    ):
        self.requests_per_minute = requests_per_minute
        self.burst = burst
        self.block_duration = block_duration
        self._buckets: Dict[str, _Bucket] = defaultdict(_Bucket)
        self._blocked: Dict[str, float] = {}

    def _key(self, request: Request) -> str:
        """Use client IP + path as key."""
        forwarded = request.headers.get("x-forwarded-for")
        client_ip = forwarded.split(",")[0].strip() if forwarded else request.client.host if request.client else "unknown"
        return f"{client_ip}:{request.url.path}"

    def is_allowed(self, request: Request) -> bool:
        key = self._key(request)
        now = time.time()

        # Check if currently blocked
        if key in self._blocked:
            if now - self._blocked[key] < self.block_duration:
                return False
            del self._blocked[key]

        bucket = self._buckets[key]
        # Clean old requests outside the 60-second window
        bucket.requests = [t for t in bucket.requests if now - t < 60]

        if len(bucket.requests) >= self.burst:
            # Block this client
            self._blocked[key] = now
            return False

        if len(bucket.requests) >= self.requests_per_minute:
            return False

        bucket.requests.append(now)
        return True

    def raise_if_limited(self, request: Request) -> None:
        if not self.is_allowed(request):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please slow down.",
            )


# Global instances for different endpoints
public_limiter = RateLimiter(requests_per_minute=30, burst=10)
auth_limiter = RateLimiter(requests_per_minute=10, burst=5, block_duration=600)
chat_limiter = RateLimiter(requests_per_minute=20, burst=5)


def rate_limit(limiter: RateLimiter) -> Callable:
    """Decorator-style dependency for FastAPI routes."""
    def dependency(request: Request) -> None:
        limiter.raise_if_limited(request)
    return dependency
