"""Controller manager.

Routes parsed AI actions to the appropriate controller.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.controllers.application_controller import ApplicationController
from src.controllers.audio_controller import AudioController
from src.controllers.base_controller import BaseController, ControllerResult
from src.controllers.clipboard_controller import ClipboardController
from src.controllers.display_controller import DisplayController
from src.controllers.file_controller import FileController
from src.controllers.input_controller import InputController
from src.controllers.media_controller import MediaController
from src.controllers.network_controller import NetworkController
from src.controllers.process_controller import ProcessController
from src.controllers.system_controller import SystemController
from src.controllers.web_controller import WebController
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ControllerManager:
    def __init__(self, controllers: Optional[List[BaseController]] = None):
        self.controllers: List[BaseController] = controllers or [
            ApplicationController(),
            FileController(),
            SystemController(),
            AudioController(),
            DisplayController(),
            InputController(),
            WebController(),
            ProcessController(),
            ClipboardController(),
            NetworkController(),
            MediaController(),
        ]

    def execute(self, action: str, params: Dict[str, Any] | None = None) -> ControllerResult:
        params = params or {}

        for controller in self.controllers:
            if controller.can_handle(action):
                logger.debug(f"Routing '{action}' to controller '{controller.name}'")
                return controller.handle(action, params)

        return ControllerResult(False, f"No controller registered for action: {action}")
