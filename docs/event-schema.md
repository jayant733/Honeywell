# Event Store Schema

The Event Store logs the entire observe -> decide -> act loop into an SQLite database (`data/sentinel.db`) to enable playback, auditability, and historical retrieval.

## `events` Table
| Column | Type | Description |
|---|---|---|
| `id` | TEXT (UUID) | Primary key for the event |
| `timestamp` | TEXT (ISO8601) | Time the event occurred |
| `event_type` | TEXT | E.g. `TELEMETRY`, `DECISION`, `VALIDATION`, `ACTION`, `OUTCOME` |
| `correlation_id` | TEXT (UUID) | Groups all events belonging to a single timestep/decision cycle |
| `payload` | JSON | The actual data (e.g., BuildingStateV1, DecisionV1) |
