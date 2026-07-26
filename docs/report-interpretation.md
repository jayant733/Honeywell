# Report Interpretation Guide

The Executive Analytics Report compares the AI (Sentinel Twin) against the baseline (Deterministic Controller).

## Key Metrics Explained

1. **Comfort Debt (°C-hours)**:
   - This measures how much time a zone spent outside the optimal temperature band (21°C - 24°C), multiplied by the severity of the deviation.
   - **Important**: It is *only* measured during occupied hours. Drifting to 18°C overnight when empty incurs 0 debt.
   
2. **Energy Savings (%)**:
   - The reduction in HVAC power draw compared to the baseline over the same exact weather profile.
   
3. **The Trade-Off (Pareto Frontier)**:
   - Perfect comfort usually requires maximum energy. The AI's objective is to reduce energy *without* significantly increasing Comfort Debt. 
   - A successful run is one where Energy is reduced by >10% while Comfort Debt remains roughly equal to the baseline.
