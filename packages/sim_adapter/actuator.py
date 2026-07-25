"""Actuator management for safe EnergyPlus override commands."""

from typing import Any

from packages.sim_adapter.contracts import ActionCommandV1


class InvalidActuatorError(ValueError):
    """Raised when an action targets a non-allow-listed actuator."""

    pass


class ActuatorAdapter:
    """Manages allow-list and applying actuators to the simulation."""

    # Define which actuators the AI/UI is permitted to touch
    def __init__(self, api: Any, state: Any, actuator_handles: dict[str, int]):
        self.api = api
        self.state = state
        self.actuator_handles = actuator_handles

    def validate_action(self, action: ActionCommandV1) -> None:
        """Raises InvalidActuatorError if the action is not permitted."""
        if action.actuator_id not in self.actuator_handles:
            raise InvalidActuatorError(f"Actuator '{action.actuator_id}' is not in the allow-list.")

    def apply_action(self, action: ActionCommandV1) -> None:
        """Applies an allowed action to the EnergyPlus API."""
        self.validate_action(action)

        handle = self.actuator_handles.get(action.actuator_id)
        if handle is None or handle < 0:
            raise InvalidActuatorError(
                f"Handle for actuator '{action.actuator_id}' not found or invalid."
            )

        self.api.exchange.set_actuator_value(self.state, handle, action.value)

    def reset_actuator(self, actuator_id: str) -> None:
        """Resets the actuator to give control back to EnergyPlus (if supported)."""
        handle = self.actuator_handles.get(actuator_id)
        if handle is not None and handle >= 0:
            self.api.exchange.reset_actuator(self.state, handle)
