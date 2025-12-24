"""Windows-specific utilities.

This module should not import Windows-only dependencies at import time.
"""

from __future__ import annotations

import sys


def is_windows() -> bool:
    return sys.platform.startswith("win")


def require_windows(feature: str) -> None:
    if not is_windows():
        raise NotImplementedError(f"{feature} is only supported on Windows")
