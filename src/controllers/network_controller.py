"""Network operations controller."""

from __future__ import annotations

from typing import Any, Dict, Iterable

from src.controllers.base_controller import BaseController, ControllerResult
from src.utils.network_utils import get_network_info


class NetworkController(BaseController):
    name = "network"

    @property
    def actions(self) -> Iterable[str]:
        return {"get_ip_info", "get_network_info", "ping", "speed_test"}

    def handle(self, action: str, params: Dict[str, Any]) -> ControllerResult:
        if action == "get_ip_info":
            return self._get_ip_info()
        elif action == "get_network_info":
            return self._get_network_info()
        elif action == "ping":
            return self._ping_host(params)
        elif action == "speed_test":
            return self._speed_test()
        else:
            return ControllerResult(False, f"Unsupported action: {action}")

    def _get_ip_info(self) -> ControllerResult:
        """Get basic IP information."""
        network_info = get_network_info()
        
        data = {
            "hostname": network_info["hostname"],
            "local_ip": network_info["local_ip"],
            "all_ips": network_info["all_ips"],
            "public_ip": network_info["public_ip"],
            "internet_connected": network_info["internet_connected"]
        }
        
        return ControllerResult(True, "IP info retrieved", data=data)

    def _get_network_info(self) -> ControllerResult:
        """Get comprehensive network information."""
        network_info = get_network_info()
        return ControllerResult(True, "Network info retrieved", data=network_info)

    def _ping_host(self, params: Dict[str, Any]) -> ControllerResult:
        """Ping a host."""
        host = params.get("host", "8.8.8.8")
        count = params.get("count", 4)
        
        from src.utils.network_utils import ping_host
        result = ping_host(host, count)
        
        return ControllerResult(result["success"], result["error"] or "Ping completed", data=result)

    def _speed_test(self) -> ControllerResult:
        """Perform a speed test."""
        from src.utils.network_utils import simple_speed_test
        result = simple_speed_test()
        
        return ControllerResult(result["success"], result["error"] or "Speed test completed", data=result)
