"""MCP Server exposing building tools to local LLMs."""

import json
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

# Initialize the MCP Server
mcp = FastMCP("Sentinel Twin")

@mcp.tool()
def get_building_state() -> str:
    """Returns the current state of the building including zone temperatures and occupancy."""
    # In a real live system, this reads from shared memory or DB
    # For now, we mock the retrieval since the actual state is held by the PyEnergyPlus runtime
    return json.dumps({
        "status": "success",
        "message": "State will be injected live by the orchestrator."
    })

@mcp.tool()
def get_forecast() -> str:
    """Returns the weather forecast and carbon intensity."""
    return json.dumps({
        "status": "success",
        "carbon_intensity": "moderate (320 gCO2/kWh)"
    })

@mcp.tool()
def execute_setpoint(zone_id: str, temperature: float) -> str:
    """Proposes a setpoint for a specific zone. Validation occurs in the SafetyKernel."""
    return json.dumps({
        "status": "proposed",
        "zone": zone_id,
        "setpoint": temperature
    })

if __name__ == "__main__":
    print("Starting Sentinel Twin MCP Server...")
    mcp.run()
