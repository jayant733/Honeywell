"""Tests for Event Store."""

import tempfile
from pathlib import Path

from packages.persistence.event_store import EventRepository


def test_event_store():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        repo = EventRepository(db_path)

        repo.append("TEST_EVENT", "corr_123", {"key": "value"})

        episode = repo.get_episode("corr_123")
        assert len(episode) == 1
        assert episode[0]["event_type"] == "TEST_EVENT"
        assert '"key": "value"' in episode[0]["payload"]
