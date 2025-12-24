"""Security utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class SafetyPolicy:
    confirm_commands: set[str]
    blocked_commands: set[str]

    def is_blocked(self, action: str) -> bool:
        return action in self.blocked_commands

    def requires_confirmation(self, action: str) -> bool:
        return action in self.confirm_commands


def default_policy(confirm_commands: Iterable[str] = (), blocked_commands: Iterable[str] = ()) -> SafetyPolicy:
    return SafetyPolicy(confirm_commands=set(confirm_commands), blocked_commands=set(blocked_commands))
