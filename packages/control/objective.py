"""Objective scoring for evaluating decision candidates."""

from packages.domain.models import BuildingStateV1
from packages.sim_adapter.contracts import ActionCommandV1


class ObjectiveScorer:
    """Evaluates candidates based on projected comfort and energy."""

    def score(self, state: BuildingStateV1, actions: list[ActionCommandV1]) -> float:
        """
        Scores a list of actions.
        Higher is better.
        Currently a stub that penalizes extreme setpoints.
        """
        score = 100.0

        for action in actions:
            if action.actuator_id.endswith("_cooling_setpoint"):
                # Penalize cooling setpoints that are too low (high energy)
                if action.value < 22.0:
                    score -= (22.0 - action.value) * 5
            elif action.actuator_id.endswith("_heating_setpoint"):
                # Penalize heating setpoints that are too high (high energy)
                if action.value > 22.0:
                    score -= (action.value - 22.0) * 5

        return score
