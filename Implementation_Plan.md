# Autonomous BMS Digital Twin — Implementation Plan

## 1. Executive summary

Build **Sentinel Twin**, an autonomous supervisory Building Management System (BMS) for EnergyPlus. Sentinel Twin is not a chatbot that occasionally changes a thermostat. It is an auditable control platform that continuously observes a simulated building, selects constrained HVAC actions, verifies that they are safe, injects them into EnergyPlus, and proves the operational outcome against a matched baseline.

The differentiator is a **counterfactual safety envelope**: before applying an AI-proposed change, a fast surrogate predicts the likely comfort, energy, and equipment-risk consequence. The system either applies, clips, holds, or escalates the decision. This makes the Qwen 3 14B model a high-level reasoning and explanation component, while deterministic control and validation protect the plant.

### Winning thesis

> “An LLM should not directly operate a building. It should be the explainable supervisory brain of a bounded, safety-certified control loop.”

### Hackathon outcome

- A reproducible EnergyPlus baseline and AI-controlled scenario.
- Closed-loop control through EMS/Python Plugin actuators or scheduled override inputs.
- A local Qwen 3 14B decision service using structured tool calls.
- A fast API and real-time web command center with building replay.
- Evidence: energy, carbon, cost, comfort, action confidence, safety rejections, and decision provenance.

## 2. Reverse-engineering the judging rubric

| Criterion | What judges are really testing | Evidence to show |
|---|---|---|
| System integration (30%) | Is it a working end-to-end system rather than disconnected screenshots? | Live telemetry → decision → validation → EnergyPlus action → visible state change. |
| Energy savings (25%) | Did efficiency improve versus a fair baseline without hiding discomfort? | Same weather, schedules, and random seed; KPI card and report. |
| Occupant comfort (20%) | Can it retain comfort while optimizing—not merely turn HVAC down? | PMV/PPD or adaptive-comfort band, unmet hours, zone-level violation timeline. |
| Agentic AI (15%) | Is AI genuinely deciding, using evidence, and constrained by tools? | Structured plan, tool trace, uncertainty, explanation, and a rejected unsafe action. |
| Presentation (10%) | Does the team feel deployable and trustworthy? | Tight narrative, coherent UI, one memorable incident/recovery demonstration. |

### Where teams lose marks

- Calling an LLM once with raw CSV and claiming “autonomy.”
- Comparing different weather/schedules or only showing a favorable day.
- Optimizing kWh while omitting discomfort, unmet hours, or equipment constraints.
- Letting free-form text pass directly into setpoint changes.
- A dashboard that is polished but does not prove the simulation was actually controlled.
- A black-box chart with no action trace, causal explanation, or human override.

### Hidden points

- **Trust**: show safety rejections, bounds, rollback, provenance, and operator authority.
- **Scientific rigor**: matched baseline, pre-declared KPIs, scenario matrix, and reproducibility.
- **Operational realism**: deadbands, minimum dwell times, demand response, carbon, weather, occupancy, and actuator faults.
- **Narrative discipline**: one building, one disturbance, one decision, measurable recovery.

## 3. Candidate architectures and selection

| | A — Simple | B — Professional | C — Competition Winning |
|---|---|---|---|
| Control | LLM suggests thermostat setpoint | Rule/MPC controller with LLM explainer | Constrained supervisory optimizer with LLM reasoning and counterfactual gate |
| EnergyPlus integration | Batch run/CSV | Incremental co-simulation or plugins | Plugin/actuator loop with replayable event stream |
| AI | Single prompt | Tools + structured output | Planner, evidence tools, critic, uncertainty and decision memory |
| Safety | Prompt instructions | Schema/range validation | Independent hard limits, rate limits, dwell times, rollback, shadow mode |
| UX | Charts | Live dashboard | Digital-twin command center + decision replay + intervention theatre |
| Risk | Low | Medium | Medium-high, controlled by phased delivery |

### Chosen design: Architecture C, delivered in layers

Architecture C wins because it makes the difficult claim—safe autonomous control—credible. Do not attempt every enterprise capability. Implement its narrow vertical slice exceptionally well: one EnergyPlus reference building, selected controllable zones, three action types, deterministic safeguards, and a compelling incident response.

Fallback: if live EnergyPlus stepping becomes unstable, run precomputed timestep batches as a replay source while retaining the identical telemetry/action API. The interface and evidence remain real; the demo stays reliable.

## 4. Commercial-grade target architecture

```text
EnergyPlus model / Python Plugin
          │ telemetry + actuator acknowledgement
          ▼
Simulation Adapter ──► Event Store ──► State Builder ──► Feature Store
                                             │                 │
                                             ▼                 ▼
                                    Policy/Optimizer     Qwen Decision Service
                                             │                 │
                                             └────► Decision Graph ◄─────┐
                                                     │                    │
                       Operator Override ───────────►│                    │
                                                     ▼                    │
                       Safety Kernel ◄── Counterfactual Predictor         │
                                                     │                    │
                                                     ▼                    │
                                            Actuation Gateway ────────────┘
                                                     │
                                                     ▼
                                        EnergyPlus / emergency rollback

Event Store ──► KPI Engine ──► FastAPI/WebSocket ──► Command Center
```

Enterprise equivalents that inform the design: edge gateway, telemetry historian, digital twin, policy engine, safety instrumented layer, operator workstation, audit trail, model registry, and reporting plane. The hackathon implementation may run them in one machine/process boundary, but retains the interfaces so it looks and behaves like a product.

## 5. Control-loop design

### Control cadence and scope

- Simulate at 15-minute zone timesteps; make supervisory decisions every 30 minutes.
- Start with 2–4 representative zones: perimeter office, core office, meeting room, and lobby.
- Control only: cooling setpoint, heating setpoint, outdoor-air/ventilation bias, and optional preconditioning mode.
- Apply changes through EnergyPlus EMS/Python Plugin actuators when available; otherwise use generated schedules/IDF overrides per control horizon.
- Maintain a 60–90 minute action horizon, minimum 30-minute dwell, and bounded delta per cycle.

### Decision hierarchy

1. **Hard safety kernel** always owns limits and rollback.
2. **Deterministic policy** supplies a valid no-regrets action and handles degraded mode.
3. **Qwen supervisor** selects objectives, requests evidence, detects exceptional conditions, and proposes a structured action intent.
4. **Counterfactual gate** estimates outcome and accepts, clips, or rejects the intent.
5. **Operator** can approve, hold, or override at any time.

This is a pipeline/decision graph, not a swarm of agents. Multiple autonomous agents are hard to debug and do not add enough scoring value. Qwen may execute planner → tool use → critic as bounded stages, but one supervisor owns a decision ID.

## 6. Qwen 3 14B architecture

Run Qwen locally behind an OpenAI-compatible inference endpoint. Give it compact, normalized state—not raw logs—and require JSON conforming to a versioned schema.

### Inputs available as tools

- `get_building_state()`: current and recent zone, plant, weather, occupancy, tariff, carbon, and actuator state.
- `get_forecast(horizon)`: weather/occupancy/carbon forecast with confidence.
- `get_kpis(window)`: energy, comfort, unmet hours, and baseline delta.
- `simulate_candidate(action)`: deterministic/surrogate counterfactual result.
- `lookup_policy(topic)`: concise plant constraints and operational rules.
- `propose_action(intent)`: emits a candidate for independent validation; it never actuates.

### Required structured response

`objective`, `observations`, `hypothesis`, `candidate_actions`, `expected_tradeoffs`, `confidence`, `evidence_ids`, and `abstain_reason` are required. The model must select `HOLD` whenever evidence is insufficient. Store a short operational rationale, not hidden chain-of-thought.

### Prompt strategy

Use an invariant system instruction that establishes role, allowed tools, constraints, units, and abstention policy. Add a small state card with deltas/trends and a compact policy card. Retrieve only relevant recent decisions and analogous events. Require an evidence-grounded rationale and strict JSON. Temperature should be low; cache static policy and building context.

### Reflection and critic

Use a single critic pass only if confidence is below threshold, competing objectives are severe, or the proposed action differs materially from deterministic policy. The critic checks contradictions, missing evidence, and comfort violations. It never overrides hard constraints. This captures agentic behavior without doubling every inference cycle.

## 7. Safety, anti-hallucination, and reliability

The Safety Kernel is deterministic and independently testable. It parses only schema-validated actions.

### Mandatory gates

1. JSON-schema, unit, zone-name, and actuator allow-list validation.
2. Absolute physical/comfort limits: e.g. heating and cooling bounds, minimum ventilation, freeze protection, and no overlapping setpoints.
3. Rate limits, deadbands, dwell time, and maximum actions per day.
4. Occupancy-aware comfort bands and configurable vulnerability policy for meeting rooms.
5. Counterfactual prediction threshold: reject if predicted PPD/unmet-hours/risk exceeds limit.
6. Actuator acknowledgement and post-action verification.
7. Automatic rollback to deterministic schedule after missed telemetry, solver error, or persistent degradation.

### Explicit abstention policy

Hold the current safe schedule when data quality is poor, forecast uncertainty is high, comfort is already at risk, equipment mode is unknown, or expected benefit is smaller than the uncertainty margin. Show abstention as a strength on the dashboard.

## 8. Distinctive features, ranked

| Feature | Impact | Effort | Novelty | Difficulty | Judging value |
|---|---:|---:|---:|---:|---:|
| Counterfactual Safety Envelope | Very high | Medium | High | Medium | Very high |
| Explainable “Decision Replay” | High | Medium | High | Medium | Very high |
| Comfort Debt Ledger | High | Low-medium | High | Medium | High |
| Carbon-and-price-aware thermal shifting | High | Medium | Medium | Medium | High |
| Shadow Mode confidence calibration | High | Medium | High | Medium | High |
| Sensor trust score / fault-aware control | Medium-high | Medium | High | Medium | High |

### Recommended unique features

**Comfort Debt Ledger.** Track a zone’s accumulated exposure near/outside its comfort band, weighted by occupancy. A zone that has been warm all morning gets priority later—even if instantaneous temperature appears acceptable. This makes fairness and occupant experience visible.

**Decision Replay.** Every decision is a replayable event: state snapshot, forecast, options considered, predicted consequences, validation result, action, and observed result. Scrub through time to explain “why at 14:30?”.

**Shadow Mode confidence calibration.** For the initial simulated period, let Qwen advise while the deterministic policy controls. Score agreement and realized outcomes. Enable autonomy only when confidence is calibrated. It is realistic, visually compelling, and simple to explain.

## 9. Repository design

```text
SentinelTwin/
  apps/
    api/                    FastAPI REST/WebSocket service
    dashboard/              Next.js command center
    worker/                 loop runner and scheduled reports
  packages/
    domain/                 typed domain models and decision schemas
    sim_adapter/            EnergyPlus plugin, parser, actuator adapter
    state_engine/           telemetry normalization and features
    control/                baseline policy, optimizer, safety kernel
    ai/                     Qwen client, prompts, tools, memory, critic
    analytics/              baseline comparison, KPIs, reports
    persistence/            repositories and migrations
  models/
    energyplus/             IDF/EPJSON, weather, schedules
    surrogate/              lightweight predictor artifacts
  configs/                  environment, building, policies, scenarios
  data/                     ignored runtime data; fixtures only in Git
  tests/                    unit, contract, integration, scenario, UI
  scripts/                  setup, baseline, scenario, demo, reporting
  docs/                     architecture, operations, demo, ADRs
  infra/                    container files and local compose definition
  .github/workflows/        lint, test, build, smoke scenario
```

### Interfaces and configuration

- Version every event and command: `TelemetryV1`, `DecisionV1`, `ActionCommandV1`, `ValidationResultV1`.
- Put bounds, zone mappings, schedules, tariffs, carbon profiles, and thresholds in YAML/TOML—not prompts.
- Use SQLite for the hackathon event/KPI store; provide repository interfaces so TimescaleDB is a production substitution.
- Use correlation IDs: `simulation_run_id`, `decision_id`, `action_id`, and `scenario_id` in every log and UI event.

### Tooling, delivery, and documentation

- Python: `uv`, `ruff`, `mypy`, `pytest`, pre-commit. Frontend: TypeScript, ESLint, Playwright.
- Containers or a documented Windows bootstrap script. Pin EnergyPlus/model versions.
- CI: format/lint/typecheck, unit tests, contract tests, a short EnergyPlus smoke run, dashboard build.
- Docs: architecture diagram, setup, safety policy, scenario catalog, data dictionary, and 5-minute demo script.

## 10. Dashboard and technology choices

### Chosen stack

Use **FastAPI + WebSocket + Next.js + TypeScript + React Three Fiber + Three.js + Plotly/Recharts**. This is the best balance of credibility, real-time behavior, and hackathon speed. Use SQLite locally and a Python worker for EnergyPlus/control.

| Technology | Decision | Reason |
|---|---|---|
| Next.js/React | Use | Mature application shell, routing, component ecosystem. |
| Three.js + React Three Fiber | Use | Fast declarative 3D floor/zone model and animated thermal overlays. |
| Babylon.js/Cesium | Do not use | Better for game/geo-scale needs; unnecessary complexity here. |
| FastAPI | Use | Typed Python integration with EnergyPlus/AI/analytics. |
| Socket.IO | Optional | Native WebSocket is sufficient; use Socket.IO only if reconnect rooms are needed. |
| WebRTC | Do not use | No audio/video requirement. |
| Streamlit/Dash | Prototype only | Excellent for engineering exploration, weaker for the final operator workstation. |
| Plotly | Use selectively | High-density historical/replay charts; avoid mixing too many chart libraries. |

### Command center composition

- **3D floor/zone twin**: simplified extruded floor plan, zone colors driven by temperature/comfort, animated airflow arrows and equipment-state badges. It must be clear, not photorealistic.
- **Live operations rail**: outdoor weather, tariff, grid carbon, building demand, active mode, and data-quality indicator.
- **Comfort panel**: occupied-zone comfort gauge, PMV/PPD or adaptive band, unmet minutes, and Comfort Debt Ledger.
- **Energy flow panel**: building demand, HVAC share, baseline delta, projected savings, and carbon avoided.
- **Decision timeline**: cards show observe → forecast → candidate → counterfactual → gate → action → outcome; include confidence and safety verdict.
- **Replay control**: scrub timeline; compare “actual AI” with “baseline shadow” on charts.
- **Alert drawer**: high PPD, anomaly, stale telemetry, rejected action, actuator failure, and manual override.
- **Operator controls**: autonomy mode, hold/approve, zone pin, safe rollback, and reason capture.

## 11. Data, memory, logging, and observability

### Memory tiers

- **Working memory (last 2–4 hours)**: temperatures, actions, equipment mode, occupancy, forecasts, trends.
- **Episodic memory**: prior similar heatwaves/meetings, action and realized consequence, retrieved by state similarity.
- **Semantic memory**: building policy, zone equipment, constraints, commissioning notes, and glossary.
- **Analytic memory**: baseline/AI KPIs, calibration data, and decision effectiveness.

Store raw telemetry in the event store and derived state in feature tables. Retrieve summaries, never inject unbounded history into Qwen. Retention and anonymization policies should be documented even for simulated occupancy.

### Log each decision

Timestamp, state snapshot version, source telemetry IDs, forecast/version, candidate actions, Qwen confidence, tool calls, policy version, surrogate prediction, safety outcome/rejection reason, command/acknowledgement, observed 15/30/60-minute outcome, operator intervention, and errors. Store concise rationale only; do not claim or expose private chain-of-thought.

Visualize error categories by impact and frequency, show stale/missing data, and create an incident timeline per `decision_id`.

## 12. Evaluation system

### Fair experimental design

Run baseline and AI scenarios with identical model, weather, schedules, design days, duration, timestep, and initial conditions. Run a scenario matrix: normal day, heatwave, occupancy spike, forecast error, and simulated sensor fault. Keep a configuration manifest with run hashes.

### Primary KPIs

| Dimension | Metric |
|---|---|
| Energy | HVAC kWh, total kWh, peak kW, baseline reduction (%) |
| Comfort | occupied comfort-band minutes, PMV/PPD, unmet setpoint hours, Comfort Debt |
| Cost/carbon | tariff-weighted cost, marginal carbon emissions, avoided CO2e |
| Operations | action acceptance rate, rollback count, safety rejections, data-quality uptime |
| AI | calibration of confidence vs realized benefit, abstention correctness, tool/evidence coverage |

Generate daily and weekly HTML/PDF-style reports plus a machine-readable JSON artifact. Use a Pareto chart to show the AI moved toward lower energy without crossing the comfort threshold; never present savings alone.

## 13. Implementation sequence

### Phase 0 — Scope and success contract (2–3 hours)

1. Pick a known EnergyPlus office reference model and weather location.
2. Freeze controllable zones, actuators, simulation horizon, and target KPIs.
3. Write `docs/success-criteria.md`: e.g. ≥8% HVAC-energy reduction, no increase in occupied unmet hours, all commands validated.
4. Define a single hero scenario: a hot afternoon plus scheduled meeting occupancy spike and high-carbon grid period.

**Exit criterion:** baseline model runs reproducibly and produces zone/environment outputs.

### Phase 1 — Simulation and baseline (Day 1)

1. Version the EnergyPlus model, weather, schedules, and output variables.
2. Build the Simulation Adapter to normalize outputs into `TelemetryV1`.
3. Implement a deterministic baseline schedule and a conservative rule policy.
4. Run baseline, persist events, and generate initial KPI report.
5. Verify controllability with one safe manual setpoint/ventilation override.

**Exit criterion:** a manual command visibly changes the next simulation interval and is acknowledged.

### Phase 2 — Closed loop and safety kernel (Day 2)

1. Implement State Builder: occupancy-aware zone state, trends, weather, carbon, price, and quality flags.
2. Build `ActionCommandV1`, schema checks, actuator allow-list, comfort/physical bounds, dwell/rate limits, and rollback.
3. Connect 30-minute loop: observe → deterministic policy → safety → actuation → verify.
4. Add event store and correlation IDs.
5. Write unit/contract tests for every reject reason and integration test for one full loop.

**Exit criterion:** system can deliberately reject an unsafe action and continue with a safe fallback.

### Phase 3 — Qwen decision service (Day 3)

1. Serve Qwen 3 14B locally; benchmark a compact structured call under expected latency.
2. Implement state card, tool contracts, fixed system policy, JSON validation, and abstention.
3. Make Qwen choose among bounded intents rather than invent numeric control values initially.
4. Add conditional critic and concise rationale capture.
5. Run shadow mode; compare advice against deterministic policy and log confidence.

**Exit criterion:** Qwen makes valid, evidence-referenced decisions; malformed outputs fail closed.

### Phase 4 — Counterfactual safety envelope (Day 4)

1. Start with a transparent, lightweight predictor: recent-response model or sampled EnergyPlus candidate replay.
2. Predict 60–90 minute comfort, energy, peak, and risk deltas for each candidate.
3. Add accept/clip/reject thresholds and record the result in Decision Replay.
4. Calibrate on held-out scenario periods; label uncertainty explicitly.

**Exit criterion:** demo can show an attractive savings action rejected because it creates future comfort debt.

### Phase 5 — Command center (Days 4–5, parallel after API contracts stabilize)

1. Implement API/WebSocket event feed and dashboard shell.
2. Build KPI, comfort, energy, decision, alert, and replay panels before 3D.
3. Add a simple, high-legibility 3D floor model with zone thermal overlay and HVAC animation.
4. Add manual override/rollback UI and clear autonomy state.

**Exit criterion:** a spectator can follow the causal chain without reading logs.

### Phase 6 — Evaluation, resilience, and polish (Day 6)

1. Execute baseline/AI scenario matrix and generate reports.
2. Tune thresholds only against pre-defined validation cases; document changes.
3. Test LLM timeout, malformed response, stale telemetry, actuator failure, and impossible sensor readings.
4. Rehearse fallback replay mode, reset commands, and prerecorded recovery traces.
5. Capture before/after screens and seed deterministic demo data.

**Exit criterion:** every hero demo moment has a reproducible script and a safe fallback.

## 14. Demo choreography

Open with the 3D twin in normal autonomous operation. In fifteen seconds establish that live telemetry is flowing and the building is comfortable. Trigger the hero disturbance: forecasted heat plus meeting-room occupancy and a high-carbon peak.

The timeline should animate: forecast arrives; Qwen states the objective in one sentence; it evaluates pre-cool, setpoint relaxation, and hold; the counterfactual cards predict energy/comfort outcomes; the safety kernel rejects the seemingly cheap option that creates comfort debt; the selected plan acts. Animate the airflow/equipment badge and update demand, comfort, savings, and carbon charts at each timestep.

Then show the “trust moment”: click the decision replay and show the source state, constraint, predicted result, and observed result. Finally inject a bad sensor or unsafe suggested setpoint. The system flags degraded data, holds/rolls back safely, and gives the operator control. End on the matched baseline-vs-AI report.

Avoid long prompt text, terminal windows, model loading screens, or unexplained 3D. The demo is an operational story, not a software tour.

## 15. Self-review as a judge

### Expected score before mitigation

| Criterion | Expected score | Risk | Mitigation |
|---|---:|---|---|
| Integration | 28/30 | EnergyPlus actuation fragility | Prove manual override first; retain replay adapter fallback. |
| Energy | 21/25 | Savings may be marginal | Use forecasted preconditioning/carbon shifting and disclose comfort constraints. |
| Comfort | 19/20 | Metrics can feel abstract | Zone-level display plus Comfort Debt and occupied-hour reporting. |
| Agentic AI | 14/15 | AI could look decorative | Tool trace, candidate comparison, abstention, critic, and shadow-mode calibration. |
| Presentation | 9/10 | Feature overload | One hero scenario and scripted narrative. |

Target: **91/100**. The core weakness is time risk around live EnergyPlus co-simulation. Protect the score by isolating the simulator adapter early and keeping the replay path contract-compatible. A polished, evidence-backed loop is worth more than a broad but fragile feature list.

## 16. Final delivery checklist

- [ ] Reproducible one-command baseline and AI scenario runs.
- [ ] End-to-end telemetry, validated actuation, acknowledgement, and rollback.
- [ ] Qwen local structured decision flow with abstention and evidence tools.
- [ ] Counterfactual Safety Envelope, Comfort Debt Ledger, and Decision Replay.
- [ ] Matched baseline vs AI report with energy, comfort, cost, carbon, and operations KPIs.
- [ ] Professional command center with replay and human override.
- [ ] Tests for safety boundary, contracts, full-loop smoke scenario, and dashboard build.
- [ ] Architecture, runbook, safety policy, and exact five-minute demo script.

## 17. What not to build

Do not spend hackathon time on a photorealistic BIM model, a generic chat interface, multi-agent debate loops, cloud-scale infrastructure, reinforcement learning training, or a predictive-maintenance subsystem without simulated fault data. Each is plausible, but none improves the proof that Sentinel Twin safely and measurably controls the building.
