"""File operations controller."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable

from src.controllers.base_controller import BaseController, ControllerResult


class FileController(BaseController):
    name = "files"

    @property
    def actions(self) -> Iterable[str]:
        return {"create_folder"}

    def handle(self, action: str, params: Dict[str, Any]) -> ControllerResult:
        if action != "create_folder":
            return ControllerResult(False, f"Unsupported action: {action}")

        path_str = str(params.get("path") or "").strip()
        name = str(params.get("name") or "").strip()

        if path_str:
            folder = Path(path_str).expanduser()
        elif name:
            folder = Path.cwd() / name
        else:
            return ControllerResult(False, "Missing folder path/name")

        try:
            folder.mkdir(parents=True, exist_ok=True)
            return ControllerResult(True, f"Created folder: {folder}", data={"path": str(folder)})
        except Exception as e:
            return ControllerResult(False, f"Failed to create folder: {e}")
