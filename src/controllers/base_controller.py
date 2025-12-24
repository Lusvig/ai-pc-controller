"""Abstract base controller."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Iterable


@dataclass(frozen=True)
class ControllerResult:
    success: bool
    message: str
    data: Dict[str, Any] | None = None


class BaseController(ABC):
    """Base interface for all controllers."""

    name: str

    @property
    @abstractmethod
    def actions(self) -> Iterable[str]:
        """Actions supported by this controller."""

    def can_handle(self, action: str) -> bool:
        return action in set(self.actions)

    @abstractmethod
    def handle(self, action: str, params: Dict[str, Any]) -> ControllerResult:
        """Handle an action with params."""
