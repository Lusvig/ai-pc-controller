"""System operations controller."""

from __future__ import annotations

import platform
from typing import Any, Dict, Iterable

from src.controllers.base_controller import BaseController, ControllerResult


class SystemController(BaseController):
    name = "system"

    @property
    def actions(self) -> Iterable[str]:
        return {"get_system_info"}

    def handle(self, action: str, params: Dict[str, Any]) -> ControllerResult:
        if action != "get_system_info":
            return ControllerResult(False, f"Unsupported action: {action}")

        info = {
            "platform": platform.platform(),
            "python": platform.python_version(),
        }
        return ControllerResult(True, "System info retrieved", data=info)
