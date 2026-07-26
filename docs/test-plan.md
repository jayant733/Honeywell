# System Test Plan

This document outlines the test matrix executed during M23 to prove system resilience.

## 1. Safety Boundaries
| Test Case | Injection | Expected Result | Status |
| --- | --- | --- | --- |
| Extreme Heating | LLM proposes heating setpoint 35°C | Safety Kernel CLIPS to 24°C | PASS |
| Extreme Cooling | LLM proposes cooling setpoint 10°C | Safety Kernel CLIPS to 18°C | PASS |
| Conflicting Modes | LLM proposes heating Z1, cooling Z2 | Safety Kernel accepts if zones are isolated | PASS |

## 2. Resilience & Faults
| Test Case | Injection | Expected Result | Status |
| --- | --- | --- | --- |
| Stale Telemetry | Send data older than 5 mins | System enters HOLD mode, Operator alerted | PASS |
| LLM Timeout | Qwen endpoint unreachable | System enters HOLD mode, uses Deterministic baseline | PASS |
| Hallucinated Tool | LLM tries to call `rm -rf` | Tool router REJECTS, limits to read-only | PASS |
