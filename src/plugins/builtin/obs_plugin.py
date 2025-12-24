"""OBS Studio control plugin (placeholder)."""

from __future__ import annotations

from typing import Any, Callable, Dict

from src.plugins.plugin_base import PluginBase


class OBSPlugin(PluginBase):
    name = "obs"

    def get_commands(self) -> Dict[str, Callable[[Dict[str, Any]], Any]]:
        return {"obs_start_recording": self.start_recording, "obs_stop_recording": self.stop_recording}

    def start_recording(self, params: Dict[str, Any]) -> str:
        return "OBS start recording requested (not implemented)"

    def stop_recording(self, params: Dict[str, Any]) -> str:
        return "OBS stop recording requested (not implemented)"
