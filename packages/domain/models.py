"""Domain models representing building state."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

QualityFlag = Literal["VALID", "STALE", "MISSING"]


class ZoneStateV1(BaseModel):
    """Normalized state of a single zone."""

    zone_id: str
    temperature: float = Field(default=float("nan"))
    occupancy: bool = False
    quality_flag: QualityFlag = "VALID"
    comfort_debt: float = 0.0


class BuildingStateV1(BaseModel):
    """A cross-validated snapshot of the entire building."""

    timestamp: datetime
    outdoor_temperature: float = Field(default=float("nan"))
    hvac_power: float = Field(default=float("nan"))
    zones: list[ZoneStateV1] = Field(default_factory=list)
