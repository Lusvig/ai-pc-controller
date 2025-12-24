"""Base plugin class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict


class PluginBase(ABC):
    """Base class for plugins."""

    name: str

    @abstractmethod
    def get_commands(self) -> Dict[str, Callable[[Dict[str, Any]], Any]]:
        """Return a mapping of action -> handler."""
