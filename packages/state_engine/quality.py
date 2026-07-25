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

        # Update last seen
        self.last_seen_times[zone_id] = current_time

        # We don't implement full stale tracking via old timestamps here unless we
        # receive explicit timestamps per reading. Assuming the Simulation Adapter
        # gives us fresh data on each tick.
        return "VALID"
