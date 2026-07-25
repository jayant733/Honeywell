"""Decision Engine comparing AI and deterministic intents."""

from pydantic import BaseModel, Field

from packages.ai.schemas import DecisionProposalV1
from packages.control.baseline_policy import BaselinePolicy
from packages.control.objective import ObjectiveScorer
from packages.domain.models import BuildingStateV1
from packages.sim_adapter.contracts import ActionCommandV1


class DecisionV1(BaseModel):
    """The final chosen decision encompassing source and intent."""

    source: str = Field(description="'AI' or 'BASELINE'")
    rationale: str
    actions: list[ActionCommandV1]

    # We must allow arbitrary types for ActionCommandV1 which is a dataclass
    model_config = {"arbitrary_types_allowed": True}


class DecisionEngine:
    """Selects the best candidate action between Baseline and AI."""

    def __init__(self, baseline: BaselinePolicy, scorer: ObjectiveScorer):
        self.baseline = baseline
        self.scorer = scorer

    def build_candidates(
        self, state: BuildingStateV1, ai_proposal: DecisionProposalV1 | None
    ) -> DecisionV1:
        """Compares baseline and AI, choosing AI if safe and confident."""

        baseline_actions = self.baseline.decide(state)

        # Determine AI actions
        ai_actions = []
        if (
            ai_proposal
            and ai_proposal.actuator_id != "NONE"
            and ai_proposal.target_value is not None
        ):
            ai_actions.append(
                ActionCommandV1(actuator_id=ai_proposal.actuator_id, value=ai_proposal.target_value)
            )

        # If AI abstains or has no confidence, fallback to baseline
        if not ai_actions or (ai_proposal and ai_proposal.confidence_score < 0.5):
            return DecisionV1(
                source="BASELINE",
                rationale="AI abstained or lacked confidence. Falling back to deterministic baseline.",
                actions=baseline_actions,
            )

        # Score them
        baseline_score = self.scorer.score(state, baseline_actions)
        ai_score = self.scorer.score(state, ai_actions)

        # For the hackathon, we trust the AI if its score isn't drastically worse
        if ai_score >= baseline_score - 10.0:
            return DecisionV1(
                source="AI",
                rationale=ai_proposal.rationale if ai_proposal else "AI selected.",
                actions=ai_actions,
            )

        return DecisionV1(
            source="BASELINE",
            rationale=f"AI proposed action scored too poorly ({ai_score} vs {baseline_score}). Rejected.",
            actions=baseline_actions,
        )
