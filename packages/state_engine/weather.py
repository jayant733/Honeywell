"""Weather forecast provider."""

from typing import Dict, Any

class WeatherProvider:
    def get_forecast(self, hour: int) -> Dict[str, Any]:
        """Provides the weather forecast for the LLM to use as evidence."""
        # Mocking the forecast based on the yaml
        if hour < 12:
            return {"temp": 24.5, "humidity": 50, "condition": "CLEAR"}
        elif hour < 16:
            return {"temp": 32.0, "humidity": 45, "condition": "SUNNY"}
        elif hour < 20:
            return {"temp": 36.5, "humidity": 40, "condition": "HEATWAVE"}
        else:
            return {"temp": 28.0, "humidity": 55, "condition": "CLEAR"}
