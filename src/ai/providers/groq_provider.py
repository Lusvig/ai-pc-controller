"""Groq provider integration."""

from __future__ import annotations

from typing import Optional

from src.utils.exceptions import AIAPIKeyError, AIResponseError

from .base_provider import AIProviderInfo, BaseAIProvider


class GroqProvider(BaseAIProvider):
    info = AIProviderInfo(name="groq", supports_streaming=False)

    def __init__(self, api_key: str, model: str, temperature: float = 0.7, max_tokens: int = 2048, **kwargs):
        if not api_key:
            raise AIAPIKeyError("groq")
        super().__init__(api_key=api_key, model=model, temperature=temperature, max_tokens=max_tokens, **kwargs)
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        try:
            from groq import Groq

            client = Groq(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            resp = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            choice = resp.choices[0]
            content = getattr(choice.message, "content", None)
            if not content:
                raise AIResponseError("groq", response=resp)
            return content
        except AIResponseError:
            raise
        except Exception as e:
            raise AIResponseError("groq", response=str(e), message="Groq request failed") from e
