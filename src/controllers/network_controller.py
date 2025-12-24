"""Network operations controller."""

from __future__ import annotations

import socket
from typing import Any, Dict, Iterable

from src.controllers.base_controller import BaseController, ControllerResult


class NetworkController(BaseController):
    name = "network"

    @property
    def actions(self) -> Iterable[str]:
        return {"get_ip_info"}

    def handle(self, action: str, params: Dict[str, Any]) -> ControllerResult:
        if action != "get_ip_info":
            return ControllerResult(False, f"Unsupported action: {action}")

        hostname = socket.gethostname()
        try:
            ip = socket.gethostbyname(hostname)
        except Exception:
            ip = "unknown"

        return ControllerResult(True, "IP info retrieved", data={"hostname": hostname, "ip": ip})
