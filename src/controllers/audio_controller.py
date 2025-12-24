"""Audio control controller.

Most audio control operations are Windows-specific. This controller provides
portable stubs and can be extended with pycaw on Windows.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable

from src.controllers.base_controller import BaseController, ControllerResult


class AudioController(BaseController):
    name = "audio"

    @property
    def actions(self) -> Iterable[str]:
        return {"set_volume"}

    def handle(self, action: str, params: Dict[str, Any]) -> ControllerResult:
        if action != "set_volume":
            return ControllerResult(False, f"Unsupported action: {action}")

        level = params.get("level")
        try:
            level_int = int(level)
        except Exception:
            return ControllerResult(False, "Volume level must be an integer")

        level_int = max(0, min(100, level_int))
        return ControllerResult(True, f"Volume set request: {level_int}% (not implemented)", data={"level": level_int})
