"""Unit tests for the state engine (M4)."""

from datetime import datetime
from pathlib import Path
from unittest.mock import mock_open, patch

from packages.sim_adapter.contracts import TelemetryV1
from packages.state_engine.normalizer import StateBuilder
from packages.state_engine.quality import QualityFlagger


def test_quality_flagger():
    flagger = QualityFlagger()
    now = datetime(2024, 7, 26, 10, 0, 0)

    # Valid reading
    assert flagger.evaluate("zone_1", now, 24.5) == "VALID"

    # Missing reading
    assert flagger.evaluate("zone_1", now, None) == "MISSING"
    assert flagger.evaluate("zone_1", now, float("nan")) == "MISSING"


def test_state_builder():
    mock_yaml = "mappings:\n  temp_zone_1: 'Office_1'"
    with patch("pathlib.Path.is_file", return_value=True):
        with patch("pathlib.Path.open", mock_open(read_data=mock_yaml)):
            builder = StateBuilder(Path("dummy.yaml"))

    # Simulate telemetry at 14:00 on a Wednesday (occupied)
    dt = datetime(2024, 7, 24, 14, 0, 0)  # July 24 2024 is Wed
    telemetry = TelemetryV1(
        timestamp=dt,
        zone_temperatures={"temp_zone_1": 23.5, "temp_zone_2": float("nan")},
        outdoor_temperature=30.0,
        hvac_power=1000.0,
    )

    state = builder.build(telemetry)

    assert state.outdoor_temperature == 30.0
    assert len(state.zones) == 2

    zone_1 = next(z for z in state.zones if z.zone_id == "Office_1")
    assert zone_1.temperature == 23.5
    assert zone_1.quality_flag == "VALID"
    assert zone_1.occupancy is True  # 14:00 weekday

    zone_2 = next(z for z in state.zones if z.zone_id == "temp_zone_2")
    assert zone_2.quality_flag == "MISSING"
