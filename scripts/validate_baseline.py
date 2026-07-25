"""Validate that recorded EnergyPlus assets are ready for a reproducible baseline run."""

from pathlib import Path

from packages.sim_adapter.baseline import BaselineAssets, validate_baseline_assets


def main() -> None:
    validate_baseline_assets(
        BaselineAssets(
            model_path=Path("models/energyplus/building.epJSON"),
            weather_path=Path("models/energyplus/weather.epw"),
            outputs_path=Path("models/energyplus/outputs.yaml"),
            manifest_path=Path("models/energyplus/baseline_manifest.json"),
        )
    )


if __name__ == "__main__":
    main()
