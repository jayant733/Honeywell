"""Contracts and schemas for the Simulation Adapter."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ActionCommandV1:
    """A command to actuate a building setpoint."""

    actuator_id: str
    value: float
    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    duration_minutes: float | None = None


@dataclass
class TelemetryV1:
    """A snapshot of building state from the simulation."""

    timestamp: datetime
    zone_temperatures: dict[str, float]
    outdoor_temperature: float
    hvac_power: float
    zone_ppd: dict[str, float] = field(default_factory=dict)
    # Other metrics could be added here later


@dataclass
class ActionAcknowledgement:
    """Acknowledgment that a command was accepted/rejected by the adapter."""

    command_id: str
    accepted: bool
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
