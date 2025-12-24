"""Wake word detection (placeholder)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WakeWordConfig:
    enabled: bool = False
    phrase: str = "hey computer"
    sensitivity: float = 0.5


class WakeWordDetector:
    def __init__(self, config: WakeWordConfig):
        self.config = config

    def start(self) -> None:
        # Placeholder: Porcupine integration would run an audio loop.
        return

    def stop(self) -> None:
        return
