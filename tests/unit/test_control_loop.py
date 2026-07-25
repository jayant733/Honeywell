"""Tests for orchestrator loop."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from datetime import datetime

from apps.worker.orchestrator import ControlLoop
from packages.sim_adapter.contracts import TelemetryV1


def test_control_loop_tick():
    # Mocks
    sim = MagicMock()
    sim.read_telemetry.return_value = TelemetryV1(
        timestamp=datetime.utcnow(), zone_temperatures={}, outdoor_temperature=0, hvac_power=0
    )
    sim.acknowledge.return_value = []

    builder = MagicMock()
    builder.build.return_value = MagicMock()

    ai = MagicMock()
    ai.complete_structured.return_value = MagicMock()

    engine = MagicMock()
    engine.build_candidates.return_value = MagicMock()

    safety = MagicMock()
    safety_val = MagicMock()
    safety_val.safe = True
    safety_val.clipped_actions = [MagicMock()]
    safety.evaluate.return_value = safety_val

    rollback = MagicMock()
    repo = MagicMock()

    # Run loop
    loop = ControlLoop(sim, builder, ai, engine, safety, rollback, repo, shadow_mode=False)
    loop.tick()

    # Verify actuate was called
    sim.apply_action.assert_called_once()

    # Verify persistence called multiple times
    assert repo.append.call_count >= 4
