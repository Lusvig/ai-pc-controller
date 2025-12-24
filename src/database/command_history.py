"""Command history storage."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.database.db_manager import DBManager
from src.database.models import CommandHistoryRecord


class CommandHistory:
    def __init__(self, db: DBManager):
        self.db = db

    def add(
        self,
        user_input: str,
        action: str,
        success: bool,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> int:
        conn = self.db.connect()
        details_json = json.dumps(details) if details is not None else None
        cur = conn.execute(
            """
            INSERT INTO command_history (created_at, user_input, action, success, message, details_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (datetime.utcnow().isoformat(), user_input, action, int(success), message, details_json),
        )
        conn.commit()
        return int(cur.lastrowid)

    def list_recent(self, limit: int = 50) -> List[CommandHistoryRecord]:
        conn = self.db.connect()
        rows = conn.execute(
            "SELECT id, created_at, user_input, action, success, message, details_json FROM command_history ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

        results: List[CommandHistoryRecord] = []
        for r in rows:
            results.append(
                CommandHistoryRecord(
                    id=int(r["id"]),
                    created_at=datetime.fromisoformat(r["created_at"]),
                    user_input=str(r["user_input"]),
                    action=str(r["action"]),
                    success=bool(r["success"]),
                    message=str(r["message"]),
                    details_json=r["details_json"],
                )
            )
        return results
