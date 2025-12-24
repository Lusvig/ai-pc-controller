"""OpenAI-compatible provider integration."""

from __future__ import annotations

from typing import Optional

from src.utils.exceptions import AIAPIKeyError, AIResponseError

from .base_provider import AIProviderInfo, BaseAIProvider


class OpenAIProvider(BaseAIProvider):
    info = AIProviderInfo(name="openai", supports_streaming=False)

    def __init__(self, api_key: str, model: str, base_url: str | None = None, **kwargs):
        if not api_key:
            raise AIAPIKeyError("openai")
        super().__init__(api_key=api_key, model=model, base_url=base_url, **kwargs)
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key, base_url=self.base_url or None)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            resp = client.chat.completions.create(model=self.model, messages=messages)
            content = resp.choices[0].message.content
            if not content:
                raise AIResponseError("openai", response=resp)
            return content
        except AIResponseError:
            raise
        except Exception as e:
            raise AIResponseError("openai", response=str(e), message="OpenAI request failed") from e
