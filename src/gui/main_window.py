"""Main application window."""

from __future__ import annotations

from datetime import datetime

from src.ai.ai_engine import AIEngine
from src.controllers.controller_manager import ControllerManager
from src.gui.chat_widget import ChatMessage, create_chat_widget
from src.gui.input_widget import create_input_widget
from src.gui.settings_window import SettingsWindow
from src.gui.themes import apply_theme
from src.utils.config_manager import get_config_manager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow:
    def __init__(self):
        import customtkinter as ctk

        cfg = get_config_manager().config
        apply_theme(cfg)

        self.app = ctk.CTk()
        self.app.title("AI PC Controller")
        self.app.geometry(f"{cfg.gui.window.width}x{cfg.gui.window.height}")

        self.engine = AIEngine(config=cfg)
        self.controllers = ControllerManager()

        self.chat = create_chat_widget(self.app)
        self.chat.pack(fill="both", expand=True, padx=12, pady=12)

        self.input = create_input_widget(self.app, self.on_user_message)
        self.input.pack(fill="x", padx=12, pady=(0, 12))

        menubar = ctk.CTkFrame(self.app)
        menubar.pack(fill="x", padx=12, pady=(12, 0))
        settings_btn = ctk.CTkButton(menubar, text="Settings", command=self.open_settings)
        settings_btn.pack(side="right")

        self.append("system", "Ready.")

    def append(self, role: str, content: str) -> None:
        msg = ChatMessage(role=role, content=content, ts=datetime.now())
        self.chat.append_message(msg)  # type: ignore[attr-defined]

    def on_user_message(self, text: str) -> None:
        self.append("user", text)
        parsed = self.engine.safe_process(text)

        if parsed.action == "chat":
            self.append("ai", parsed.message or parsed.raw_text)
            return

        result = self.controllers.execute(parsed.action, parsed.params)
        if parsed.message:
            self.append("ai", parsed.message)
        self.append("system", result.message)

    def open_settings(self) -> None:
        SettingsWindow(self.app)

    def run(self) -> None:
        self.app.mainloop()


def run_app() -> None:
    win = MainWindow()
    win.run()
