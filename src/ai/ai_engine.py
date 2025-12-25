"""Main AI engine orchestrator.

This module coordinates AI providers and provides a resilient interface for the
rest of the app. In particular, it attempts to prevent confusing errors like
HTTP 404 from Ollama by ensuring the provider is initialized and ready before
first use.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from src.ai.prompts.system_prompts import get_system_prompt
from src.ai.response_parser import ParsedResponse, ResponseParser
from src.ai.providers.base_provider import BaseAIProvider
from src.ai.providers.gemini_provider import GeminiProvider
from src.ai.providers.groq_provider import GroqProvider
from src.ai.providers.ollama_provider import OllamaProvider
from src.ai.providers.openai_provider import OpenAIProvider
from src.utils.config_manager import AppConfig, ConfigManager, get_config_manager
from src.utils.exceptions import (
    AIAPIKeyError,
    AIConnectionError,
    AIModelNotFoundError,
    AIProviderError,
    AIResponseError,
)
from src.utils.logger import get_logger
from src.utils.ollama_helper import get_ollama_helper

logger = get_logger(__name__)


class AIEngine:
    """High-level orchestrator that talks to the configured AI provider."""

    def __init__(
        self,
        config: Optional[AppConfig] = None,
        config_manager: Optional[ConfigManager] = None,
        provider_name: Optional[str] = None,
    ):
        self.config_manager = config_manager or get_config_manager()
        self.config = config or self.config_manager.config

        self.provider_name = (provider_name or self.config.ai.provider).lower()
        self.provider: Optional[BaseAIProvider] = None

        self._is_initialized = False
        self._initialization_error: Optional[str] = None

        # Create provider lazily on initialize so GUI startup can present friendly
        # status if something is missing.

    def _create_provider(self, provider_name: str) -> Optional[BaseAIProvider]:
        provider_name = provider_name.lower()

        try:
            if provider_name == "ollama":
                return OllamaProvider(
                    host=self.config.ai.ollama.host,
                    model=self.config.ai.ollama.model,
                    timeout=self.config.ai.ollama.timeout,
                    context_length=self.config.ai.ollama.context_length,
                )

            api_key = self.config_manager.get_api_key(provider_name) or ""

            if provider_name == "gemini":
                if not api_key:
                    return None
                return GeminiProvider(
                    api_key=api_key,
                    model=self.config.ai.gemini.model,
                    temperature=self.config.ai.gemini.temperature,
                    max_tokens=self.config.ai.gemini.max_tokens,
                )

            if provider_name == "groq":
                if not api_key:
                    return None
                return GroqProvider(
                    api_key=api_key,
                    model=self.config.ai.groq.model,
                    temperature=self.config.ai.groq.temperature,
                    max_tokens=self.config.ai.groq.max_tokens,
                )

            if provider_name == "openai":
                if not api_key:
                    return None
                base_url = self.config_manager.env.openai_base_url or None
                return OpenAIProvider(api_key=api_key, model="gpt-4o-mini", base_url=base_url)

            logger.error(f"Unsupported provider: {provider_name}")
            return None

        except AIProviderError as e:
            logger.debug(f"Provider creation failed ({provider_name}): {e}")
            return None
        except Exception as e:
            logger.exception(f"Provider creation error ({provider_name}): {e}")
            return None

    def _initialize_provider(self, provider: BaseAIProvider) -> Tuple[bool, str]:
        # Preferred: providers may implement initialize() returning bool
        if hasattr(provider, "initialize"):
            try:
                ok = bool(provider.initialize())
            except Exception as e:
                return False, str(e)

            if ok:
                return True, "initialized"

            err = getattr(provider, "error_message", None) or "Provider initialization failed"
            return False, str(err)

        # Fallback: rely on health_check
        try:
            if provider.health_check():
                return True, "healthy"
            return False, "Provider health check failed"
        except Exception as e:
            return False, str(e)

    def initialize(self, force: bool = False) -> Tuple[bool, str]:
        """Initialize the engine.

        This will:
        - attempt to initialize the configured provider
        - fall back to other providers (if configured) when initialization fails
        """

        if self._is_initialized and not force:
            return True, "Already initialized"

        self._is_initialized = False
        self._initialization_error = None

        # Fallback order: try configured first, then others.
        fallback_order = ["ollama", "gemini", "groq", "openai"]
        if self.provider_name in fallback_order:
            fallback_order.remove(self.provider_name)
        candidates = [self.provider_name] + fallback_order

        last_error = "Provider initialization failed"

        for name in candidates:
            provider = self._create_provider(name)
            if not provider:
                continue

            ok, msg = self._initialize_provider(provider)
            if ok:
                self.provider = provider
                self.provider_name = name
                self._is_initialized = True
                self._initialization_error = None

                model = getattr(provider, "model", "unknown")
                message = f"AI Engine initialized successfully using {name} ({model})"
                logger.info(message)
                return True, message

            last_error = msg

        self._initialization_error = last_error
        logger.error(f"AI Engine initialization failed: {last_error}")
        return False, last_error

    @property
    def is_ready(self) -> bool:
        if not self._is_initialized or not self.provider:
            return False

        if hasattr(self.provider, "is_available"):
            try:
                return bool(self.provider.is_available)
            except Exception:
                return False

        return True

    @property
    def status(self) -> Dict[str, Any]:
        status_info: Dict[str, Any] = {
            "initialized": self._is_initialized,
            "ready": self.is_ready,
            "provider": self.provider_name,
            "error": self._initialization_error,
        }

        if self.provider and hasattr(self.provider, "get_status"):
            try:
                status_info["provider_status"] = self.provider.get_status()
            except Exception as e:
                status_info["provider_status"] = {"error": str(e)}

        return status_info

    def get_startup_message(self) -> str:
        if self.is_ready and self.provider:
            model = getattr(self.provider, "model", "unknown")
            return f"✓ AI Ready - Using {self.provider_name.title()} ({model})"
        return f"✗ AI Not Ready - {self._initialization_error or 'Unknown error'}"

    def generate_raw(self, user_input: str) -> str:
        if not self.is_ready:
            ok, msg = self.initialize()
            if not ok:
                raise AIConnectionError(self.provider_name, message=msg)

        assert self.provider is not None
        return self.provider.generate(user_input, system_prompt=get_system_prompt())

    def process(self, user_input: str) -> ParsedResponse:
        raw = self.generate_raw(user_input)
        try:
            return ResponseParser.parse(raw)
        except Exception as e:
            logger.warning(f"Failed to parse AI response; falling back to chat: {e}")
            return ParsedResponse(action="chat", params={}, message=raw.strip(), raw_text=raw)

    def _format_provider_error(self, err: AIProviderError) -> str:
        # Add actionable hints for the most common failure modes.
        if isinstance(err, AIModelNotFoundError) and self.provider_name == "ollama":
            model = err.details.get("model", "<model>")
            return (
                f"{err}\n\n"
                "Fix:\n"
                f"  1) Run: ollama pull {model}\n"
                "  2) Ensure Ollama is running: ollama serve\n"
            )

        if isinstance(err, AIConnectionError) and self.provider_name == "ollama":
            helper = get_ollama_helper(self.config.ai.ollama.host)
            instructions = helper.get_installation_instructions() if not helper.is_installed() else ""
            return (
                f"{err}\n\n"
                "Fix:\n"
                "  1) Start Ollama: ollama serve\n"
                "  2) If you have no models: ollama pull llama3.2:1b\n"
                + (instructions if instructions else "")
            )

        if isinstance(err, AIAPIKeyError):
            return (
                f"{err}\n\n"
                "Fix:\n"
                "  - Configure the provider API key in your .env file and restart.\n"
            )

        if isinstance(err, AIResponseError) and self.provider_name == "ollama":
            return (
                f"{err}\n\n"
                "This often means Ollama is running but the configured model is missing.\n"
                "Try: ollama pull llama3.2:1b\n"
            )

        return str(err)

    def safe_process(self, user_input: str) -> ParsedResponse:
        try:
            return self.process(user_input)
        except AIProviderError as e:
            return ParsedResponse(action="chat", params={}, message=self._format_provider_error(e), raw_text=str(e))

    def process_command(self, user_input: str) -> Dict[str, Any]:
        """
        Process a user command: AI generates response, we execute it.

        Args:
            user_input: Natural language command from user

        Returns:
            Dictionary with execution results including:
            - success: bool
            - action: str
            - params: dict
            - message: str
            - executed: bool
            - result: dict (execution result from controller)
        """
        from src.controllers.controller_manager import ControllerManager

        if not self.is_ready:
            ok, message = self.initialize()
            if not ok:
                return {
                    "success": False,
                    "action": "error",
                    "params": {},
                    "message": message,
                    "executed": False,
                    "result": None
                }

        try:
            # Generate AI response
            logger.debug(f"Sending to AI: {user_input}")
            raw_response = self.generate_raw(user_input)
            logger.debug(f"AI raw response: {raw_response}")

            # Parse the response
            parsed = self.process(raw_response)
            logger.info(f"Parsed command: action={parsed.action}, params={parsed.params}")

            # If it's just chat, return without execution
            if parsed.action == "chat":
                return {
                    "success": True,
                    "action": "chat",
                    "params": {},
                    "message": parsed.message or raw_response.strip(),
                    "executed": False,
                    "result": None
                }

            # Execute the command via controller manager
            controller_manager = ControllerManager()
            result = controller_manager.execute(parsed.action, parsed.params)

            return {
                "success": result.success,
                "action": parsed.action,
                "params": parsed.params,
                "message": parsed.message or result.message,
                "executed": True,
                "result": {
                    "success": result.success,
                    "message": result.message,
                    "data": result.data
                }
            }

        except Exception as e:
            logger.exception(f"Error processing command: {e}")
            return {
                "success": False,
                "action": "error",
                "params": {},
                "message": str(e),
                "executed": False,
                "result": None
            }

    def health_check(self) -> Dict[str, Any]:
        health: Dict[str, Any] = {
            "engine_ready": self.is_ready,
            "provider": self.provider_name,
            "status": self.status,
        }

        if self.provider and hasattr(self.provider, "health_check"):
            try:
                health["provider_healthy"] = bool(self.provider.health_check())
            except Exception as e:
                health["provider_healthy"] = False
                health["provider_health_error"] = str(e)

        return health
