"""Ollama provider integration."""

from __future__ import annotations

from typing import Optional

import httpx

from src.utils.exceptions import AIConnectionError, AIResponseError

from .base_provider import AIProviderInfo, BaseAIProvider


class OllamaProvider(BaseAIProvider):
    info = AIProviderInfo(name="ollama", supports_streaming=False)

    def __init__(self, host: str, model: str, timeout: int = 60, **kwargs):
        super().__init__(host=host, model=model, timeout=timeout, **kwargs)
        self.host = host.rstrip("/")
        self.model = model
        self.timeout = timeout

    def health_check(self) -> bool:
        try:
            with httpx.Client(timeout=5) as client:
                r = client.get(f"{self.host}/api/tags")
            return r.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(f"{self.host}/api/generate", json=payload)
        except Exception as e:
            raise AIConnectionError("ollama", message=str(e)) from e

        if resp.status_code >= 400:
            raise AIResponseError("ollama", response=resp.text, message=f"HTTP {resp.status_code}")

        try:
            data = resp.json()
        except Exception as e:
            raise AIResponseError("ollama", response=resp.text, message="Invalid JSON") from e

        if not isinstance(data, dict) or "response" not in data:
            raise AIResponseError("ollama", response=data)

        return str(data.get("response", ""))
