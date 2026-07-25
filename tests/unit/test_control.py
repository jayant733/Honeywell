"""Tests for deterministic policy and safety kernel."""

from datetime import datetime
from pathlib import Path

from packages.control.baseline_policy import BaselinePolicy
from packages.control.decision_engine import DecisionV1
from packages.control.safety_kernel import SafetyKernel
from packages.domain.models import BuildingStateV1, ZoneStateV1
from packages.sim_adapter.contracts import ActionCommandV1


def test_baseline_policy():
    policy = BaselinePolicy(Path("dummy.yaml"))

    zone = ZoneStateV1(zone_id="zone_1", occupancy=True)
    state = BuildingStateV1(timestamp=datetime.utcnow(), zones=[zone])

    actions = policy.decide(state)
    assert len(actions) == 2

    cooling = next(a for a in actions if "cooling" in a.actuator_id)
    assert cooling.value == 24.0


def test_safety_kernel_rejection():
    kernel = SafetyKernel(Path("dummy.yaml"))

    zone = ZoneStateV1(zone_id="zone_1", quality_flag="VALID")
    state = BuildingStateV1(timestamp=datetime.utcnow(), zones=[zone])

    # 1. Test overlap rejection
    bad_decision = DecisionV1(
        source="AI",
        rationale="Test",
        actions=[
            ActionCommandV1(actuator_id="zone_1_heating_setpoint", value=22.0),
            ActionCommandV1(actuator_id="zone_1_cooling_setpoint", value=22.0),  # No deadband!
        ],
    )

    val = kernel.evaluate(bad_decision, state)
    assert not val.safe
    assert "overlap" in val.message

    # 2. Test clipping
    clip_decision = DecisionV1(
        source="AI",
        rationale="Test",
        actions=[
            ActionCommandV1(
                actuator_id="zone_1_heating_setpoint", value=25.0
            ),  # Too high, will clip to 24.0
            ActionCommandV1(
                actuator_id="zone_1_cooling_setpoint", value=28.0
            ),  # Safe to avoid overlap with 24.0
        ],
    )

    val2 = kernel.evaluate(clip_decision, state)
    assert val2.safe  # It is safe because it CLIPS

    clipped_heat = next(a for a in val2.clipped_actions if "heating" in a.actuator_id)
    clipped_cool = next(a for a in val2.clipped_actions if "cooling" in a.actuator_id)

    assert clipped_heat.value == 24.0  # max heating is 24.0
    assert clipped_cool.value == 28.0  # untouched


def test_safety_kernel_enforces_dwell_and_rate_limits(tmp_path: Path):
    config = tmp_path / "limits.yaml"
    config.write_text(
        "temperature_limits:\n  min_heating_setpoint: 16\n  max_heating_setpoint: 24\n"
        "  min_cooling_setpoint: 20\n  max_cooling_setpoint: 30\n"
        "max_change_per_hour: 2\nminimum_dwell_minutes: 30\n",
        encoding="utf-8",
    )
    kernel = SafetyKernel(config)
    state = BuildingStateV1(timestamp=datetime(2026, 1, 1, 10), zones=[])
    first = DecisionV1(source="AI", rationale="x", actions=[ActionCommandV1("z_heating_setpoint", 21)])
    assert kernel.evaluate(first, state).safe
    second = DecisionV1(source="AI", rationale="x", actions=[ActionCommandV1("z_heating_setpoint", 22)])
    assert not kernel.evaluate(second, state).safe
