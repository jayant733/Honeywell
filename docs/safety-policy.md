# Safety Policy

The Safety Kernel acts as the final gatekeeper for all actions before they reach the Simulation Adapter.

## Constraints
1. **Min Cooling Setpoint**: The cooling setpoint can NEVER be set below `20.0 C` (to prevent coil freezing and extreme energy waste).
2. **Max Heating Setpoint**: The heating setpoint can NEVER be set above `24.0 C`.
3. **Overlapping Setpoints**: The cooling setpoint must ALWAYS be at least `1.0 C` higher than the heating setpoint (deadband) to prevent simultaneous heating and cooling.
4. **Stale Data Rejection**: If the telemetry quality flag is `STALE` or `MISSING`, the safety kernel rejects all AI actions and requests rollback.

## Rollback
If an action is rejected due to safety violations, or if telemetry drops out, the system triggers the `RollbackManager` to restore the deterministic baseline policy.
