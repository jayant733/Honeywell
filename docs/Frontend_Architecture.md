# Sentinel Twin frontend architecture

## Product direction

The command center is a Honeywell Forge-style operational workstation: calm, premium,
precise, and evidence-led. It is not a generic admin dashboard. Every visual answers
one of three operator questions: *Is the building safe? What changed? What should I do?*

## Stack and structure

Use Next.js 15, React 19, TypeScript, Tailwind, shadcn/ui, Motion, React Three Fiber,
TanStack Query, Socket.IO, Plotly, and Recharts.

```text
apps/dashboard/
  app/(operations)/{overview,twin,telemetry,ai,analytics,replay}/page.tsx
  components/{shell,metrics,status,timeline,inspector}/
  features/{twin,analytics,decisions,replay}/
  lib/{api,socket,theme,formatters}/
  hooks/{useLiveEvents,useEvaluationReport,useCommandPalette}/
```

TanStack Query owns REST/report state; a small Zustand store owns layout, selected
zone, replay time, and inspector state. Socket events update query caches. Use API
schemas shared from the backend, never ad-hoc chart payloads.

## Design system

Typography: Inter or Geist, 12/14/16/20/28/36px scale. Use an 8px spacing grid;
card radii 12px, controls 8px, compact data cells 6px. Surfaces are layered charcoal
in dark mode and warm-white in light mode; reserve glass for floating inspector,
command palette, and timeline only. Shadows are low-opacity and directional.

| Token | Use | Rationale |
|---|---|---|
| `--bg` | application canvas | low-glare operational focus |
| `--surface` | cards/panels | hierarchy without visual noise |
| `--energy` | kWh and demand | electric cyan-blue is distinct from AI |
| `--comfort` | comfort state | teal communicates stability |
| `--carbon` | emissions | muted green, never implies safety |
| `--ai` | autonomous decisions | restrained violet, not neon |
| `--warning` / `--danger` | intervention states | amber/red reserved for action |

All state colors meet WCAG AA on their surface. Icons, labels, and patterns accompany
color. Motion uses 160ms hover, 220ms panel transitions, 320ms page transitions,
and `cubic-bezier(.2,.8,.2,1)`; respect reduced-motion settings.

## Shell and screen hierarchy

```text
Top bar: building selector | scenario | autonomy state | connection | command palette
Left rail: Overview / Twin / Telemetry / AI / Analytics / Replay
Main canvas: route content
Right inspector: selected zone, decision, sensor, or report detail
Bottom timeline: live/replay cursor and event markers
```

Overview is a bento grid: building health and AI state first; energy/comfort/carbon
outcomes second; alerts and forecast third. Analytics consumes Milestone 11 reports:
baseline/current comparison, savings, peak delta, comfort delta, cost, and carbon.
It must visibly warn when a comparison manifest is invalid.

Twin uses an intentionally simple floor model, thermal overlay, selected-zone outline,
and airflow/equipment animation. Render only visible zones, instanced sensor markers,
and throttled live updates to retain 60 FPS. Use Plotly for dense/replay time series,
Recharts for compact KPI trends, and React Flow only for AI decision graphs.

## Key interaction flows

`Live event → Socket service → query cache → metric/twin/timeline update`.

`Analytics report → report card → inspector drilldown → source manifest + KPI formula`.

`Zone click → selected-zone store → inspector + timeline filter + thermal focus`.

Fullscreen presentation mode hides navigation, enlarges the twin and decision timeline,
and preserves alert visibility. Keyboard shortcuts: `⌘K` command palette, `R` replay,
`F` fullscreen, `Esc` deselect. On tablet, inspector becomes a sheet; mobile provides
summary and alerts rather than full 3D operations.
