from pathlib import Path

import pytest

from packages.sim_adapter.baseline import (
    BaselineAssets,
    BaselinePrerequisiteError,
    validate_baseline_assets,
    validate_output_columns,
)


def test_output_contract_reports_missing_series() -> None:
    missing = validate_output_columns(
        columns={"zone_air_temperature_c", "facility_total_hvac_electricity_j"},
        required_series={"zone_air_temperature_c", "zone_people_occupant_count"},
    )

    assert missing == {"zone_people_occupant_count"}


def test_baseline_assets_require_versioned_model_and_weather(tmp_path: Path) -> None:
    assets = BaselineAssets(
        model_path=tmp_path / "building.epJSON",
        weather_path=tmp_path / "weather.epw",
        outputs_path=tmp_path / "outputs.yaml",
        manifest_path=tmp_path / "baseline_manifest.json",
    )

    with pytest.raises(BaselinePrerequisiteError, match="EnergyPlus model"):
        validate_baseline_assets(assets)
