# Task quality (Jira culture)

Living checklist for how HOSPA/SHEYE tickets should look so `/triage-analytics` can pass the [context gate](../../../docs/agents/context-gate.md) without guessing, and `/do-jira-task` can re-score without bouncing. Grow this file from sprint retros — one bullet per repeated gap.

## Minimum ticket shape

1. **Summary** — outcome, not activity (“Воронка апсейла шаблонов на дашборде”, not “посмотреть события”).
2. **Description** — goal, scope, DoD, links. Comments are history; durable decisions move into description.
3. **Components** — primary HOSPA component (drives the [context-gate](../../../docs/agents/context-gate.md) section).
4. **Links** — Metabase / Confluence / Figma / related tickets / sibling repo paths. If none apply, write `n/a` in description.
5. **Need Info** — name who/what is missing and the next meeting/thread; do not leave empty Need Info.

## By type (expectations)

### BI

- Target dash/collection URL
- Grain (users vs devices vs sessions)
- Events **or** warehouse objects named
- Acceptance: screenshots / chart list / “stakeholder signed”

### ETL

- Source + target relations
- Consumer + freshness
- Coverage/volume if incomplete data is expected

### Discovery

- One research question + “enough when…”
- Entry point for lineage

### DataOps

- Scope + safety (copies) + pilot + compare-results test

### Ad-hoc

- One number/question + time range/grain
- Where to look, or “unknown — discovery first”
- Delivery and “enough when…”

### A/B

- Experiment/flag/variants + metric grain
- Exposure source + window/guardrails

### Docs

- Source + publish location + format

### Report

- Audience, artifact location, source charts, sign-off owner

### Goal

- Outcome in one sentence + children or “wrapper only”

## Cross-repo ownership

| Artifact | Prefer owning repo |
|----------|-------------------|
| Metric/dataset contract | mdm |
| CH model | ch_dbt |
| DWS model | dbt-smarthome |
| Metabase catalog note | analytics-context |
| Ad-hoc EDA / ticket scratch | tasks (`hospa_*`) |

If work in `tasks` discovers a lasting rule, flag OUTBOX → owning repo; do not silently patch siblings.

## Sprint learning log


