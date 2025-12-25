"""
Response Parser for AI PC Controller

Parses AI responses and extracts executable commands.
Handles various response formats and malformed JSON.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class ParsedResponse:
    action: str
    params: Dict[str, Any]
    message: str
    raw_text: str


class ResponseParser:
    """Parses provider output into an executable action."""

    # Valid action types (what AI returns)
    VALID_AI_ACTIONS = {
        "open_app",
        "close_app",
        "open_website",
        "search_google",
        "open_youtube",
        "volume",
        "screenshot",
        "system",
        "file_open",
        "folder_open",
        "type_text",
        "hotkey",
        "get_system_info",
        "chat",
    }

    # Mapping from AI action names to controller action names
    ACTION_MAPPING = {
        "open_app": "open_application",
        "close_app": "close_application",
        "open_website": "open_url",
        "search_google": "web_search",
        "get_system_info": "get_system_info",
        "system": "system",
        "screenshot": "screenshot",
        "volume": "volume",
    }

    _json_re = re.compile(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", re.DOTALL)

    @classmethod
    def parse(cls, text: str) -> ParsedResponse:
        """Parse AI response text into a structured response."""
        raw_text = text or ""
        original_text = raw_text.strip()

        if not original_text:
            return ParsedResponse(
                action="chat", params={}, message="I'm not sure what you mean. Try saying 'open notepad' or 'search google for weather'.",
                raw_text=raw_text
            )

        # Strategy 1: Try direct JSON parse
        if original_text.startswith("{"):
            result = cls._try_direct_json(original_text, raw_text)
            if result:
                return result

        # Strategy 2: Extract JSON from text (markdown, code blocks, etc.)
        result = cls._try_extract_json(original_text, raw_text)
        if result:
            return result

        # Strategy 3: Try to fix common JSON issues
        result = cls._try_fix_json(original_text, raw_text)
        if result:
            return result

        # Strategy 4: Pattern matching for common commands
        result = cls._try_pattern_match(original_text)
        if result:
            return result

        # Fallback: treat as conversational response
        logger.debug(f"Falling back to chat for: {original_text[:100]}")
        return ParsedResponse(
            action="chat", params={}, message=original_text.strip(), raw_text=raw_text
        )

    @classmethod
    def _try_direct_json(cls, text: str, raw_text: str) -> Optional[ParsedResponse]:
        """Try to parse response as direct JSON."""
        try:
            data = json.loads(text)
            return cls._format_response(data, raw_text)
        except json.JSONDecodeError:
            return None

    @classmethod
    def _try_extract_json(cls, text: str, raw_text: str) -> Optional[ParsedResponse]:
        """Try to extract JSON from text that might contain other content."""

        # Remove markdown code blocks first
        cleaned = re.sub(r'```json?\s*', '', text)
        cleaned = re.sub(r'```\s*', '', cleaned)

        # Look for JSON object pattern
        matches = cls._json_re.findall(cleaned)
        for match in matches:
            try:
                data = json.loads(match)
                if isinstance(data, dict) and "action" in data:
                    return cls._format_response(data, raw_text)
            except json.JSONDecodeError:
                continue

        # If cleaned text starts with {, try it as-is
        if cleaned.startswith("{"):
            try:
                data = json.loads(cleaned)
                return cls._format_response(data, raw_text)
            except json.JSONDecodeError:
                pass

        return None

    @classmethod
    def _try_fix_json(cls, text: str, raw_text: str) -> Optional[ParsedResponse]:
        """Try to fix common JSON formatting issues."""
        fixed = text

        # Remove markdown code block markers
        fixed = re.sub(r'^```json?\s*', '', fixed)
        fixed = re.sub(r'\s*```$', '', fixed)

        # Remove leading text before the first {
        first_brace = fixed.find("{")
        if first_brace > 0:
            fixed = fixed[first_brace:]

        # Find the matching closing brace for the first opening brace
        if fixed.startswith("{"):
            open_count = 0
            in_string = False
            escape_next = False
            end_pos = -1

            for i, char in enumerate(fixed):
                if escape_next:
                    escape_next = False
                    continue
                if char == "\\":
                    escape_next = True
                    continue
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                if not in_string:
                    if char == "{":
                        open_count += 1
                    elif char == "}":
                        open_count -= 1
                        if open_count == 0:
                            end_pos = i + 1
                            break

            if end_pos > 0:
                fixed = fixed[:end_pos]

                try:
                    data = json.loads(fixed)
                    return cls._format_response(data, raw_text)
                except json.JSONDecodeError:
                    pass

            # If no complete JSON found, try to construct one from common patterns
            # For cases like {"action":"open_app","params":{"name":"notepad"
            # where the closing is missing
            if open_count > 0:
                # Try adding closing braces
                fixed_with_braces = fixed + "}" * open_count
                try:
                    data = json.loads(fixed_with_braces)
                    return cls._format_response(data, raw_text)
                except json.JSONDecodeError:
                    pass

        return None

    @classmethod
    def _try_pattern_match(cls, text: str) -> Optional[ParsedResponse]:
        """Try to match response against known patterns for common commands."""

        text_lower = text.lower()

        # Opening patterns
        open_match = re.search(
            r"(?:i'?m |i am |i will |)open(?:ing|ed|)?\s+(?:the\s+)?(\w+)",
            text_lower
        )
        if open_match:
            app_name = open_match.group(1)
            return ParsedResponse(
                action="open_app",
                params={"name": app_name},
                message=f"Opening {app_name}",
                raw_text=text
            )

        # Closing patterns
        close_match = re.search(
            r"clos(?:ing|ed|e)?\s+(?:the\s+)?(\w+)",
            text_lower
        )
        if close_match:
            app_name = close_match.group(1)
            return ParsedResponse(
                action="close_app",
                params={"name": app_name},
                message=f"Closing {app_name}",
                raw_text=text
            )

        # Volume patterns
        if "mute" in text_lower:
            return ParsedResponse(
                action="volume",
                params={"level": "mute"},
                message="Muting volume",
                raw_text=text
            )

        if re.search(r"volume\s+(up|down)", text_lower):
            level = "up" if "up" in text_lower else "down"
            return ParsedResponse(
                action="volume",
                params={"level": level},
                message=f"Turning volume {level}",
                raw_text=text
            )

        # Screenshot patterns
        if re.search(r"screenshot|capture\s*(?:the\s*)?screen", text_lower):
            return ParsedResponse(
                action="screenshot",
                params={},
                message="Taking screenshot",
                raw_text=text
            )

        # Lock computer patterns
        if re.search(r"lock\s*(?:the\s*)?(computer|pc|screen)?", text_lower):
            return ParsedResponse(
                action="system",
                params={"command": "lock"},
                message="Locking computer",
                raw_text=text
            )

        # Shutdown patterns
        if re.search(r"shut\s*down", text_lower):
            return ParsedResponse(
                action="system",
                params={"command": "shutdown"},
                message="Shutting down",
                raw_text=text
            )

        # Restart patterns
        if re.search(r"restart", text_lower):
            return ParsedResponse(
                action="system",
                params={"command": "restart"},
                message="Restarting",
                raw_text=text
            )

        return None

    @classmethod
    def _format_response(cls, data: Dict, raw_text: str) -> ParsedResponse:
        """Validate and format parsed JSON data."""

        if not isinstance(data, dict):
            return ParsedResponse(
                action="chat", params={}, message=raw_text.strip(), raw_text=raw_text
            )

        action = str(data.get("action", "")).strip().lower()

        if not action:
            return ParsedResponse(
                action="chat", params={}, message=raw_text.strip(), raw_text=raw_text
            )

        # Normalize action names
        normalized = cls.ACTION_MAPPING.get(action, action)

        # Validate action
        if normalized not in cls.VALID_AI_ACTIONS and normalized not in cls.ACTION_MAPPING.values():
            # If it's an unknown action, treat as chat
            logger.debug(f"Unknown action '{action}', treating as chat")
            return ParsedResponse(
                action="chat",
                params={},
                message=data.get("message", data.get("response", raw_text.strip())),
                raw_text=raw_text
            )

        # Get params
        params = data.get("params", {})
        if not isinstance(params, dict):
            params = {}

        # Get message
        message = data.get("message", data.get("response", ""))
        if not isinstance(message, str):
            message = str(message)

        return ParsedResponse(
            action=normalized,
            params=params,
            message=message,
            raw_text=raw_text
        )
