"""Unit tests for the AI integration (M5 and M6)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from packages.ai.tool_router import ToolRouter
from packages.ai.tools import ToolRegistry


def test_tool_registry():
    registry = ToolRegistry()
    registry.register("get_forecast", lambda: {"temp": 25.0})

    res = registry.execute("get_forecast", {})
    assert json.loads(res) == {"temp": 25.0}

    # Missing tool
    res_missing = registry.execute("launch_nukes", {})
    assert "error" in json.loads(res_missing)


def test_tool_router():
    registry = ToolRegistry()
    registry.register("get_building_state", lambda sensor: f"{sensor} is OK")
    router = ToolRouter(registry)

    mock_call = MagicMock()
    mock_call.id = "call_123"
    mock_call.function.name = "get_building_state"
    mock_call.function.arguments = '{"sensor": "temp_1"}'

    results = router.handle_tool_calls([mock_call])
    assert len(results) == 1
    assert results[0]["role"] == "tool"
    assert results[0]["name"] == "get_building_state"
    assert "temp_1 is OK" in results[0]["content"]
