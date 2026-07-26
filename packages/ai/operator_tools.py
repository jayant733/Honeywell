"""Operator Assistant Tools."""

from typing import Dict, Any

class OperatorIntentParser:
    def parse_intent(self, user_message: str) -> Dict[str, Any]:
        """
        Simulates parsing natural language intent into an action proposal.
        In the real system, Qwen 14B would do this.
        """
        msg = user_message.lower()
        if "cool" in msg or "too hot" in msg:
            # Try to find zone, default to Z1
            zone = "Z2" if "conference" in msg or "z2" in msg else "Z1"
            return {
                "action_type": "HVAC_SETPOINT_UPDATE",
                "proposal": {
                    "zone_id": zone,
                    "setpoint": 20.0,
                    "hvac_mode": "COOLING"
                },
                "confidence": 0.85
            }
        elif "heat" in msg or "too cold" in msg:
            zone = "Z2" if "conference" in msg or "z2" in msg else "Z1"
            return {
                "action_type": "HVAC_SETPOINT_UPDATE",
                "proposal": {
                    "zone_id": zone,
                    "setpoint": 23.0,
                    "hvac_mode": "HEATING"
                },
                "confidence": 0.85
            }
        else:
            return {
                "action_type": "QUERY",
                "proposal": {},
                "confidence": 0.0
            }
