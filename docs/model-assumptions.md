# Reference model and baseline assumptions

## Fixed comparison contract

The baseline and controlled runs use the same EnergyPlus engine version, EPJSON
model, EPW weather file, schedules, run-period, timestep, initialization, and
output contract. The controller is the only experimental variable.

## Selected model profile

Use a medium office with at least two conditioned zones and a controllable HVAC
system. The final selection must be recorded in `models/energyplus/baseline_manifest.json`
with source URL, license, EnergyPlus version, and SHA-256 checksums.

## Required proof before Milestone 2 closes

1. Record asset provenance and checksums, then change manifest status to `ready`.
2. Run `scripts/run_baseline.ps1` twice from the same configuration.
3. Preserve run manifests and show matching required output series.
4. Confirm the output contract in `models/energyplus/outputs.yaml` is available.

Generated EnergyPlus output stays in `data/outputs/` and is excluded from Git.
