"""NYX Health Checks — LLM provider connectivity verification."""
from __future__ import annotations

import asyncio
import os
from typing import Dict, Optional

import httpx


class LLMHealthChecker:
    """Verify LLM provider connectivity at startup."""

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "groq")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.lmstudio_url = os.getenv("LMSTUDIO_URL", "http://localhost:1234")

    async def check_groq(self) -> tuple[bool, Optional[str]]:
        if not self.groq_api_key:
            return False, "GROQ_API_KEY not configured"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    "https://api.groq.com/openai/v1/models",
                    headers={"Authorization": f"Bearer {self.groq_api_key}"},
                )
                if response.status_code == 200:
                    return True, None
                return False, f"Groq API returned {response.status_code}"
        except Exception as e:
            return False, f"Groq connection failed: {str(e)}"

    async def check_gemini(self) -> tuple[bool, Optional[str]]:
        if not self.gemini_api_key:
            return False, "GEMINI_API_KEY not configured"
        try:
            from google import genai
            client = genai.Client(api_key=self.gemini_api_key)
            # Try a simple models list
            models = list(client.models.list())
            if models:
                return True, None
            return False, "Gemini returned empty model list"
        except Exception as e:
            return False, f"Gemini connection failed: {str(e)}"

    async def check_ollama(self) -> tuple[bool, Optional[str]]:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                if response.status_code == 200:
                    return True, None
                return False, f"Ollama returned {response.status_code}"
        except Exception as e:
            return False, f"Ollama connection failed: {str(e)}"

    async def check_lmstudio(self) -> tuple[bool, Optional[str]]:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.lmstudio_url}/v1/models")
                if response.status_code == 200:
                    return True, None
                return False, f"LM Studio returned {response.status_code}"
        except Exception as e:
            return False, f"LM Studio connection failed: {str(e)}"

    async def check(self) -> Dict[str, any]:
        """Run health check for configured provider."""
        if self.provider == "mock":
            return {"provider": "mock", "healthy": True, "message": "Mock mode active"}

        checkers = {
            "groq": self.check_groq,
            "gemini": self.check_gemini,
            "ollama": self.check_ollama,
            "lmstudio": self.check_lmstudio,
        }

        checker = checkers.get(self.provider)
        if not checker:
            return {"provider": self.provider, "healthy": False, "message": f"Unknown provider: {self.provider}"}

        healthy, error = await checker()
        return {
            "provider": self.provider,
            "healthy": healthy,
            "message": error or "Connected successfully",
        }


# Global instance
llm_health_checker = LLMHealthChecker()
