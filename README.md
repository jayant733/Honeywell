# Sentinel Twin: Autonomous AI Building Management

![Sentinel Twin](docs/assets/banner.png)

Sentinel Twin is a next-generation autonomous Building Management System (BMS) powered by local LLMs (Qwen 14B) and fortified by a deterministic Safety Kernel. It optimizes HVAC energy use, reduces carbon emissions, and maintains comfort—all while guaranteeing absolute operational safety.

## Key Features
- **Local AI Brain**: Private, air-gapped decision making using Qwen 14B.
- **Unbypassable Safety Kernel**: Hard-coded physics limits that cannot be overridden by prompt injection or model hallucination.
- **Carbon & Weather Aware**: Proactively shifts energy loads based on grid carbon intensity.
- **Live 3D Digital Twin**: Executive-grade command center built in Next.js 15.

## Documentation
- [Architecture](docs/architecture.md)
- [Setup Guide](docs/setup.md)
- [Evaluation Protocol](docs/evaluation-protocol.md)
- [Hackathon Pitch](docs/presentation/outline.md)

## Hackathon Demo Execution
To run the fully compliant autonomous pipeline for the judges:

1. **Start the Frontend Dashboard:**
   ```bash
   cd apps/dashboard
   npm run dev
   ```
2. **Start the Live Orchestrator:**
   This script will automatically start the official MCP Server, the PyEnergyPlus Co-Simulation runtime, and the FastAPI backend.
   ```bash
   python scripts/run_live.py
   ```
3. **Verify:**
   Open `http://localhost:3000` to watch the Live EnergyPlus runtime send actual state to the MCP/FastAPI backend, get optimized by the Qwen LLM, and correctly write-back setpoints via the Actuator Gateway.
