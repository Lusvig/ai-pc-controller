"""System operations controller."""

from __future__ import annotations

import platform
import subprocess
import sys
from typing import Any, Dict, Iterable

from src.controllers.base_controller import BaseController, ControllerResult


class SystemController(BaseController):
    name = "system"

    @property
    def actions(self) -> Iterable[str]:
        return {
            "get_system_info",
            "system",
            "screenshot",
        }

    def handle(self, action: str, params: Dict[str, Any]) -> ControllerResult:
        if action == "get_system_info":
            info = {
                "platform": platform.platform(),
                "python": platform.python_version(),
                "system": platform.system(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
            }
            return ControllerResult(True, "System info retrieved", data=info)

        if action == "system":
            command = str(params.get("command", "")).lower().strip()
            return self._handle_system_command(command)

        if action == "screenshot":
            return self._handle_screenshot()

        return ControllerResult(False, f"Unsupported action: {action}")

    def _handle_system_command(self, command: str) -> ControllerResult:
        """Handle system commands like lock, shutdown, restart, sleep."""
        if not command:
            return ControllerResult(False, "Missing system command")

        if sys.platform.startswith("win"):
            if command == "lock":
                try:
                    subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
                    return ControllerResult(True, "Computer locked")
                except Exception as e:
                    return ControllerResult(False, f"Failed to lock computer: {e}")

            elif command == "shutdown":
                try:
                    subprocess.run(["shutdown", "/s", "/t", "30"], check=True)
                    return ControllerResult(True, "Shutting down in 30 seconds", data={"delay": 30})
                except Exception as e:
                    return ControllerResult(False, f"Failed to shutdown: {e}")

            elif command == "restart":
                try:
                    subprocess.run(["shutdown", "/r", "/t", "30"], check=True)
                    return ControllerResult(True, "Restarting in 30 seconds", data={"delay": 30})
                except Exception as e:
                    return ControllerResult(False, f"Failed to restart: {e}")

            elif command == "sleep":
                try:
                    subprocess.run(
                        ["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"],
                        check=True
                    )
                    return ControllerResult(True, "Computer going to sleep")
                except Exception as e:
                    return ControllerResult(False, f"Failed to sleep: {e}")

            elif command == "cancel_shutdown":
                try:
                    subprocess.run(["shutdown", "/a"], check=True)
                    return ControllerResult(True, "Shutdown cancelled")
                except Exception as e:
                    return ControllerResult(False, f"Failed to cancel shutdown: {e}")

            else:
                return ControllerResult(False, f"Unknown system command: {command}")

        elif sys.platform == "darwin":
            if command == "lock":
                return ControllerResult(True, "Lock (not implemented on macOS)")
            elif command == "shutdown":
                try:
                    subprocess.run(["shutdown", "now", "+1"], check=True)
                    return ControllerResult(True, "Shutting down")
                except Exception as e:
                    return ControllerResult(False, f"Failed to shutdown: {e}")
            elif command == "restart":
                try:
                    subprocess.run(["shutdown", "-r", "now"], check=True)
                    return ControllerResult(True, "Restarting")
                except Exception as e:
                    return ControllerResult(False, f"Failed to restart: {e}")
            elif command == "sleep":
                return ControllerResult(True, "Sleep (not implemented on macOS)")
            else:
                return ControllerResult(False, f"Unknown system command: {command}")

        else:  # Linux
            if command == "lock":
                return ControllerResult(True, "Lock (not implemented on Linux)")
            elif command == "shutdown":
                try:
                    subprocess.run(["shutdown", "now"], check=True)
                    return ControllerResult(True, "Shutting down")
                except Exception as e:
                    return ControllerResult(False, f"Failed to shutdown: {e}")
            elif command == "restart":
                try:
                    subprocess.run(["reboot"], check=True)
                    return ControllerResult(True, "Restarting")
                except Exception as e:
                    return ControllerResult(False, f"Failed to restart: {e}")
            elif command == "sleep":
                return ControllerResult(True, "Sleep (not implemented on Linux)")
            else:
                return ControllerResult(False, f"Unknown system command: {command}")

    def _handle_screenshot(self) -> ControllerResult:
        """Handle screenshot command."""
        # Try using pyautogui if available
        try:
            import pyautogui
            import os
            from datetime import datetime
            from pathlib import Path

            # Create screenshots folder
            screenshots_dir = Path.home() / "Pictures" / "Screenshots"
            screenshots_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = screenshots_dir / f"screenshot_{timestamp}.png"

            # Take screenshot
            screenshot = pyautogui.screenshot()
            screenshot.save(str(filename))

            return ControllerResult(True, f"Screenshot saved: {filename}", data={"path": str(filename)})
        except ImportError:
            return ControllerResult(False, "pyautogui not installed for screenshots")
        except Exception as e:
            return ControllerResult(False, f"Failed to take screenshot: {e}")
