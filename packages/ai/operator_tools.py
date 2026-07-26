"""Operator Assistant Tools."""

from typing import Dict, Any
from packages.ai.ollama_client import OllamaClient

from pathlib import Path

class OperatorIntentParser:
    def __init__(self):
        self.llm = OllamaClient(config_path=Path("d:/Hackathon/.env"))
        
    def parse_intent(self, user_message: str) -> Dict[str, Any]:
        """
        Uses local Llama3 to parse natural language into an ActionCommandV1.
        """
        prompt = f"""
You are the Sentinel Twin BMS Operator Assistant.
A user says: "{user_message}"

Extract their intent and output exactly this JSON schema:
{{
  "action_type": "HVAC_SETPOINT_UPDATE", // or "QUERY"
  "proposal": {{
    "zone_id": "Z1", // Infer zone (e.g. "conference" -> Z2, "main" -> Z1)
    "setpoint": 22.0, // Extract temperature
    "hvac_mode": "COOLING" // Infer HEATING or COOLING
  }},
  "confidence": 0.9
}}
Return ONLY valid JSON.
"""
        return self.llm.generate_json(prompt)
