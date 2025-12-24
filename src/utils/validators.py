"""Input validation utilities."""

from __future__ import annotations

from typing import Any


def validate_percentage(value: Any) -> int:
    """Coerce a value into an integer 0..100."""

    try:
        v = int(value)
    except Exception as e:
        raise ValueError("Expected an integer percentage") from e

    return max(0, min(100, v))


def non_empty_str(value: Any, field: str = "value") -> str:
    v = str(value or "").strip()
    if not v:
        raise ValueError(f"{field} must be non-empty")
    return v
