"""Display control controller (brightness, resolution, monitors)."""

from __future__ import annotations

from typing import Any, Dict, Iterable

from src.controllers.base_controller import BaseController, ControllerResult


class DisplayController(BaseController):
    name = "display"

    @property
    def actions(self) -> Iterable[str]:
        return {"set_brightness"}

    def handle(self, action: str, params: Dict[str, Any]) -> ControllerResult:
        if action != "set_brightness":
            return ControllerResult(False, f"Unsupported action: {action}")

        try:
            value = int(params.get("value"))
        except Exception:
            return ControllerResult(False, "Brightness value must be an integer")

        value = max(0, min(100, value))
        return ControllerResult(True, f"Brightness set request: {value}% (not implemented)", data={"value": value})
