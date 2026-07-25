"""Data quality evaluation for telemetry data."""

from datetime import datetime, timedelta
from typing import Any


class QualityFlagger:
    """Evaluates telemetry data freshness and validity."""

    def __init__(self, stale_threshold_minutes: float = 15.0):
        self.stale_threshold = timedelta(minutes=stale_threshold_minutes)
        self.last_seen_times: dict[str, datetime] = {}

    def evaluate(self, zone_id: str, current_time: datetime, val: Any) -> str:
        """Returns a quality flag (VALID, STALE, MISSING) for a reading."""
        if val is None or (isinstance(val, float) and val != val):
            return "MISSING"

        previous = self.last_seen_times.get(zone_id)
        if previous is not None and current_time - previous > self.stale_threshold:
            self.last_seen_times[zone_id] = current_time
            return "STALE"

        self.last_seen_times[zone_id] = current_time
        return "VALID"
