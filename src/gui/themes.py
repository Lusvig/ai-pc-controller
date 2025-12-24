"""Theme definitions and helpers."""

from __future__ import annotations

from typing import Literal

from src.utils.config_manager import AppConfig


ThemeName = Literal["dark", "light", "system"]


def resolve_theme(theme: ThemeName) -> Literal["dark", "light"]:
    if theme != "system":
        return theme

    try:
        import darkdetect

        return "dark" if darkdetect.isDark() else "light"
    except Exception:
        return "dark"


def apply_theme(config: AppConfig) -> None:
    """Apply appearance mode for customtkinter if available."""

    try:
        import customtkinter as ctk

        mode = resolve_theme(config.gui.theme)
        ctk.set_appearance_mode(mode)
        ctk.set_default_color_theme("blue")
    except Exception:
        return
