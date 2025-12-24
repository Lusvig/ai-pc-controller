"""Macro player (placeholder)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from src.automation.macro_recorder import MacroEvent


class MacroPlayer:
    def load(self, path: Path) -> List[MacroEvent]:
        data = json.loads(path.read_text(encoding="utf-8"))
        return [MacroEvent(**e) for e in data]

    def play(self, events: List[MacroEvent]) -> None:
        # Placeholder: actual playback would drive controllers.
        return
