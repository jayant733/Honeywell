# Decision Explanation Policy

When surfacing AI decisions to the dashboard, we must strictly adhere to the following principles to maintain trust:

1. **No Hallucination**: Do NOT ask the LLM to "explain" its decision after the fact. Display the exact JSON output that the AI generated in the `DecisionProposalV1`.
2. **Safety Kernel Supremacy**: The dashboard must clearly delineate between what the AI *proposed* and what the Safety Kernel *permitted*. If an action was clipped or rejected, the Safety Kernel's rationale is the source of truth, not the AI.
3. **Evidence Transparency**: Every decision must link to the specific `BuildingStateV1` timestamp and any `tool_calls` (e.g., weather lookup) that were executed during the decision cycle.
4. **Visibility**: Rejections are not failures; they are a feature. The UI should prominently display "REJECTED" or "CLIPPED" as proof that the guardrails work.
