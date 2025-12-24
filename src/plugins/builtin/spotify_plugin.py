"""Spotify control plugin (placeholder)."""

from __future__ import annotations

from typing import Any, Callable, Dict

from src.plugins.plugin_base import PluginBase


class SpotifyPlugin(PluginBase):
    name = "spotify"

    def get_commands(self) -> Dict[str, Callable[[Dict[str, Any]], Any]]:
        return {
            "spotify_play": self.play,
            "spotify_pause": self.pause,
        }

    def play(self, params: Dict[str, Any]) -> str:
        return "Spotify play requested (not implemented)"

    def pause(self, params: Dict[str, Any]) -> str:
        return "Spotify pause requested (not implemented)"
