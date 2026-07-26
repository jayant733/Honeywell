"""FastAPI dependency injection for Sentinel."""

from pathlib import Path
from packages.persistence.event_store import EventRepository

# In a real app, this would be a singleton initialized on startup
_DB_PATH = Path("data/sentinel.db")
_REPO = EventRepository(_DB_PATH)

def get_event_store() -> EventRepository:
    return _REPO
