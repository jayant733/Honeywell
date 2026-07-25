"""Episodic memory retrieval for the AI."""

from typing import Any

from packages.persistence.event_store import EventRepository


class MemoryRetriever:
    """Retrieves relevant past decisions to provide context to the AI."""

    def __init__(self, repository: EventRepository):
        self.repo = repository

    def find_similar_episodes(self, current_state: Any) -> list[dict[str, Any]]:
        """
        Return bounded, auditable prior decisions. Similarity scoring is deliberately
        deferred until a validated feature store exists.
        """
        del current_state
        return self.repo.recent_events("DECISION", limit=5)
