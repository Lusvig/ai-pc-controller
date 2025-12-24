"""Chat display widget."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str
    ts: datetime


def create_chat_widget(parent):
    """Factory to create the chat widget.

    Implemented as a factory to avoid importing GUI dependencies at module import time.
    """

    import customtkinter as ctk

    textbox = ctk.CTkTextbox(parent, wrap="word")
    textbox.configure(state="disabled")

    def append(message: ChatMessage) -> None:
        textbox.configure(state="normal")
        line = f"[{message.ts.strftime('%H:%M:%S')}] {message.role}: {message.content}\n"
        textbox.insert("end", line)
        textbox.see("end")
        textbox.configure(state="disabled")

    textbox.append_message = append  # type: ignore[attr-defined]
    return textbox
