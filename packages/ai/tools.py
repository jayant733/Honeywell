"""AI tool definitions available to the model."""

import json
from collections.abc import Callable

from pydantic import BaseModel


class ToolRegistry:
    """Holds references to actual python functions that the LLM can call."""

    def __init__(self):
        self._tools: dict[str, Callable[..., object]] = {}

    def register(self, name: str, func: Callable[..., object]) -> None:
        self._tools[name] = func

    def execute(self, name: str, args: dict[str, object]) -> str:
        """Executes a registered tool and returns a JSON string result."""
        if name not in self._tools:
            return json.dumps({"error": f"Tool {name} is not registered or not permitted."})

        try:
            result = self._tools[name](**args)
            if isinstance(result, BaseModel):
                return result.model_dump_json()
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": str(e)})


# We define the JSON schemas that can be passed to the LLM (if using OpenAI tools format)
# However, for our structured-output-only approach, these might just be evidence sources
# fetched before the prompt, or requested dynamically.


def get_tool_schemas() -> list[dict[str, object]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "get_building_state",
                "description": "Returns the current state of the building including zone temperatures.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_forecast",
                "description": "Returns the weather forecast for the next 12 hours.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
    ]
