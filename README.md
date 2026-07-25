# Sentinel Twin

Sentinel Twin is an auditable, closed-loop Building Management System digital twin.
It observes an EnergyPlus building simulation, uses a constrained local Qwen 3 14B
supervisor to propose actions, validates them in an independent safety layer, and
measures energy and comfort results against a reproducible baseline.

## Current status

Milestone 1 is complete: the repository, configuration, engineering quality gates,
and environment diagnostics are in place. Simulation, control, AI, and dashboard
features are implemented in later milestones.

## Repository map

```text
apps/       Deployable API, worker, and dashboard applications
packages/   Shared domain, simulation, state, control, AI, and analytics packages
models/     Versioned EnergyPlus model assets (not generated outputs)
configs/    Non-secret, versioned runtime policy and building configuration
scripts/    Windows bootstrap and diagnostic scripts
tests/      Unit, contract, integration, scenario, and UI tests
docs/       Architecture, runbooks, and decisions
```

## Local setup

1. Install Python 3.11 or later, Git, and EnergyPlus.
2. Copy `.env.example` to `.env` and set `ENERGYPLUS_PATH` if it is not on `PATH`.
3. Run `powershell -ExecutionPolicy Bypass -File scripts/check_environment.ps1`.
4. Create a virtual environment and install development tools:

   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   python -m pip install pytest ruff mypy
   ```

5. Run `python -m pytest`, `python -m ruff check .`, and `python -m mypy packages`.

The Qwen service is optional at this milestone. The diagnostic script reports its
availability without failing the foundational setup check.

## Planning documents

- [Architecture and implementation strategy](Implementation_Plan.md)
- [Execution roadmap](Milestones.md)

## Safety posture

No user interface or AI component will gain direct simulator actuation rights.
Future milestones route every command through a deterministic safety kernel.
