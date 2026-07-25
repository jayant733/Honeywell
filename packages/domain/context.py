"""Run identity primitives used for audit correlation across future milestones."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RunContext:
    """Identifies one scenario execution without carrying mutable runtime state."""

    run_id: str
    scenario_id: str
    started_at: datetime
