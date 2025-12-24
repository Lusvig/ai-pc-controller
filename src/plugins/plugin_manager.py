"""Plugin loading system."""

from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from src.plugins.plugin_base import PluginBase
from src.utils.exceptions import PluginLoadError
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PluginCommand:
    plugin: str
    handler: Callable[[Dict[str, Any]], Any]


class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, PluginBase] = {}
        self.commands: Dict[str, PluginCommand] = {}

    def load_builtin(self) -> None:
        """Load built-in plugins from src.plugins.builtin."""

        try:
            import src.plugins.builtin as builtin
        except Exception as e:
            raise PluginLoadError("builtin", str(e)) from e

        for mod in pkgutil.iter_modules(builtin.__path__, builtin.__name__ + "."):
            try:
                module = importlib.import_module(mod.name)
            except Exception as e:
                logger.debug(f"Skipping plugin module {mod.name}: {e}")
                continue

            for obj in module.__dict__.values():
                if isinstance(obj, type) and issubclass(obj, PluginBase) and obj is not PluginBase:
                    try:
                        plugin = obj()  # type: ignore[call-arg]
                        self.register(plugin)
                    except Exception as e:
                        logger.warning(f"Failed loading plugin from {mod.name}: {e}")

    def register(self, plugin: PluginBase) -> None:
        self.plugins[plugin.name] = plugin
        for action, handler in plugin.get_commands().items():
            self.commands[action] = PluginCommand(plugin=plugin.name, handler=handler)

    def has_action(self, action: str) -> bool:
        return action in self.commands

    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        if action not in self.commands:
            raise KeyError(f"Unknown plugin action: {action}")
        return self.commands[action].handler(params or {})
