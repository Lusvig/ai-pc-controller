"""Input area widget."""

from __future__ import annotations

from typing import Callable


def create_input_widget(parent, on_send: Callable[[str], None]):
    import customtkinter as ctk

    frame = ctk.CTkFrame(parent)

    entry = ctk.CTkEntry(frame)
    entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

    def send() -> None:
        text = entry.get().strip()
        if not text:
            return
        entry.delete(0, "end")
        on_send(text)

    button = ctk.CTkButton(frame, text="Send", command=send)
    button.pack(side="right")

    frame.entry = entry  # type: ignore[attr-defined]
    frame.send = send  # type: ignore[attr-defined]

    entry.bind("<Return>", lambda _e: send())
    return frame
