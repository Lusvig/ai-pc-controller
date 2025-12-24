"""Main AI engine orchestrator."""

from __future__ import annotations

from typing import Optional

from src.ai.prompts.system_prompts import SYSTEM_PROMPT
from src.ai.response_parser import ParsedResponse, ResponseParser
from src.ai.providers.gemini_provider import GeminiProvider
from src.ai.providers.groq_provider import GroqProvider
from src.ai.providers.ollama_provider import OllamaProvider
from src.ai.providers.openai_provider import OpenAIProvider
from src.utils.config_manager import AppConfig, ConfigManager, get_config_manager
from src.utils.exceptions import AIProviderError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AIEngine:
    """High-level orchestrator that talks to the configured AI provider."""

    def __init__(self, config: Optional[AppConfig] = None, config_manager: Optional[ConfigManager] = None):
        self.config_manager = config_manager or get_config_manager()
        self.config = config or self.config_manager.config
        self.provider = self._create_provider()

    def _create_provider(self):
        provider_name = self.config.ai.provider

        if provider_name == "ollama":
            return OllamaProvider(
                host=self.config.ai.ollama.host,
                model=self.config.ai.ollama.model,
                timeout=self.config.ai.ollama.timeout,
            )

        api_key = self.config_manager.get_api_key(provider_name) or ""

        if provider_name == "gemini":
            return GeminiProvider(
                api_key=api_key,
                model=self.config.ai.gemini.model,
                temperature=self.config.ai.gemini.temperature,
                max_tokens=self.config.ai.gemini.max_tokens,
            )

        if provider_name == "groq":
            return GroqProvider(
                api_key=api_key,
                model=self.config.ai.groq.model,
                temperature=self.config.ai.groq.temperature,
                max_tokens=self.config.ai.groq.max_tokens,
            )

        if provider_name == "openai":
            base_url = self.config_manager.env.openai_base_url or None
            return OpenAIProvider(api_key=api_key, model="gpt-4o-mini", base_url=base_url)

        raise ValueError(f"Unsupported provider: {provider_name}")

    def generate_raw(self, user_input: str) -> str:
        """Get raw provider output."""

        return self.provider.generate(user_input, system_prompt=SYSTEM_PROMPT)

    def process(self, user_input: str) -> ParsedResponse:
        """Generate and parse a response."""

        raw = self.generate_raw(user_input)
        try:
            return ResponseParser.parse(raw)
        except Exception as e:
            logger.warning(f"Failed to parse AI response; falling back to chat: {e}")
            return ParsedResponse(action="chat", params={}, message=raw, raw_text=raw)

    def safe_process(self, user_input: str) -> ParsedResponse:
        """Process a command, returning a chat action on provider errors."""

        try:
            return self.process(user_input)
        except AIProviderError as e:
            return ParsedResponse(action="chat", params={}, message=str(e), raw_text=str(e))
