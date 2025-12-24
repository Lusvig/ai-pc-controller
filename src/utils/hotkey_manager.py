"""Global hotkey management.

Uses the `keyboard` library when available.
"""

from __future__ import annotations

from typing import Callable, Dict

from src.utils.logger import get_logger

logger = get_logger(__name__)


class HotkeyManager:
    def __init__(self) -> None:
        self._registered: Dict[str, Callable[[], None]] = {}

    def register(self, hotkey: str, callback: Callable[[], None]) -> None:
        self._registered[hotkey] = callback
        try:
            import keyboard

            keyboard.add_hotkey(hotkey, callback)
            logger.info(f"Registered hotkey: {hotkey}")
        except Exception as e:
            logger.warning(f"Failed to register hotkey {hotkey}: {e}")

    def unregister_all(self) -> None:
        try:
            import keyboard

            keyboard.unhook_all_hotkeys()
        except Exception:
            pass
        self._registered.clear()
