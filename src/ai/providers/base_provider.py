"""Base class for AI providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from src.utils.exceptions import AIConnectionError, AIResponseError


@dataclass(frozen=True)
class AIProviderInfo:
    name: str
    supports_streaming: bool = False


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""

    info: AIProviderInfo

    def __init__(self, **kwargs: Any) -> None:
        self._kwargs = kwargs

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a model response for a prompt."""

    def health_check(self) -> bool:
        return True

    def _connection_error(self, message: str | None = None) -> AIConnectionError:
        return AIConnectionError(self.info.name, message=message)

    def _response_error(self, response: Any, message: str | None = None) -> AIResponseError:
        return AIResponseError(self.info.name, response=response, message=message)
