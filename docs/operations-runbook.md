# Operations Runbook

## Modes of Operation
1. **Shadow Mode**: The default mode. The AI observes the simulation, makes decisions, and the Safety Kernel evaluates them, but **no commands are sent to the simulation**. The baseline EnergyPlus schedules remain untouched. This is used to prove the AI's intent is safe without risking comfort.
2. **Autonomous Mode**: The Safety-validated commands are actually dispatched to the EnergyPlus `SimulationAdapter` and alter the physical simulation.

## How to run
```powershell
# Run in shadow mode
.\scripts\run_scenario.ps1

# Run in autonomous mode
.\scripts\run_scenario.ps1 -AutonomousMode
```

## Emergency Rollback
If the AI behaves erratically or the connection is lost, the Safety Kernel will automatically engage the `RollbackManager` to restore the deterministic baseline policy setpoints for all zones.
