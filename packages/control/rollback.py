"""Rollback manager for restoring safe baseline state."""

from packages.control.baseline_policy import BaselinePolicy
from packages.domain.models import BuildingStateV1
from packages.sim_adapter.contracts import ActionCommandV1


class RollbackManager:
    """Restores deterministic safety if the system is compromised."""

    def __init__(self, baseline_policy: BaselinePolicy):
        self.baseline = baseline_policy

    def restore(self, state: BuildingStateV1) -> list[ActionCommandV1]:
        """Generate override commands to immediately return to the safe baseline."""
        return self.baseline.decide(state)
