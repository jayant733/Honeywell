# Data Dictionary

This document explains the standard data models used in the system, primarily the `BuildingStateV1`.

## BuildingStateV1
Represents a unified, cross-validated snapshot of the entire building at a given timestep.
- **timestamp**: ISO8601 timestamp.
- **outdoor_temperature**: Current outside drybulb temperature.
- **hvac_power**: Current total electrical power used by HVAC (Watts).
- **zones**: A list of `ZoneStateV1` objects.

## ZoneStateV1
- **zone_id**: Normalized name of the zone (e.g. `Office_South`).
- **temperature**: Current zone air temperature (Celsius).
- **occupancy**: A boolean or integer proxy representing if people are currently occupying the zone. (Defaults to True during work hours or if measured).
- **quality_flag**: String representing data trust (e.g., `VALID`, `STALE`, `MISSING`).
- **comfort_debt**: Accumulated time (or degree-time) the zone has spent outside the comfort bounds while occupied. (Initially set to 0.0, will be updated in M21).

## Quality Flags
- **VALID**: Data is fresh and within physically plausible bounds.
- **STALE**: Data has not updated in an expected timeframe.
- **MISSING**: Expected sensor stream is totally absent.
