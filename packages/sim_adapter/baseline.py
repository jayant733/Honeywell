"""Reproducible baseline-run prerequisites and output-contract validation."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class BaselineAssets:
    """Paths required to execute a comparable EnergyPlus baseline run."""

    model_path: Path
    weather_path: Path
    outputs_path: Path
    manifest_path: Path


class BaselinePrerequisiteError(RuntimeError):
    """Raised when baseline assets are not ready for a valid comparison run."""


def validate_baseline_assets(assets: BaselineAssets) -> None:
    """Fail with a clear message until versioned model and weather assets exist."""

    required_paths = {
        "EnergyPlus model": assets.model_path,
        "EnergyPlus weather file": assets.weather_path,
        "Output contract": assets.outputs_path,
        "Baseline manifest": assets.manifest_path,
    }
    missing = [f"{name}: {path}" for name, path in required_paths.items() if not path.is_file()]
    if missing:
        joined = "; ".join(missing)
        raise BaselinePrerequisiteError(f"Baseline run cannot start; missing {joined}")

    manifest = load_manifest(assets.manifest_path)
    if manifest.get("status") != "ready":
        raise BaselinePrerequisiteError(
            "Baseline manifest must have status 'ready' after source, version, and checksums "
            "are recorded."
        )


def load_manifest(path: Path) -> dict[str, Any]:
    """Load the versioned baseline manifest without silently accepting invalid JSON."""

    with path.open(encoding="utf-8") as manifest_file:
        content: Any = json.load(manifest_file)
    if not isinstance(content, dict):
        raise BaselinePrerequisiteError("Baseline manifest must contain a JSON object.")
    return content


def validate_output_columns(columns: set[str], required_series: set[str]) -> set[str]:
    """Return missing normalized series so callers can produce actionable diagnostics."""

    return required_series.difference(columns)


def validate_sql_output_contract(sql_path: Path, required_series: set[str]) -> set[str]:
    """Return EnergyPlus report variables missing from the completed SQL output."""

    if not sql_path.is_file():
        raise BaselinePrerequisiteError(f"EnergyPlus SQL output does not exist: {sql_path}")

    with sqlite3.connect(sql_path) as connection:
        rows = connection.execute("SELECT DISTINCT Name FROM ReportDataDictionary").fetchall()
    available_series = {str(row[0]) for row in rows}
    return required_series.difference(available_series)
