"""Occupancy Forecaster."""

from typing import Dict

class OccupancyForecaster:
    def predict(self, hour: int, day_of_week: str) -> float:
        """Returns the predicted percentage of max occupancy [0.0 - 1.0]."""
        if day_of_week in ("Saturday", "Sunday"):
            return 0.0
            
        if hour < 8 or hour >= 18:
            return 0.0
        if 8 <= hour < 9:
            return 0.2
        if 9 <= hour < 12:
            return 0.8
        if 12 <= hour < 13:
            return 0.5 # Lunch dip
        if 13 <= hour < 17:
            return 0.9
        if 17 <= hour < 18:
            return 0.3
            
        return 0.0
