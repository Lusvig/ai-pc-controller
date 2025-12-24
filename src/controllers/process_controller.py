"""Process management controller."""

from __future__ import annotations

from typing import Any, Dict, Iterable

from src.controllers.base_controller import BaseController, ControllerResult


class ProcessController(BaseController):
    name = "process"

    @property
    def actions(self) -> Iterable[str]:
        return {"list_processes"}

    def handle(self, action: str, params: Dict[str, Any]) -> ControllerResult:
        if action != "list_processes":
            return ControllerResult(False, f"Unsupported action: {action}")

        try:
            import psutil

            names = [p.name() for p in psutil.process_iter()]
            return ControllerResult(True, f"Found {len(names)} processes", data={"processes": names[:50]})
        except Exception as e:
            return ControllerResult(False, f"Failed to list processes: {e}")
