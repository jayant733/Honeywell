"""Parsing utilities for EnergyPlus simulation data."""

from datetime import datetime, timedelta
from typing import Any

from packages.sim_adapter.contracts import TelemetryV1


class TelemetryParser:
    """Parses raw EnergyPlus API state into normalized TelemetryV1."""

    def __init__(self, api: Any, state: Any, handles: dict[str, int]):
        self.api = api
        self.state = state
        self.handles = handles

    def parse(self) -> TelemetryV1:
        """Reads variables from the EP state and builds a TelemetryV1 snapshot."""

        # Read time
        year = self.api.exchange.year(self.state)

        # EnergyPlus hours can be 24, we need to handle that for datetime
        # (Though usually we use current_time which gives elapsed hours)
        current_time_hours = self.api.exchange.current_time(self.state)

        # We can construct a roughly accurate datetime (EP year defaults to 2006 often)
        # Using a fixed year if none is provided realistically
        dt = datetime(year if year > 0 else 2024, 1, 1) + timedelta(
            days=(self.api.exchange.day_of_year(self.state) - 1), hours=current_time_hours
        )

        zone_temperatures = {}
        for key, handle in self.handles.items():
            if key.startswith("temp_"):
                zone_name = key.replace("temp_", "")
                zone_temperatures[zone_name] = self.api.exchange.get_variable_value(
                    self.state, handle
                )

        outdoor_temp = 0.0
        if "outdoor_temp" in self.handles:
            outdoor_temp = self.api.exchange.get_variable_value(
                self.state, self.handles["outdoor_temp"]
            )

        hvac_power = 0.0
        if "hvac_power" in self.handles:
            hvac_power = self.api.exchange.get_variable_value(
                self.state, self.handles["hvac_power"]
            )

        return TelemetryV1(
            timestamp=dt,
            zone_temperatures=zone_temperatures,
            outdoor_temperature=outdoor_temp,
            hvac_power=hvac_power,
        )
