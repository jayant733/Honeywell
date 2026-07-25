"""Pure functions evaluating constraints."""

from typing import Any


class LimitChecker:
    """Evaluates individual constraints."""

    def __init__(self, config: dict[str, Any]):
        self.limits = config.get(
            "temperature_limits", {"min_cooling_setpoint": 20.0, "max_heating_setpoint": 24.0}
        )

    def check_cooling(self, value: float) -> float:
        """Returns the value clipped to the minimum cooling setpoint."""
        return max(value, self.limits["min_cooling_setpoint"])

    def check_heating(self, value: float) -> float:
        """Returns the value clipped to the maximum heating setpoint."""
        return min(value, self.limits["max_heating_setpoint"])

    def check_overlap(self, heating: float, cooling: float) -> bool:
        """Returns True if there is a safe deadband (cooling > heating + 0.5)."""
        return cooling >= heating + 0.5
