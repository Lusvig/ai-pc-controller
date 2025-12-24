"""Clipboard controller."""

from __future__ import annotations

from typing import Any, Dict, Iterable

from src.controllers.base_controller import BaseController, ControllerResult


class ClipboardController(BaseController):
    name = "clipboard"

    @property
    def actions(self) -> Iterable[str]:
        return {"clipboard_copy", "clipboard_paste"}

    def handle(self, action: str, params: Dict[str, Any]) -> ControllerResult:
        try:
            import pyperclip
        except Exception:
            pyperclip = None  # type: ignore

        if action == "clipboard_copy":
            text = str(params.get("text") or "")
            if not text:
                return ControllerResult(False, "Missing text")
            if pyperclip is None:
                return ControllerResult(False, "pyperclip is not available")
            pyperclip.copy(text)
            return ControllerResult(True, "Copied to clipboard")

        if action == "clipboard_paste":
            if pyperclip is None:
                return ControllerResult(False, "pyperclip is not available")
            return ControllerResult(True, "Clipboard content retrieved", data={"text": pyperclip.paste()})

        return ControllerResult(False, f"Unsupported action: {action}")
