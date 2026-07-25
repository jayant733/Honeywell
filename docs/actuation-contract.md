# Actuation Contract

This document defines the boundary between the artificial intelligence / operator interface and the EnergyPlus simulation.

## 1. Safety & Stability Policy
1. **No direct EPJSON editing during a run:** The AI/UI must never directly modify building models or schedules on disk. All commands flow through the Simulation Adapter.
2. **Explicit Allow-List:** Only a predefined list of actuators can be manipulated. Any command targeting an unregistered actuator will be rejected by the Simulation Adapter (and later by the Safety Kernel).
3. **Data Immutability:** Once a telemetry point is published for a time step, it is immutable. Acknowledgment of actions is always linked to the timestep in which they are applied.

## 2. Telemetry Schema (TelemetryV1)
The adapter provides a unified snapshot of the building at the current timestep.

- `timestamp`: The simulation time of the reading (ISO8601).
- `zone_temperatures`: Mapping of zone IDs to their current air temperature (Celsius).
- `outdoor_temperature`: Current outdoor air temperature (Celsius).
- `hvac_power`: Total HVAC electrical power (Watts).

## 3. Action Command Schema (ActionCommandV1)
All commands issued to the building must conform to this schema:

- `command_id`: A unique UUID for the command (for tracking/acknowledgment).
- `actuator_id`: The target actuator identifier (e.g., `zone_1_cooling_setpoint`).
- `value`: The target numeric value (e.g., `24.0`).
- `duration_minutes`: (Optional) How long the override should persist before reverting to baseline schedule. (Note: The adapter might rely on the control loop to send new commands rather than internally managing durations, but it's part of the API).

## 4. Allow-Listed Actuators
Initially, the simulation adapter will restrict control to the following types of actuators:
- **Cooling Setpoint**: `Zone Temperature Control` / `Cooling Setpoint`
- **Heating Setpoint**: `Zone Temperature Control` / `Heating Setpoint`

Any attempt to override unlisted components (like `Fan Power` or `Chiller COP`) will raise an immediate error.

## 5. Acknowledgement
When a command is submitted to the Simulation Adapter:
- The adapter validates the `actuator_id`.
- The adapter sets the actuator via the `pyenergyplus` API at the next timestep.
- The adapter returns an acknowledgment indicating the command was accepted and queued for actuation.
