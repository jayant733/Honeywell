"""The main control loop orchestrating all components."""

import logging
import uuid

from packages.ai.ollama_client import OllamaClient
from packages.control.decision_engine import DecisionEngine
from packages.control.rollback import RollbackManager
from packages.control.safety_kernel import SafetyKernel
from packages.persistence.event_store import EventRepository
from packages.sim_adapter.runner import SimulationAdapter
from packages.state_engine.normalizer import StateBuilder

logger = logging.getLogger(__name__)


class ControlLoop:
    """Orchestrates the observe -> decide -> validate -> act loop."""

    def __init__(
        self,
        sim: SimulationAdapter,
        builder: StateBuilder,
        ai_client: OllamaClient,
        engine: DecisionEngine,
        safety: SafetyKernel,
        rollback: RollbackManager,
        repo: EventRepository,
        shadow_mode: bool = True,
    ):
        self.sim = sim
        self.builder = builder
        self.ai = ai_client
        self.engine = engine
        self.safety = safety
        self.rollback = rollback
        self.repo = repo
        self.shadow_mode = shadow_mode

    def tick(self) -> None:
        """Executes a single pass of the control loop (called per simulation step)."""
        correlation_id = str(uuid.uuid4())

        # 1. Observe
        raw_telemetry = self.sim.read_telemetry()
        if not raw_telemetry:
            return

        state = self.builder.build(raw_telemetry)
        self.repo.append("TELEMETRY", correlation_id, state)

        # 2. AI Proposal
        system_prompt = "You are a BMS controller. Propose a safe HVAC action."
        user_prompt = f"Current state: {state.model_dump_json()}"
        ai_proposal = self.ai.complete_structured(system_prompt, user_prompt)
        self.repo.append("AI_PROPOSAL", correlation_id, ai_proposal)

        # 3. Decision Engine
        decision = self.engine.build_candidates(state, ai_proposal)
        self.repo.append("DECISION", correlation_id, decision)

        # 4. Validate (Safety Kernel)
        validation = self.safety.evaluate(decision, state)
        self.repo.append(
            "VALIDATION", correlation_id, {"safe": validation.safe, "message": validation.message}
        )

        # 5. Actuate & Rollback
        if validation.safe:
            actions_to_apply = validation.clipped_actions
        else:
            actions_to_apply = self.rollback.restore(state)

        if not self.shadow_mode:
            for action in actions_to_apply:
                self.sim.apply_action(action)
                self.repo.append("ACTION_DISPATCHED", correlation_id, action)
        else:
            self.repo.append("SHADOW_MODE_SKIP", correlation_id, actions_to_apply)

        # 6. Process acknowledgments from the adapter (happens next tick, but we record available ones)
        acks = self.sim.acknowledge()
        for ack in acks:
            self.repo.append("ACKNOWLEDGEMENT", ack.command_id, ack)
