"""Audio control controller.

Most audio control operations are Windows-specific. This controller provides
portable stubs and can be extended with pycaw on Windows.
"""

from __future__ import annotations

import sys
from typing import Any, Dict, Iterable

from src.controllers.base_controller import BaseController, ControllerResult

# Try to import platform-specific audio control
PYCAW_AVAILABLE = False
try:
    if sys.platform.startswith("win"):
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        from ctypes import cast, POINTER
        PYCAW_AVAILABLE = True
except ImportError:
    pass


class AudioController(BaseController):
    name = "audio"

    @property
    def actions(self) -> Iterable[str]:
        return {"volume", "set_volume"}

    def handle(self, action: str, params: Dict[str, Any]) -> ControllerResult:
        level = params.get("level", "up")

        # Handle string levels
        if isinstance(level, str):
            level = level.lower().strip()
            if level in ("up", "increase"):
                return self._volume_up()
            elif level in ("down", "decrease"):
                return self._volume_down()
            elif level == "mute":
                return self._volume_mute()
            else:
                # Try to parse as number
                try:
                    level = int(level)
                except ValueError:
                    return ControllerResult(False, f"Unknown volume level: {level}")

        # Handle numeric level
        if isinstance(level, (int, float)):
            return self._set_volume(level)

        return ControllerResult(False, f"Unknown volume action: {action}")

    def _volume_up(self) -> ControllerResult:
        """Increase volume by 10%."""
        if PYCAW_AVAILABLE:
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_,
                    CLSCTX_ALL,
                    None
                )
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                current = volume.GetMasterVolumeLevelScalar()
                new_level = min(1.0, current + 0.1)
                volume.SetMasterVolumeLevelScalar(new_level, None)
                return ControllerResult(True, "Volume increased", data={"level": int(new_level * 100)})
            except Exception as e:
                return ControllerResult(False, f"Failed to increase volume: {e}")

        return ControllerResult(True, "Volume up (not implemented)")

    def _volume_down(self) -> ControllerResult:
        """Decrease volume by 10%."""
        if PYCAW_AVAILABLE:
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_,
                    CLSCTX_ALL,
                    None
                )
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                current = volume.GetMasterVolumeLevelScalar()
                new_level = max(0.0, current - 0.1)
                volume.SetMasterVolumeLevelScalar(new_level, None)
                return ControllerResult(True, "Volume decreased", data={"level": int(new_level * 100)})
            except Exception as e:
                return ControllerResult(False, f"Failed to decrease volume: {e}")

        return ControllerResult(True, "Volume down (not implemented)")

    def _volume_mute(self) -> ControllerResult:
        """Toggle mute."""
        if PYCAW_AVAILABLE:
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_,
                    CLSCTX_ALL,
                    None
                )
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                is_muted = volume.GetMute()
                volume.SetMute(not is_muted, None)
                return ControllerResult(True, "Mute toggled", data={"muted": not is_muted})
            except Exception as e:
                return ControllerResult(False, f"Failed to toggle mute: {e}")

        return ControllerResult(True, "Mute toggled (not implemented)")

    def _set_volume(self, level: int) -> ControllerResult:
        """Set volume to a specific level (0-100)."""
        level = max(0, min(100, level))

        if PYCAW_AVAILABLE:
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_,
                    CLSCTX_ALL,
                    None
                )
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMasterVolumeLevelScalar(level / 100.0, None)
                return ControllerResult(True, f"Volume set to {level}%", data={"level": level})
            except Exception as e:
                return ControllerResult(False, f"Failed to set volume: {e}")

        return ControllerResult(True, f"Volume set to {level}% (not implemented)", data={"level": level})
