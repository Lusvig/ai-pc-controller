"""Macro recorder (placeholder)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from time import time
from typing import Any, Dict, List


@dataclass
class MacroEvent:
    ts: float
    type: str
    payload: Dict[str, Any]


class MacroRecorder:
    def __init__(self):
        self._events: List[MacroEvent] = []
        self._recording = False

    def start(self) -> None:
        self._events = []
        self._recording = True

    def stop(self) -> List[MacroEvent]:
        self._recording = False
        return list(self._events)

    def add_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        if not self._recording:
            return
        self._events.append(MacroEvent(ts=time(), type=event_type, payload=payload))

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = [e.__dict__ for e in self._events]
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
