"""Web/browser controller."""

from __future__ import annotations

import urllib.parse
import webbrowser
from typing import Any, Dict, Iterable

from src.controllers.base_controller import BaseController, ControllerResult


class WebController(BaseController):
    name = "web"

    @property
    def actions(self) -> Iterable[str]:
        return {"open_url", "web_search"}

    def handle(self, action: str, params: Dict[str, Any]) -> ControllerResult:
        if action == "open_url":
            url = str(params.get("url") or "").strip()
            if not url:
                return ControllerResult(False, "Missing url")
            try:
                webbrowser.open(url)
                return ControllerResult(True, f"Opened URL: {url}")
            except Exception as e:
                return ControllerResult(False, f"Failed to open URL: {e}")

        if action == "web_search":
            query = str(params.get("query") or "").strip()
            if not query:
                return ControllerResult(False, "Missing query")
            url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query)
            try:
                webbrowser.open(url)
                return ControllerResult(True, f"Searching Google for: {query}", data={"url": url})
            except Exception as e:
                return ControllerResult(False, f"Failed to search: {e}")

        return ControllerResult(False, f"Unsupported action: {action}")
