"""Generates markdown reports for hackathon judging."""

from typing import Dict, Any

def generate_markdown_report(comparison: Dict[str, Any], scenario_name: str) -> str:
    """Formats the comparison output into a readable report."""
    
    savings_str = f"+{comparison['savings']['energy_pct']}%" if comparison['savings']['energy_pct'] > 0 else f"{comparison['savings']['energy_pct']}%"
    
    return f"""# AI Performance Report: {scenario_name}

## Summary
The Sentinel Twin AI achieved a **{savings_str}** reduction in HVAC energy consumption compared to the deterministic baseline.

## Metrics

| Metric | Baseline | AI Controller | Delta |
|--------|----------|---------------|-------|
| **Energy (kWh)** | {comparison['baseline']['energy_kwh']} | {comparison['ai']['energy_kwh']} | {comparison['savings']['energy_kwh']} kWh |
| **Comfort Debt** | {comparison['baseline']['comfort_debt']} | {comparison['ai']['comfort_debt']} | {comparison['savings']['comfort_debt_delta']} |

*Comfort Debt is measured in °C-hours of deviation during occupied times.*
"""
