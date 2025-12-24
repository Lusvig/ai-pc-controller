"""Application management controller."""

from __future__ import annotations

import os
import subprocess
import sys
from typing import Any, Dict, Iterable

from src.controllers.base_controller import BaseController, ControllerResult


class ApplicationController(BaseController):
    name = "applications"

    @property
    def actions(self) -> Iterable[str]:
        return {"open_application", "close_application"}

    def handle(self, action: str, params: Dict[str, Any]) -> ControllerResult:
        if action == "open_application":
            app = str(params.get("name") or params.get("app") or "").strip()
            if not app:
                return ControllerResult(False, "Missing application name")

            try:
                if sys.platform.startswith("win"):
                    os.startfile(app)  # type: ignore[attr-defined]
                else:
                    subprocess.Popen([app])
                return ControllerResult(True, f"Opened {app}")
            except Exception as e:
                return ControllerResult(False, f"Failed to open {app}: {e}")

        if action == "close_application":
            # Closing arbitrary apps is platform-specific; return a friendly message.
            app = str(params.get("name") or params.get("app") or "").strip()
            if not app:
                return ControllerResult(False, "Missing application name")
            return ControllerResult(False, f"Close application is not implemented in this build (requested: {app})")

        return ControllerResult(False, f"Unsupported action: {action}")
