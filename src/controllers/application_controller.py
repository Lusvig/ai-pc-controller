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
        return {
            "open_application", "open_app",
            "close_application", "close_app"
        }

    def handle(self, action: str, params: Dict[str, Any]) -> ControllerResult:
        app = str(params.get("name") or params.get("app") or "").strip()
        if not app:
            return ControllerResult(False, "Missing application name")

        if action in ("open_application", "open_app"):
            try:
                # First try to find known apps by name
                app_lower = app.lower()

                # Map common app names to executable names
                app_executables = {
                    "notepad": "notepad.exe",
                    "word": "WINWORD.EXE",
                    "excel": "EXCEL.EXE",
                    "powerpoint": "POWERPNT.EXE",
                    "chrome": "chrome.exe",
                    "firefox": "firefox.exe",
                    "edge": "msedge.exe",
                    "vscode": "Code.exe",
                    "code": "Code.exe",
                    "calculator": "calc.exe",
                    "explorer": "explorer.exe",
                    "cmd": "cmd.exe",
                    "powershell": "powershell.exe",
                    "spotify": "Spotify.exe",
                    "discord": "Discord.exe",
                    "steam": "steam.exe",
                }

                executable = app_executables.get(app_lower, app)

                if sys.platform.startswith("win"):
                    # Try using os.startfile first (works for registered apps)
                    try:
                        os.startfile(app)  # type: ignore[attr-defined]
                        return ControllerResult(True, f"Opened {app}")
                    except Exception:
                        pass

                    # Try running the executable directly
                    try:
                        subprocess.Popen(
                            [executable],
                            shell=False,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        return ControllerResult(True, f"Opened {app}")
                    except FileNotFoundError:
                        pass

                    # Try with shell execute
                    try:
                        subprocess.Popen(
                            f'start "" "{app}"',
                            shell=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        return ControllerResult(True, f"Opened {app}")
                    except Exception:
                        pass

                else:
                    subprocess.Popen([app])

                return ControllerResult(False, f"Could not find or open: {app}")
            except Exception as e:
                return ControllerResult(False, f"Failed to open {app}: {e}")

        if action in ("close_application", "close_app"):
            try:
                # Map common app names to process names
                process_names = {
                    "notepad": "notepad.exe",
                    "word": "WINWORD.EXE",
                    "excel": "EXCEL.EXE",
                    "powerpoint": "POWERPNT.EXE",
                    "chrome": "chrome.exe",
                    "firefox": "firefox.exe",
                    "edge": "msedge.exe",
                    "vscode": "Code.exe",
                    "code": "Code.exe",
                    "calculator": "Calculator.exe",
                    "explorer": "explorer.exe",
                    "cmd": "cmd.exe",
                    "powershell": "powershell.exe",
                    "spotify": "Spotify.exe",
                    "discord": "Discord.exe",
                    "steam": "steam.exe",
                }

                process_name = process_names.get(app.lower(), f"{app}.exe")

                if sys.platform.startswith("win"):
                    # Try taskkill
                    result = subprocess.run(
                        ["taskkill", "/IM", process_name, "/F"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        return ControllerResult(True, f"Closed {app}")
                    else:
                        return ControllerResult(False, f"Could not close {app}")
                else:
                    return ControllerResult(False, f"Close application not implemented for {sys.platform}")

            except Exception as e:
                return ControllerResult(False, f"Failed to close {app}: {e}")

        return ControllerResult(False, f"Unsupported action: {action}")
