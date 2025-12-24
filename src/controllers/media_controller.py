"""Media playback controller."""

from __future__ import annotations

from typing import Any, Dict, Iterable

from src.controllers.base_controller import BaseController, ControllerResult


class MediaController(BaseController):
    name = "media"

    @property
    def actions(self) -> Iterable[str]:
        return {"media_play", "media_pause", "media_next", "media_prev"}

    def handle(self, action: str, params: Dict[str, Any]) -> ControllerResult:
        return ControllerResult(True, f"Media action received: {action} (not implemented)")
