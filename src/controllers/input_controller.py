"""Keyboard and mouse input controller."""

from __future__ import annotations

from typing import Any, Dict, Iterable

from src.controllers.base_controller import BaseController, ControllerResult


class InputController(BaseController):
    name = "input"

    @property
    def actions(self) -> Iterable[str]:
        return {"type_text"}

    def handle(self, action: str, params: Dict[str, Any]) -> ControllerResult:
        if action != "type_text":
            return ControllerResult(False, f"Unsupported action: {action}")

        text = str(params.get("text") or "")
        if not text:
            return ControllerResult(False, "Missing text")

        return ControllerResult(True, "Typing request received (not executed in headless mode)", data={"text": text})
