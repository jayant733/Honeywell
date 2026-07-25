import sqlite3
from pathlib import Path

import pytest

from packages.sim_adapter.baseline import (
    BaselineAssets,
    BaselinePrerequisiteError,
    validate_baseline_assets,
    validate_output_columns,
    validate_sql_output_contract,
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


def test_sql_contract_reports_missing_energyplus_series(tmp_path: Path) -> None:
    sql_path = tmp_path / "eplusout.sql"
    with sqlite3.connect(sql_path) as connection:
        connection.execute("CREATE TABLE ReportDataDictionary (Name TEXT)")
        connection.execute("INSERT INTO ReportDataDictionary VALUES ('Zone Mean Air Temperature')")

    missing = validate_sql_output_contract(
        sql_path,
        {"Zone Mean Air Temperature", "Zone People Occupant Count"},
    )

    assert missing == {"Zone People Occupant Count"}
