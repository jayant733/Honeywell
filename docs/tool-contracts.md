# AI Tool Contracts

This defines the allowed interactions the AI model can have with the Building Management System.

## Bounded Read-Only Tools

1. **`get_building_state()`**:
   - **Description**: Returns the current normalized building state (zones, temperatures, quality flags).
   - **Input**: None
   - **Returns**: `BuildingStateV1` serialized to JSON.

2. **`get_forecast()`**:
   - **Description**: Returns the upcoming weather or carbon intensity forecast.
   - **Input**: None (for now)
   - **Returns**: JSON object with forecast.

3. **`get_kpis()`**:
   - **Description**: Returns current Key Performance Indicators (comfort debt, energy used).
   - **Input**: None
   - **Returns**: JSON object.

## Action Proposal Tool

The AI is explicitly forbidden from directly calling actuators (e.g. `set_temperature`). Instead, it is only allowed to propose actions. This is handled natively by the structured output schema `DecisionProposalV1`, rather than a standalone tool call. The orchestrator receives the proposal and hands it to the **Safety Kernel**.
