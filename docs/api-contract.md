# Sentinel API Contract

The FastAPI backend provides REST endpoints for historical data and control, and WebSockets for live 1Hz telemetry.

## REST Endpoints

- `GET /api/state`: Returns the current `BuildingStateV1`.
- `GET /api/kpis`: Returns the current energy and comfort metrics.
- `GET /api/decisions`: Returns the last 10 AI decisions and safety validations.
- `POST /api/mode`: Sets the global mode (`SHADOW` vs `AUTONOMOUS`).

## WebSocket Endpoints

- `WS /ws/telemetry`: Pushes `BuildingStateV1` JSON every time the simulation ticks.

*Note: No endpoint is allowed to bypass the Safety Kernel.*
