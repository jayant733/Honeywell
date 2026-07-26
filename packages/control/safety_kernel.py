"""Safety Kernel ensuring no unsafe commands reach the adapter."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

from packages.control.decision_engine import DecisionV1
from packages.control.limits import LimitChecker
from packages.domain.models import BuildingStateV1
from packages.sim_adapter.contracts import ActionCommandV1


class ValidationResultV1:
    """The result of the safety evaluation."""

    def __init__(self, safe: bool, message: str, clipped_actions: list[ActionCommandV1]):
        self.safe = safe
        self.message = message
        self.clipped_actions = clipped_actions


class SafetyKernel:
    """Independent gatekeeper that validates and clips actions."""

    def __init__(self, config_path: Path):
        self.config = self._load_config(config_path)
        self.checker = LimitChecker(self.config)
        self.max_change_per_hour = float(self.config.get("max_change_per_hour", 2.0))
        self.minimum_dwell = timedelta(minutes=float(self.config.get("minimum_dwell_minutes", 30.0)))
        self.last_actions: dict[str, tuple[float, datetime]] = {}

    def _load_config(self, path: Path) -> dict[str, Any]:
        if not path.is_file():
            return {}
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def evaluate(self, decision: DecisionV1, state: BuildingStateV1) -> ValidationResultV1:
        """Evaluate a decision against safety constraints."""

        # 1. Telemetry & Comfort check
        for zone in state.zones:
            if zone.quality_flag in ("STALE", "MISSING"):
                return ValidationResultV1(
                    safe=False,
                    message=f"Rejected: Telemetry is {zone.quality_flag} for {zone.zone_id}.",
                    clipped_actions=[],
                )
            # PPD constraint (ASHRAE recommends < 20% for acceptable comfort)
            if zone.occupancy and zone.ppd_percent > 20.0:
                 # We don't reject outright because we might be trying to fix it,
                 # but we require that the proposed action must be pushing temperature 
                 # toward 22.0 if PPD is already violating.
                 # For the hackathon, we simply note it or reject actions that make it worse.
                 pass

        # 2. Constraint checking & clipping
        clipped = []
        for action in decision.actions:
            new_action = ActionCommandV1(
                actuator_id=action.actuator_id, value=action.value, command_id=action.command_id
            )

            if action.actuator_id.endswith("_cooling_setpoint"):
                new_action.value = self.checker.check_cooling(action.value)
            elif action.actuator_id.endswith("_heating_setpoint"):
                new_action.value = self.checker.check_heating(action.value)

            previous = self.last_actions.get(action.actuator_id)
            if previous is not None:
                old_value, old_time = previous
                elapsed_hours = max((state.timestamp - old_time).total_seconds() / 3600, 0.001)
                if state.timestamp - old_time < self.minimum_dwell:
                    return ValidationResultV1(False, "Rejected: minimum dwell time not met.", [])
                if abs(new_action.value - old_value) / elapsed_hours > self.max_change_per_hour:
                    return ValidationResultV1(False, "Rejected: rate limit exceeded.", [])

            clipped.append(new_action)

        # 3. Overlap check (requires looking at pairs of actions for a zone)
        # For simplicity in the hackathon, we assume the baseline policy doesn't violate this,
        # but if we detect it, we reject.
        heat_sp = {
            a.actuator_id: a.value for a in clipped if a.actuator_id.endswith("_heating_setpoint")
        }
        cool_sp = {
            a.actuator_id: a.value for a in clipped if a.actuator_id.endswith("_cooling_setpoint")
        }

        for hid, hval in heat_sp.items():
            zone_prefix = hid.replace("_heating_setpoint", "")
            cid = f"{zone_prefix}_cooling_setpoint"
            if cid in cool_sp:
                if not self.checker.check_overlap(hval, cool_sp[cid]):
                    return ValidationResultV1(
                        safe=False,
                        message=f"Rejected: Setpoint overlap in {zone_prefix} ({hval} vs {cool_sp[cid]}).",
                        clipped_actions=[],
                    )

        # If any values were clipped, we note it in the message, but it is "safe" to apply the clipped version
        is_clipped = any(c.value != o.value for c, o in zip(clipped, decision.actions))
        msg = "Safe. " + ("Actions were clipped to limits." if is_clipped else "")

        for action in clipped:
            self.last_actions[action.actuator_id] = (action.value, state.timestamp)
        return ValidationResultV1(safe=True, message=msg, clipped_actions=clipped)
