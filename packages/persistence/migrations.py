"""Database migrations for the Event Store."""

import contextlib
import sqlite3
from pathlib import Path


def run_migrations(db_path: Path) -> None:
    """Ensures the SQLite database has the correct schema."""
    if not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)

    with contextlib.closing(sqlite3.connect(db_path)) as conn:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    correlation_id TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
            """)
            # Create an index on correlation_id for faster retrieval of an episode
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_correlation_id ON events(correlation_id)
            """)
            # Create an index on timestamp for time-travel queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)
            """)
