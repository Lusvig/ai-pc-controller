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
        return {"open_url", "open_website", "web_search", "search_google", "open_youtube"}

    def handle(self, action: str, params: Dict[str, Any]) -> ControllerResult:
        # Normalize action names
        if action in ("open_website",):
            action = "open_url"

        if action == "open_url":
            url = str(params.get("url") or "").strip()
            if not url:
                return ControllerResult(False, "Missing url")
            # Ensure URL has protocol
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            try:
                webbrowser.open(url)
                return ControllerResult(True, f"Opened URL: {url}")
            except Exception as e:
                return ControllerResult(False, f"Failed to open URL: {e}")

        if action in ("web_search", "search_google"):
            query = str(params.get("query") or "").strip()
            if not query:
                return ControllerResult(False, "Missing query")
            url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query)
            try:
                webbrowser.open(url)
                return ControllerResult(True, f"Searching Google for: {query}", data={"url": url})
            except Exception as e:
                return ControllerResult(False, f"Failed to search: {e}")

        if action == "open_youtube":
            search = str(params.get("search") or "").strip()
            if search:
                url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(search)
            else:
                url = "https://www.youtube.com"
            try:
                webbrowser.open(url)
                if search:
                    return ControllerResult(True, f"Opening YouTube search: {search}", data={"url": url})
                else:
                    return ControllerResult(True, "Opening YouTube", data={"url": url})
            except Exception as e:
                return ControllerResult(False, f"Failed to open YouTube: {e}")

        return ControllerResult(False, f"Unsupported action: {action}")
