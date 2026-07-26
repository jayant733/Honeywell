"""Compares a baseline run vs an AI run."""

from typing import List, Dict, Any
from packages.domain.models import BuildingStateV1
from packages.analytics.kpis import KpiEngine

class ComparisonEngine:
    """Compares two sets of states to prove AI value."""
    
    def __init__(self):
        self.kpis = KpiEngine()

    def compare(self, baseline_states: List[BuildingStateV1], ai_states: List[BuildingStateV1]) -> Dict[str, Any]:
        """Calculates net savings and comfort changes."""
        
        base_energy = self.kpis.calculate_energy(baseline_states)
        base_comfort = self.kpis.calculate_comfort_debt(baseline_states)
        
        ai_energy = self.kpis.calculate_energy(ai_states)
        ai_comfort = self.kpis.calculate_comfort_debt(ai_states)
        
        energy_savings = base_energy - ai_energy
        energy_savings_pct = (energy_savings / base_energy * 100) if base_energy > 0 else 0
        
        return {
            "baseline": {
                "energy_kwh": base_energy,
                "comfort_debt": base_comfort
            },
            "ai": {
                "energy_kwh": ai_energy,
                "comfort_debt": ai_comfort
            },
            "savings": {
                "energy_kwh": round(energy_savings, 3),
                "energy_pct": round(energy_savings_pct, 1),
                "comfort_debt_delta": round(ai_comfort - base_comfort, 2)
            }
        }
