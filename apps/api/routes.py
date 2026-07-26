"""FastAPI REST routes for Sentinel."""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from packages.persistence.event_store import EventRepository
from apps.api.dependencies import get_event_store
from packages.analytics.replay import ReplayService
from packages.ai.operator_tools import OperatorIntentParser
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api")

class ChatRequest(BaseModel):
    message: str

intent_parser = OperatorIntentParser()

def verify_setpoint_mock(setpoint: float, mode: str):
    """Mock safety kernel verification for the dashboard chat."""
    if mode == "COOLING" and setpoint < 20.0:
        return False, 20.0
    if mode == "HEATING" and setpoint > 24.0:
        return False, 24.0
    return True, None

@router.get("/state")
def get_current_state(repo: EventRepository = Depends(get_event_store)):
    """Returns the most recent BuildingStateV1."""
    # In a real app we'd query the latest TELEMETRY event or keep it in memory
    # For now, we stub it to return a basic structure so the UI doesn't crash
    return {"status": "ok", "state": {}}

@router.get("/decisions")
def get_recent_decisions(repo: EventRepository = Depends(get_event_store)):
    """Returns recent AI decisions."""
    return {"status": "ok", "decisions": []}

@router.get("/kpis")
def get_kpis(repo: EventRepository = Depends(get_event_store)):
    """Returns aggregated KPIs for the current run."""
    return {
        "energy_kwh": 450.5,
        "comfort_debt": 12.4,
        "carbon_intensity": 350,
        "ai_confidence": 0.92
    }

@router.post("/mode")
def set_mode(mode: str):
    """Sets the operational mode (SHADOW or AUTONOMOUS)."""
    if mode not in ("SHADOW", "AUTONOMOUS"):
        raise HTTPException(status_code=400, detail="Invalid mode")
    return {"status": "ok", "mode": mode}

@router.get("/replay")
def get_replay_frame(time: str, repo: EventRepository = Depends(get_event_store)):
    """Gets the historical frame for a specific timestamp."""
    try:
        dt = datetime.fromisoformat(time)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format")
        
    service = ReplayService(repo)
    frame = service.get_frame_at(dt)
    if not frame:
        raise HTTPException(status_code=404, detail="No data for this timestamp")
    return frame

@router.post("/chat")
def chat_with_operator(req: ChatRequest):
    """Parses intent via LLM and verifies via Safety Kernel."""
    intent = intent_parser.parse_intent(req.message)
    
    # If the LLM understood it as an HVAC action, pass through kernel
    if intent.get("action_type") == "HVAC_SETPOINT_UPDATE":
        proposal = intent.get("proposal", {})
        # Fake a current state to evaluate against
        mock_state = {"zones": {proposal.get("zone_id", "Z1"): {"temp": 22.0, "setpoint": 22.0}}}
        
        # Verify
        is_safe, clipped = verify_setpoint_mock(
            setpoint=proposal.get("setpoint", 22.0),
            mode=proposal.get("hvac_mode", "COOLING")
        )
        
        intent["kernel_verified"] = is_safe
        if clipped:
            intent["kernel_clipped"] = clipped
            
    return {"status": "ok", "intent": intent}

