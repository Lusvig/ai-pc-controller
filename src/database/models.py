"""Database models (lightweight, sqlite3-based)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class CommandHistoryRecord:
    id: int
    created_at: datetime
    user_input: str
    action: str
    success: bool
    message: str
    details_json: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "user_input": self.user_input,
            "action": self.action,
            "success": self.success,
            "message": self.message,
            "details_json": self.details_json,
        }
