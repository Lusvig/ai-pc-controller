"""Ollama provider integration with automatic service management."""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from src.ai.providers.base_provider import AIProviderInfo, BaseAIProvider
from src.utils.exceptions import (
    AIConnectionError,
    AIModelNotFoundError,
    AIResponseError,
)
from src.utils.logger import get_logger
from src.utils.ollama_helper import get_ollama_helper

logger = get_logger(__name__)


class OllamaProvider(BaseAIProvider):
    """Ollama AI provider with automatic service startup and model verification."""

    info = AIProviderInfo(name="ollama", supports_streaming=False)

    def __init__(self, host: str, model: str, timeout: int = 60, **kwargs):
        super().__init__(host=host, model=model, timeout=timeout, **kwargs)
        self.host = host.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.helper = get_ollama_helper(host)

        # Track state
        self._verified_model: Optional[str] = None
        self._is_initialized = False
        self._error_message: Optional[str] = None

        logger.info(f"Ollama provider created - Host: {host}, Model: {model}")

    def initialize(self) -> bool:
        return self._initialize()

    def _initialize(self) -> bool:
        """Internal: initialize the provider if not already done."""
        if self._is_initialized:
            return True

        logger.info("Initializing Ollama provider...")
        try:
            ok, message, working_model = self.helper.ensure_ready(self.model)
            if ok and working_model:
                self._verified_model = working_model
                self._is_initialized = True
                self._error_message = None

                test_ok, test_msg = self.helper.test_generation(working_model)
                if test_ok:
                    logger.info(f"Ollama initialized successfully with model: {working_model}")
                    return True
                else:
                    logger.warning(f"Model test failed: {test_msg}")
                    self._error_message = test_msg
                    self._is_initialized = False
                    return False
            else:
                self._is_initialized = False
                self._error_message = message
                logger.error(f"Ollama initialization failed: {message}")
                return False
        except Exception as e:
            self._is_initialized = False
            self._error_message = str(e)
            logger.exception(f"Ollama initialization error: {e}")
            return False

    @property
    def is_available(self) -> bool:
        return self._is_initialized and self.helper.is_running()

    @property
    def error_message(self) -> Optional[str]:
        return self._error_message

    def get_status(self) -> Dict[str, Any]:
        return {
            "provider": "ollama",
            "is_ready": self._is_initialized,
            "is_running": self.helper.is_running(),
            "is_installed": self.helper.is_installed(),
            "model": self._verified_model or self.model,
            "host": self.host,
            "error": self._error_message,
            "installed_models": [str(m.get("name", "")) for m in self.helper.get_installed_models()],
        }

    def health_check(self) -> bool:
        # If not initialized yet, try now
        if not self._is_initialized:
            if not self._initialize():
                return False

        if not self.helper.is_running():
            return False

        model = self._verified_model or self.model
        ok, _ = self.helper.test_generation(model)
        return ok

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        # Ensure provider is ready before each request
        if not self._is_initialized:
            if not self._initialize():
                raise AIConnectionError(
                    "ollama",
                    message=self._error_message or "Ollama is not ready",
                )

        model = self._verified_model or self.model

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        logger.debug(f"Sending request to Ollama - Model: {model}")

        try:
            with httpx.Client(timeout=self.timeout) as client:
                r = client.post(f"{self.host}/api/generate", json=payload)
        except httpx.ConnectError as e:
            self._is_initialized = False
            self._error_message = "Cannot connect to Ollama. Is it running?"

            logger.warning("Connection failed, attempting to restart Ollama...")
            ok, msg = self.helper.start_service()
            if ok:
                logger.info("Ollama restarted, retrying request...")
                # Retry once
                try:
                    with httpx.Client(timeout=self.timeout) as client:
                        r = client.post(f"{self.host}/api/generate", json=payload)
                except Exception as retry_exc:
                    raise AIConnectionError("ollama", message=f"Retry failed: {retry_exc}") from retry_exc
            else:
                raise AIConnectionError("ollama", message=f"Cannot connect to Ollama at {self.host}. {msg}") from e
        except httpx.TimeoutException as e:
            raise AIResponseError("ollama", message=f"Request timed out after {self.timeout} seconds") from e
        except Exception as e:
            raise AIConnectionError("ollama", message=str(e)) from e

        if r.status_code == 404:
            self._is_initialized = False
            raise AIModelNotFoundError(model, "ollama")

        if r.status_code >= 400:
            error_text = r.text[:500] if r.text else "Unknown error"
            raise AIResponseError("ollama", response=error_text, message=f"HTTP {r.status_code}: {error_text}")

        try:
            data = r.json()
        except Exception as e:
            raise AIResponseError("ollama", response=r.text, message="Invalid JSON") from e

        if not isinstance(data, dict):
            raise AIResponseError("ollama", response=data, message="Expected JSON object")

        if "error" in data:
            raise AIResponseError("ollama", message=str(data["error"]))

        response_text = data.get("response")
        if not response_text:
            raise AIResponseError("ollama", message="Empty response from Ollama")

        logger.debug(f"Received response: {len(str(response_text))} characters")
        return str(response_text).strip()
