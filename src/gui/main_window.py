"""Main application window."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

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
    def __init__(self, ai_engine: Optional[AIEngine] = None):
        import customtkinter as ctk

        cfg = get_config_manager().config
        apply_theme(cfg)

        self.app = ctk.CTk()
        self.app.title("AI PC Controller")
        self.app.geometry(f"{cfg.gui.window.width}x{cfg.gui.window.height}")

        self.engine = ai_engine or AIEngine(config=cfg)
        self.controllers = ControllerManager()

        self.chat = create_chat_widget(self.app)
        self.chat.pack(fill="both", expand=True, padx=12, pady=12)

        self.input = create_input_widget(self.app, self.on_user_message)
        self.input.pack(fill="x", padx=12, pady=(0, 12))

        menubar = ctk.CTkFrame(self.app)
        menubar.pack(fill="x", padx=12, pady=(12, 0))

        status_btn = ctk.CTkButton(menubar, text="AI Status", command=self.open_ai_status)
        status_btn.pack(side="left")

        retry_btn = ctk.CTkButton(menubar, text="Retry AI", command=self.retry_ai)
        retry_btn.pack(side="left", padx=(8, 0))

        settings_btn = ctk.CTkButton(menubar, text="Settings", command=self.open_settings)
        settings_btn.pack(side="right")

        self.append("system", "Initializing AI...")
        ok, msg = self.engine.initialize()
        self.append("system", self.engine.get_startup_message())
        if not ok:
            self.append("system", "AI is not ready. Use 'Retry AI' or open 'AI Status' for details.")

    def append(self, role: str, content: str) -> None:
        msg = ChatMessage(role=role, content=content, ts=datetime.now())
        self.chat.append_message(msg)  # type: ignore[attr-defined]

    def retry_ai(self) -> None:
        self.append("system", "Retrying AI initialization...")
        ok, msg = self.engine.initialize(force=True)
        if ok:
            self.append("system", self.engine.get_startup_message())
        else:
            self.append("system", f"AI still not ready: {msg}")

    def open_ai_status(self) -> None:
        import customtkinter as ctk

        top = ctk.CTkToplevel(self.app)
        top.title("AI Status")
        top.geometry("650x500")

        btn_row = ctk.CTkFrame(top)
        btn_row.pack(fill="x", padx=12, pady=(12, 6))

        def refresh_text(text_widget: "ctk.CTkTextbox") -> None:
            data = {
                "startup_message": self.engine.get_startup_message(),
                "status": self.engine.status,
                "health": self.engine.health_check(),
            }
            text_widget.configure(state="normal")
            text_widget.delete("1.0", "end")
            text_widget.insert("end", json.dumps(data, indent=2))
            text_widget.configure(state="disabled")

        text = ctk.CTkTextbox(top)
        text.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        refresh_btn = ctk.CTkButton(btn_row, text="Refresh", command=lambda: refresh_text(text))
        refresh_btn.pack(side="left")

        retry_btn = ctk.CTkButton(btn_row, text="Retry Connection", command=lambda: (self.retry_ai(), refresh_text(text)))
        retry_btn.pack(side="left", padx=(8, 0))

        close_btn = ctk.CTkButton(btn_row, text="Close", command=top.destroy)
        close_btn.pack(side="right")

        refresh_text(text)

    def on_user_message(self, text: str) -> None:
        self.append("user", text)
        parsed = self.engine.safe_process(text)

        if parsed.action == "chat":
            self.append("ai", parsed.message or parsed.raw_text)
            if not self.engine.is_ready:
                self.append("system", "Tip: Click 'Retry AI' if the AI connection failed.")
            return

        result = self.controllers.execute(parsed.action, parsed.params)
        if parsed.message:
            self.append("ai", parsed.message)
        self.append("system", result.message)

    def open_settings(self) -> None:
        SettingsWindow(self.app)

    def run(self) -> None:
        self.app.mainloop()


def run_app(ai_engine: Optional[AIEngine] = None) -> None:
    win = MainWindow(ai_engine=ai_engine)
    win.run()
