"""Alert Engine for evaluating building states and decisions."""

from typing import List, Dict, Any
from packages.domain.models import BuildingStateV1
from datetime import datetime, timedelta

class AlertEngine:
    def __init__(self):
        self.active_alerts = []

    def evaluate_state(self, state: BuildingStateV1) -> List[Dict[str, Any]]:
        """Evaluates a building state for temperature anomalies or stale data."""
        alerts = []
        
        for zone in state.zones:
            if zone.quality_flag == "STALE":
                alerts.append({
                    "severity": "WARNING",
                    "type": "STALE_TELEMETRY",
                    "message": f"Sensor data for {zone.zone_id} is stale.",
                    "timestamp": state.timestamp.isoformat()
                })
            
            if zone.occupancy and (zone.temperature < 18.0 or zone.temperature > 27.0):
                alerts.append({
                    "severity": "CRITICAL",
                    "type": "COMFORT_VIOLATION",
                    "message": f"Extreme comfort violation in {zone.zone_id} ({zone.temperature}°C).",
                    "timestamp": state.timestamp.isoformat()
                })
                
        return alerts

    def evaluate_decision(self, decision: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluates if the Safety Kernel rejected an AI decision."""
        if decision.get("safety_verdict") == "REJECTED":
            return [{
                "severity": "WARNING",
                "type": "AI_ACTION_REJECTED",
                "message": f"Safety Kernel rejected AI proposal for {decision.get('zone_id')}.",
                "timestamp": datetime.now().isoformat()
            }]
        return []
