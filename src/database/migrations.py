"""Database migrations.

We keep migrations minimal for the sqlite3 implementation.
"""

from __future__ import annotations

import sqlite3


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS command_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            user_input TEXT NOT NULL,
            action TEXT NOT NULL,
            success INTEGER NOT NULL,
            message TEXT NOT NULL,
            details_json TEXT
        );
        """
    )
    conn.commit()
