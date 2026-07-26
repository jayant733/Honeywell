"""KPI calculations for a given run episode."""

from typing import List, Dict, Any
from packages.domain.models import BuildingStateV1

class KpiEngine:
    """Calculates aggregate metrics for a series of building states."""
    
    def __init__(self, comfort_band: tuple = (21.0, 24.0)):
        self.comfort_min, self.comfort_max = comfort_band

    def calculate_comfort_debt(self, states: List[BuildingStateV1]) -> float:
        """
        Calculates total comfort debt (°C-hours).
        Only penalizes deviations when the zone is occupied.
        Assuming states are 1-minute intervals.
        """
        debt = 0.0
        for state in states:
            for zone in state.zones:
                if zone.occupancy and zone.quality_flag != "MISSING":
                    if zone.temperature < self.comfort_min:
                        debt += (self.comfort_min - zone.temperature) / 60.0
                    elif zone.temperature > self.comfort_max:
                        debt += (zone.temperature - self.comfort_max) / 60.0
        return round(debt, 2)

    def calculate_energy(self, states: List[BuildingStateV1]) -> float:
        """
        Calculates total HVAC energy used in kWh.
        Assuming hvac_power is in Watts and states are 1-minute intervals.
        """
        total_joules = sum(state.hvac_power * 60 for state in states if state.hvac_power == state.hvac_power) # drop NaNs
        return round(total_joules / 3600000.0, 3) # J to kWh
