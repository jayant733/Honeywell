"""Runner for EnergyPlus simulations using pyenergyplus."""

import sys
from pathlib import Path
from typing import Any

# Attempt to load pyenergyplus, add default path if not found
try:
    import pyenergyplus
except ImportError:
    ep_path = "C:\\EnergyPlusV26-1-0"
    if ep_path not in sys.path:
        sys.path.append(ep_path)

from pyenergyplus.api import EnergyPlusAPI

from packages.sim_adapter.actuator import ActuatorAdapter
from packages.sim_adapter.contracts import ActionAcknowledgement, ActionCommandV1, TelemetryV1
from packages.sim_adapter.parser import TelemetryParser


class SimulationAdapter:
    """Stable adapter wrapping EnergyPlus simulation for step-by-step control."""

    def __init__(self, model_path: Path, weather_path: Path, output_dir: Path):
        self.model_path = model_path
        self.weather_path = weather_path
        self.output_dir = output_dir

        self.api = EnergyPlusAPI()
        self.state = self.api.state_manager.new_state()

        # Internal state
        self.is_running = False
        self.current_telemetry: TelemetryV1 | None = None

        # Will be populated during warm-up callbacks
        self.variable_handles: dict[str, int] = {}
        self.actuator_handles: dict[str, int] = {}

        self.parser: TelemetryParser | None = None
        self.actuator: ActuatorAdapter | None = None

        self._action_queue: list[ActionCommandV1] = []
        self._acknowledgements: list[ActionAcknowledgement] = []

        # Register callbacks
        self.api.runtime.callback_begin_zone_timestep_after_init_heat_balance(
            self.state, self._on_begin_zone_timestep
        )

    def _initialize_handles(self) -> None:
        """Fetch handles for variables and actuators after EP is initialized."""
        if not self.api.exchange.api_data_fully_ready(self.state):
            return

        if self.variable_handles and self.actuator_handles:
            return  # Already initialized

        controlled_zones = ("CORE_BOTTOM", "PERIMETER_BOT_ZN_1")
        for zone_name in controlled_zones:
            self.variable_handles[f"temp_{zone_name}"] = self.api.exchange.get_variable_handle(
                self.state, "Zone Mean Air Temperature", zone_name
            )
        self.variable_handles["outdoor_temp"] = self.api.exchange.get_variable_handle(
            self.state, "Site Outdoor Air Drybulb Temperature", "Environment"
        )

        for zone_name in controlled_zones:
            actuator_prefix = zone_name.lower()
            self.actuator_handles[f"{actuator_prefix}_cooling_setpoint"] = (
                self.api.exchange.get_actuator_handle(
                    self.state, "Zone Temperature Control", "Cooling Setpoint", zone_name
                )
            )
            self.actuator_handles[f"{actuator_prefix}_heating_setpoint"] = (
                self.api.exchange.get_actuator_handle(
                    self.state, "Zone Temperature Control", "Heating Setpoint", zone_name
                )
            )

        self.parser = TelemetryParser(self.api, self.state, self.variable_handles)
        self.actuator = ActuatorAdapter(self.api, self.state, self.actuator_handles)

    def _on_begin_zone_timestep(self, state: Any) -> None:
        """Callback invoked by EnergyPlus at the start of a timestep."""
        self._initialize_handles()
        if not self.parser or not self.actuator:
            return

        # 1. Apply queued actions
        for action in self._action_queue:
            try:
                self.actuator.apply_action(action)
                self._acknowledgements.append(
                    ActionAcknowledgement(
                        command_id=action.command_id, accepted=True, message="Applied."
                    )
                )
            except Exception as e:
                self._acknowledgements.append(
                    ActionAcknowledgement(
                        command_id=action.command_id, accepted=False, message=str(e)
                    )
                )
        self._action_queue.clear()

        # 2. Read state
        self.current_telemetry = self.parser.parse()

    def run_simulation(self) -> int:
        """Runs the simulation synchronously.

        In a real application, you might run this on a separate thread and
        use synchronization primitives in the callback to pause/step the sim.
        """
        self.is_running = True

        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True)

        # Format args for EnergyPlus
        cmd_args = [
            "-w",
            str(self.weather_path.absolute()),
            "-d",
            str(self.output_dir.absolute()),
            str(self.model_path.absolute()),
        ]

        result = self.api.runtime.run_energyplus(self.state, cmd_args)
        self.is_running = False
        return result

    def apply_action(self, action: ActionCommandV1) -> None:
        """Queue an action to be applied at the next available timestep."""
        self._action_queue.append(action)

    def read_telemetry(self) -> TelemetryV1 | None:
        """Returns the latest parsed telemetry."""
        return self.current_telemetry

    def acknowledge(self) -> list[ActionAcknowledgement]:
        """Returns list of acknowledgements and clears them."""
        acks = list(self._acknowledgements)
        self._acknowledgements.clear()
        return acks

    def stop(self) -> None:
        """Cleans up the EP state."""
        self.api.state_manager.delete_state(self.state)
