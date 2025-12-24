"""SQLite database manager."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from src.database.migrations import ensure_schema
from src.utils.exceptions import DatabaseConnectionError


class DBManager:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn

        try:
            conn = sqlite3.connect(self.db_path)
        except Exception as e:
            raise DatabaseConnectionError(str(self.db_path), str(e)) from e

        conn.row_factory = sqlite3.Row
        ensure_schema(conn)
        self._conn = conn
        return conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
