"""Scheduled command execution (placeholder)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class ScheduledTask:
    id: str
    cron: str
    action: str
    payload: dict


class Scheduler:
    def __init__(self):
        self._scheduler = None

    def start(self) -> None:
        try:
            from apscheduler.schedulers.background import BackgroundScheduler

            self._scheduler = BackgroundScheduler()
            self._scheduler.start()
        except Exception:
            self._scheduler = None

    def shutdown(self) -> None:
        if self._scheduler:
            self._scheduler.shutdown()

    def add_interval(self, seconds: int, callback: Callable[[], None]) -> None:
        if not self._scheduler:
            return
        self._scheduler.add_job(callback, "interval", seconds=seconds)
