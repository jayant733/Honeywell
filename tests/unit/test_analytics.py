"""Unit tests for KPI Engine."""

import pytest
from packages.analytics.kpis import KpiEngine
from packages.analytics.comparison import ComparisonEngine
from packages.domain.models import BuildingStateV1, ZoneStateV1
from datetime import datetime

def test_comfort_debt_calculation():
    kpi = KpiEngine(comfort_band=(21.0, 24.0))
    
    # Create an occupied state that is too hot (25.0) -> debt of 1.0 * (1/60)
    hot_zone = ZoneStateV1(zone_id="Z1", temperature=25.0, occupancy=True, hvac_mode="COOLING", setpoint=22.0, quality_flag="VALID")
    state = BuildingStateV1(timestamp=datetime.now(), zones=[hot_zone], hvac_power=1000.0)
    
    debt = kpi.calculate_comfort_debt([state])
    assert debt > 0.0

def test_comparison_savings():
    kpi = KpiEngine()
    comp = ComparisonEngine()
    
    # Baseline uses 2000W, AI uses 1000W
    base_zone = ZoneStateV1(zone_id="Z1", temperature=22.0, occupancy=True, hvac_mode="COOLING", setpoint=22.0, quality_flag="VALID")
    base_state = BuildingStateV1(timestamp=datetime.now(), zones=[base_zone], hvac_power=2000.0)
    
    ai_zone = ZoneStateV1(zone_id="Z1", temperature=22.0, occupancy=True, hvac_mode="COOLING", setpoint=22.0, quality_flag="VALID")
    ai_state = BuildingStateV1(timestamp=datetime.now(), zones=[ai_zone], hvac_power=1000.0)
    
    result = comp.compare([base_state], [ai_state])
    assert result["savings"]["energy_kwh"] > 0
    assert result["savings"]["energy_pct"] == 48.5
