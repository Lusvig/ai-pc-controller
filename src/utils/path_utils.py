"""Path handling utilities."""

from __future__ import annotations

import os
from pathlib import Path


def expand_path(path: str) -> Path:
    """Expand user (~) and environment variables (%VAR% / $VAR) into a Path."""

    expanded = os.path.expandvars(os.path.expanduser(path))
    return Path(expanded)
