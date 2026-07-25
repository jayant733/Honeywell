"""Event Repository for storing and retrieving decisions."""

import contextlib
import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from packages.persistence.migrations import run_migrations


class EventRepository:
    """Stores all system events into SQLite for audit and replay."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        run_migrations(db_path)

    def append(self, event_type: str, correlation_id: str, payload: Any) -> str:
        """Appends an event and returns its ID."""
        event_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        # We rely on Pydantic models being dumped, or just dicts.
        if hasattr(payload, "model_dump_json"):
            payload_str = payload.model_dump_json()
        elif hasattr(payload, "to_json"):
            payload_str = payload.to_json()
        elif isinstance(payload, str):
            payload_str = payload
        else:
            payload_str = json.dumps(payload, default=str)

        with contextlib.closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                conn.execute(
                    "INSERT INTO events (id, timestamp, event_type, correlation_id, payload) VALUES (?, ?, ?, ?, ?)",
                    (event_id, timestamp, event_type, correlation_id, payload_str),
                )

        return event_id

    def get_episode(self, correlation_id: str) -> list[dict[str, Any]]:
        """Retrieves all events for a single decision cycle."""
        with contextlib.closing(sqlite3.connect(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM events WHERE correlation_id = ? ORDER BY timestamp ASC",
                (correlation_id,),
            ).fetchall()

        return [dict(row) for row in rows]

    def recent_events(self, event_type: str, limit: int = 5) -> list[dict[str, Any]]:
        """Return bounded recent history for episodic retrieval."""
        with contextlib.closing(sqlite3.connect(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM events WHERE event_type = ? ORDER BY timestamp DESC LIMIT ?",
                (event_type, limit),
            ).fetchall()
        return [dict(row) for row in rows]
