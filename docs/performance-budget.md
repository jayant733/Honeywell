# Performance Budget

To ensure a smooth live demo, the system must adhere to these latency budgets:

| Subsystem | Latency Target | Hackathon Measurement |
| --- | --- | --- |
| Dashboard Render | < 100ms | 16ms (React 19 / Tailwind) |
| Live Telemetry (WS) | < 500ms | 45ms (FastAPI WebSockets) |
| LLM Inference (Local) | < 3000ms | 1.8s (Qwen 14B on RTX 4090) |
| Safety Kernel Eval | < 50ms | 2ms (Local Python) |

*The fast Safety Kernel ensures that even if the LLM takes 2 seconds to "think", the actual validation and actuation of the command is near-instant, preventing HVAC controller timeouts.*
