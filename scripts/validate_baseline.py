"""Validate that recorded EnergyPlus assets are ready for a reproducible baseline run."""

from pathlib import Path

from packages.sim_adapter.baseline import (
    BaselineAssets,
    validate_baseline_assets,
    validate_sql_output_contract,
)

REQUIRED_ENERGYPLUS_SERIES = {
    "Site Outdoor Air Drybulb Temperature",
    "Zone Mean Air Temperature",
    "Zone Thermostat Heating Setpoint Temperature",
    "Zone Thermostat Cooling Setpoint Temperature",
    "Zone People Occupant Count",
    "Zone Thermal Comfort Fanger Model PPD",
    "Zone Heating Setpoint Not Met Time",
    "Zone Cooling Setpoint Not Met Time",
}


def main() -> None:
    validate_baseline_assets(
        BaselineAssets(
            model_path=Path("models/energyplus/building.epJSON"),
            weather_path=Path("models/energyplus/weather.epw"),
            outputs_path=Path("models/energyplus/outputs.yaml"),
            manifest_path=Path("models/energyplus/baseline_manifest.json"),
        )
    )


def validate_completed_run(sql_path: Path) -> None:
    """Fail completed baseline validation when a required simulator signal is absent."""

    missing = validate_sql_output_contract(sql_path, REQUIRED_ENERGYPLUS_SERIES)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise RuntimeError(f"Baseline SQL is missing required EnergyPlus series: {missing_text}")


if __name__ == "__main__":
    main()
