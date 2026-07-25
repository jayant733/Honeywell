from datetime import UTC, datetime

from packages.domain.context import RunContext


def test_run_context_retains_audit_identity() -> None:
    context = RunContext(
        run_id="run-001",
        scenario_id="baseline-hot-day",
        started_at=datetime(2026, 7, 25, tzinfo=UTC),
    )

    assert context.run_id == "run-001"
    assert context.scenario_id == "baseline-hot-day"
