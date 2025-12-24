"""System tray functionality (best-effort)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional


@dataclass
class TrayConfig:
    icon_path: Optional[Path] = None


class SystemTray:
    def __init__(self, on_show: Callable[[], None], on_quit: Callable[[], None], config: TrayConfig | None = None):
        self.on_show = on_show
        self.on_quit = on_quit
        self.config = config or TrayConfig()
        self._icon = None

    def start(self) -> None:
        try:
            import pystray
            from PIL import Image

            icon_img = None
            if self.config.icon_path and self.config.icon_path.exists():
                try:
                    icon_img = Image.open(self.config.icon_path)
                except Exception:
                    icon_img = None

            if icon_img is None:
                icon_img = Image.new("RGB", (64, 64), color=(15, 52, 96))

            menu = pystray.Menu(
                pystray.MenuItem("Show", lambda: self.on_show()),
                pystray.MenuItem("Quit", lambda: self.on_quit()),
            )
            self._icon = pystray.Icon("ai-pc-controller", icon_img, "AI PC Controller", menu)
            self._icon.run_detached()
        except Exception:
            self._icon = None

    def stop(self) -> None:
        try:
            if self._icon:
                self._icon.stop()
        except Exception:
            pass
