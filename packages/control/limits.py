"""Pure functions evaluating constraints."""

from typing import Any


class LimitChecker:
    """Evaluates individual constraints."""

    def __init__(self, config: dict[str, Any]):
        defaults = {
            "min_heating_setpoint": 16.0,
            "max_heating_setpoint": 24.0,
            "min_cooling_setpoint": 20.0,
            "max_cooling_setpoint": 30.0,
        }
        self.limits = defaults | config.get("temperature_limits", {})

    def check_cooling(self, value: float) -> float:
        """Clip cooling setpoints to configured physical bounds."""
        return min(max(value, self.limits["min_cooling_setpoint"]), self.limits["max_cooling_setpoint"])

    def check_heating(self, value: float) -> float:
        """Clip heating setpoints to configured physical bounds."""
        return max(min(value, self.limits["max_heating_setpoint"]), self.limits["min_heating_setpoint"])

    def check_overlap(self, heating: float, cooling: float) -> bool:
        """Returns True if there is a safe deadband (cooling > heating + 0.5)."""
        return cooling >= heating + 0.5
