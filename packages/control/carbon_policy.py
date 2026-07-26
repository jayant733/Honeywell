"""Carbon-aware optimization policy."""

from typing import Dict, Any, List

class CarbonPolicy:
    def __init__(self, profile: Dict[str, float]):
        self.profile = profile

    def get_intensity_at(self, hour: int) -> float:
        """Returns the grid carbon intensity (gCO2/kWh) for the given hour."""
        # Simple interpolation logic for the hackathon
        if hour < 4: return 200.0
        if hour < 8: return 180.0
        if hour < 12: return 220.0
        if hour < 16: return 350.0
        if hour < 20: return 450.0
        return 280.0

    def rank_candidates(self, candidates: List[Dict[str, Any]], current_hour: int) -> List[Dict[str, Any]]:
        """
        Ranks candidates based on carbon efficiency.
        If carbon is high (>300), prioritize low-power candidates.
        If carbon is low (<200), prioritize pre-cooling candidates.
        """
        intensity = self.get_intensity_at(current_hour)
        
        def score(candidate: Dict[str, Any]) -> float:
            power = candidate.get("expected_power", 0)
            if intensity > 300:
                # Penalty for high power during dirty grid
                return -power * 2.0
            elif intensity < 200:
                # Reward for pre-cooling during clean grid
                # Assuming pre-cooling means mode=COOLING and setpoint < 22
                if candidate.get("hvac_mode") == "COOLING" and candidate.get("setpoint", 22) < 22:
                    return 100.0 - power
                return -power
            return -power
            
        return sorted(candidates, key=score, reverse=True)
