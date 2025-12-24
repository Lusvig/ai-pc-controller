"""Audio utilities (placeholder)."""

from __future__ import annotations

from pathlib import Path


def play_sound(path: Path) -> None:
    """Best-effort sound playback."""

    try:
        import winsound

        winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception:
        # Not available / unsupported on this platform.
        return
