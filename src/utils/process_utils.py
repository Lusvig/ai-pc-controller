"""Process utilities."""

from __future__ import annotations

import subprocess
from typing import List, Sequence


def run_command(cmd: Sequence[str], timeout: float | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(cmd), capture_output=True, text=True, timeout=timeout, check=False)


def popen(cmd: Sequence[str]) -> subprocess.Popen[str]:
    return subprocess.Popen(list(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
