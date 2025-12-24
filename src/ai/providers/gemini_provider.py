"""Google Gemini provider integration."""

from __future__ import annotations

from typing import Optional

from src.utils.exceptions import AIAPIKeyError, AIResponseError

from .base_provider import AIProviderInfo, BaseAIProvider


class GeminiProvider(BaseAIProvider):
    info = AIProviderInfo(name="gemini", supports_streaming=False)

    def __init__(self, api_key: str, model: str, temperature: float = 0.7, max_tokens: int = 2048, **kwargs):
        if not api_key:
            raise AIAPIKeyError("gemini")
        super().__init__(api_key=api_key, model=model, temperature=temperature, max_tokens=max_tokens, **kwargs)
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model, system_instruction=system_prompt)
            resp = model.generate_content(prompt, generation_config={"temperature": self.temperature, "max_output_tokens": self.max_tokens})
            text = getattr(resp, "text", None)
            if not text:
                raise AIResponseError("gemini", response=resp)
            return text
        except AIResponseError:
            raise
        except Exception as e:
            raise AIResponseError("gemini", response=str(e), message="Gemini request failed") from e
