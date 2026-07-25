"""Deterministic baseline BMS controller."""

from pathlib import Path
from typing import Any

import yaml

from packages.domain.models import BuildingStateV1
from packages.sim_adapter.contracts import ActionCommandV1


class BaselinePolicy:
    """Calculates deterministic default HVAC setpoints based on occupancy."""

    def __init__(self, config_path: Path):
        self.config = self._load_config(config_path)
        self.setpoints = self.config.get(
            "baseline_setpoints",
            {
                "occupied": {"heating": 21.0, "cooling": 24.0},
                "unoccupied": {"heating": 16.0, "cooling": 28.0},
            },
        )
        self.deadband = self.config.get("deadband", 0.5)

    def _load_config(self, path: Path) -> dict[str, Any]:
        if not path.is_file():
            return {}
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def decide(self, state: BuildingStateV1) -> list[ActionCommandV1]:
        """Generate safe, default commands based solely on current state."""
        actions = []
        for zone in state.zones:
            mode = "occupied" if zone.occupancy else "unoccupied"

            # Simple deadband logic could be added here to avoid issuing commands
            # if we are already near the setpoint, but for the baseline we just
            # enforce the schedule.

            # Note: A real BMS would read current setpoints to avoid spamming commands,
            # but we assume the SimulationAdapter handles duplicate filtering or we just resend.

            actions.append(
                ActionCommandV1(
                    actuator_id=f"{zone.zone_id.lower()}_cooling_setpoint",
                    value=self.setpoints[mode]["cooling"],
                )
            )
            actions.append(
                ActionCommandV1(
                    actuator_id=f"{zone.zone_id.lower()}_heating_setpoint",
                    value=self.setpoints[mode]["heating"],
                )
            )

        return actions
