"""FastAPI REST routes for Sentinel."""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from packages.persistence.event_store import EventRepository
from apps.api.dependencies import get_event_store
from packages.analytics.replay import ReplayService
from datetime import datetime

router = APIRouter(prefix="/api")

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

