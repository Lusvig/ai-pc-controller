"""Settings dialog (placeholder)."""

from __future__ import annotations

from src.utils.config_manager import get_config_manager


class SettingsWindow:
    def __init__(self, parent):
        import customtkinter as ctk

        self.top = ctk.CTkToplevel(parent)
        self.top.title("Settings")
        self.top.geometry("500x400")

        cfg = get_config_manager().config
        text = ctk.CTkTextbox(self.top)
        text.pack(fill="both", expand=True)
        text.insert("end", cfg.model_dump_json(indent=2))
        text.configure(state="disabled")
