# Evaluation Protocol

To prove that the AI-powered BMS provides tangible value, we use a strict counterfactual evaluation protocol.

## Process
1. **Baseline Run**: The simulation is run using a specific weather file (e.g., Summer Heatwave) and the `BaselinePolicy` (deterministic). No AI is used. The outputs are logged to the Event Store under a specific `scenario_id`.
2. **AI Run**: The exact same simulation is run again, but this time in Autonomous Mode where Qwen 14B dictates the HVAC setpoints (gated by the Safety Kernel).
3. **Comparison**: The `KpiEngine` computes aggregate metrics for both runs:
   - **Total HVAC Energy (kWh)**
   - **Total Comfort Debt (°C-hours)**: The sum of temperature deviations from the ideal comfort band during *occupied* hours.
   - **Carbon Emissions (kgCO2)**
4. **Report**: The `compare_runs` module generates a JSON/Markdown report proving the net savings (or loss) of the AI over the Baseline.

This strict A/B testing approach ensures that the AI cannot "cheat" by modifying weather or occupancy schedules.
