"""Schemas mapping to LLM tool and output responses."""

from pydantic import BaseModel, Field


class DecisionProposalV1(BaseModel):
    """The structured decision the model proposes after analysis."""

    rationale: str = Field(
        description="A brief explanation of why this action is proposed based on current state and safety rules."
    )
    actuator_id: str = Field(
        description="The exact string ID of the actuator to modify, or 'NONE' if abstaining."
    )
    target_value: float | None = Field(
        description="The numeric setpoint to apply. Required if actuator_id is not 'NONE'."
    )
    confidence_score: float = Field(
        description="A value between 0.0 and 1.0 indicating confidence in this decision."
    )
