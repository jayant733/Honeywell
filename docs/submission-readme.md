# Sentinel Twin — Final Submission

**Track:** Advanced AI & Infrastructure
**Team:** Antigravity

## The Problem
Commercial buildings waste 30% of their HVAC energy. Existing AI solutions are treated as "black boxes" that facility managers don't trust, because an AI hallucination could freeze pipes or cook server rooms. 

## What We Built
Sentinel Twin is a local, autonomous Building Management System (BMS) powered by **Qwen 14B**. 
We solved the trust problem by introducing the **Safety Kernel**: an un-bypassable, deterministic physics engine. 

The AI acts as an advisor. It reads weather forecasts, grid carbon intensity, and telemetry to propose HVAC optimizations. The Safety Kernel evaluates those proposals in milliseconds. If the AI hallucinates an unsafe temperature, the Kernel clips the action to physical limits and logs the rejection. 

## Features
- **Carbon-Aware Pre-Cooling**: Shifts HVAC loads to hours when grid energy is clean.
- **Safety Kernel**: Absolute physical limits applied to all LLM output.
- **Time-Travel Auditing**: Rewind the dashboard to see exactly what evidence the AI had during a past decision.
- **Natural Language Operator**: Safely request building changes via chat.

## Repository Guide
We built this across 28 distinct milestones. Our Git history is fully documented.
- `apps/dashboard`: Next.js 15 Command Center.
- `apps/api`: FastAPI backend and WebSockets.
- `packages/control`: The Safety Kernel and Carbon Policies.
- `packages/ai`: Qwen 14B integration and tool routers.

We are ready to present!
