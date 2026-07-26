# Architecture

Sentinel Twin is designed with a strict separation of concerns, ensuring that the AI can make intelligent proposals without ever compromising the physical safety of the building.

## Core Components

1. **Building State Engine**: Normalizes messy telemetry into a clean `BuildingStateV1`.
2. **AI Decision Engine**: Local Qwen 14B model that evaluates state, weather, and grid carbon to propose HVAC changes.
3. **The Safety Kernel**: A deterministic, hard-coded policy layer. All AI proposals MUST pass through the Kernel. If a proposal is unsafe, it is clipped or rejected.
4. **Command Center UI**: A Next.js 15 App Router frontend featuring live 3D visualization, alert monitoring, and historical playback.

## Data Flow
`Telemetry -> State Engine -> AI Proposal -> Safety Kernel -> Actuation -> Event Store -> UI`
