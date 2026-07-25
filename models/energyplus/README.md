# EnergyPlus reference-model assets

Milestone 2 uses a medium-office reference building with a weather file matched to
the selected location. These assets are intentionally not committed until their
source, license, EnergyPlus version, and checksum are recorded in
`baseline_manifest.json`.

Place the selected assets here before running the baseline:

```text
models/energyplus/
  building.epJSON
  weather.epw
```

The model must request the output variables listed in `outputs.yaml`. Select a
model that supports a 15-minute timestep and exposes at least two conditioned
zones. Do not alter the model, weather, schedules, or initial conditions between
the baseline and AI-controlled comparison runs.
