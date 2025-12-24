"""AI response parsing logic."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.utils.exceptions import CommandParseError


@dataclass(frozen=True)
class ParsedResponse:
    action: str
    params: Dict[str, Any]
    message: str
    raw_text: str


class ResponseParser:
    """Parses provider output into an executable action."""

    _json_re = re.compile(r"\{.*\}", re.DOTALL)

    @classmethod
    def parse(cls, text: str) -> ParsedResponse:
        raw_text = text or ""
        candidate = raw_text.strip()

        # Some models might accidentally wrap JSON in extra text. Extract the first {...} blob.
        if not candidate.startswith("{") or not candidate.endswith("}"):
            m = cls._json_re.search(candidate)
            if m:
                candidate = m.group(0).strip()

        try:
            data = json.loads(candidate)
        except Exception as e:
            # Fallback: treat as chat.
            return ParsedResponse(action="chat", params={}, message=raw_text.strip(), raw_text=raw_text)

        if not isinstance(data, dict) or not data.get("action"):
            raise CommandParseError(raw_text, reason="Missing 'action' field")

        action = str(data.get("action"))
        params = data.get("params")
        if params is None:
            params = {}
        if not isinstance(params, dict):
            raise CommandParseError(raw_text, reason="'params' must be an object")

        message = data.get("message")
        if message is None:
            message = ""

        return ParsedResponse(action=action, params=params, message=str(message), raw_text=raw_text)
