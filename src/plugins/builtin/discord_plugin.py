"""Discord control plugin (placeholder)."""

from __future__ import annotations

from typing import Any, Callable, Dict

from src.plugins.plugin_base import PluginBase


class DiscordPlugin(PluginBase):
    name = "discord"

    def get_commands(self) -> Dict[str, Callable[[Dict[str, Any]], Any]]:
        return {"discord_status": self.set_status}

    def set_status(self, params: Dict[str, Any]) -> str:
        status = params.get("status")
        return f"Discord status requested: {status} (not implemented)"
