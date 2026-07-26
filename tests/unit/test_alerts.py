"""Unit tests for Alert Engine."""

import pytest
from datetime import datetime
from packages.domain.models import BuildingStateV1, ZoneStateV1
from packages.domain.alerts import AlertEngine

def test_alert_engine_stale_telemetry():
    engine = AlertEngine()
    
    zone = ZoneStateV1(zone_id="Z1", temperature=22.0, occupancy=True, hvac_mode="COOLING", setpoint=22.0, quality_flag="STALE")
    state = BuildingStateV1(timestamp=datetime.now(), zones=[zone], hvac_power=1000.0)
    
    alerts = engine.evaluate_state(state)
    assert len(alerts) == 1
    assert alerts[0]["type"] == "STALE_TELEMETRY"

def test_alert_engine_comfort_violation():
    engine = AlertEngine()
    
    zone = ZoneStateV1(zone_id="Z1", temperature=28.0, occupancy=True, hvac_mode="COOLING", setpoint=22.0, quality_flag="VALID")
    state = BuildingStateV1(timestamp=datetime.now(), zones=[zone], hvac_power=1000.0)
    
    alerts = engine.evaluate_state(state)
    assert len(alerts) == 1
    assert alerts[0]["type"] == "COMFORT_VIOLATION"

def test_alert_engine_ai_rejected():
    engine = AlertEngine()
    
    decision = {
        "zone_id": "Z1",
        "safety_verdict": "REJECTED"
    }
    alerts = engine.evaluate_decision(decision)
    assert len(alerts) == 1
    assert alerts[0]["type"] == "AI_ACTION_REJECTED"
