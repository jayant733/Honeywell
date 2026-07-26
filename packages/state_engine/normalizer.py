"""Converts simulation adapter telemetry into standard building state."""

from pathlib import Path
from typing import cast

import yaml

from packages.domain.models import BuildingStateV1, QualityFlag, ZoneStateV1
from packages.sim_adapter.contracts import TelemetryV1
from packages.state_engine.quality import QualityFlagger


class StateBuilder:
    """Builds a validated BuildingStateV1 from raw TelemetryV1."""

    def __init__(self, zone_map_path: Path):
        self.quality = QualityFlagger()
        self.zone_map = self._load_map(zone_map_path)

    def _load_map(self, path: Path) -> dict[str, str]:
        if not path.is_file():
            return {}
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("mappings", {})

    def build(self, telemetry: TelemetryV1) -> BuildingStateV1:
        """Normalize telemetry and construct the building state."""
        zones = []
        for raw_zone_id, temp in telemetry.zone_temperatures.items():
            mapped_id = self.zone_map.get(raw_zone_id, raw_zone_id)
            flag = self.quality.evaluate(mapped_id, telemetry.timestamp, temp)

            # Simple heuristic: occupied from 8 AM to 6 PM Monday-Friday
            is_occupied = False
            dt = telemetry.timestamp
            if dt.weekday() < 5 and 8 <= dt.hour < 18:
                is_occupied = True

            # PPD mapping (requires telemetry payload to include it, or we look it up)
            # We will assume TelemetryV1 includes zone_ppd
            zone_ppd = getattr(telemetry, 'zone_ppd', {}).get(raw_zone_id, float("nan"))
            
            zone_state = ZoneStateV1(
                zone_id=mapped_id,
                temperature=temp,
                occupancy=is_occupied,
                quality_flag=cast(QualityFlag, flag),
                comfort_debt=0.0,
                ppd_percent=zone_ppd
            )
            zones.append(zone_state)

        return BuildingStateV1(
            timestamp=telemetry.timestamp,
            outdoor_temperature=telemetry.outdoor_temperature,
            hvac_power=telemetry.hvac_power,
            zones=zones,
        )
