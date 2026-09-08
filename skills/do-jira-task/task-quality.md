# Task quality (Jira culture)

Living checklist for how issue-tracker tickets should look so `/triage-analytics` can pass the context gate without guessing, and `/do-jira-task` can re-score without bouncing. The gate is `docs/agents/context-gate.md`, declared in `SKILL.md` under *Requires from the consuming repo*. Grow this file from sprint retros — one bullet per repeated gap.

## Minimum ticket shape

1. **Summary** — outcome, not activity (“Checkout funnel on the revenue dashboard”, not “look at events”).
2. **Description** — goal, scope, DoD, links. Comments are history; durable decisions move into description.
3. **Components** — primary tracker component (drives the context-gate section).
4. **Links** — Metabase / Confluence / Figma / related tickets / sibling repo paths. If none apply, write `n/a` in description.
5. **Needs-info** — name who/what is missing and the next meeting/thread; do not leave an empty waiting-on-requester status.

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
| Metric/dataset contract | semantic layer / metrics repo |
| ClickHouse model | ClickHouse dbt project |
| Warehouse mart | warehouse dbt project |
| Metabase catalog note | dashboard catalog |
| Ad-hoc EDA / ticket scratch | consuming repo (`{issue-key}/`) |

If work in the consuming repo discovers a lasting rule, flag OUTBOX → owning repo; do not silently patch siblings.

## Sprint learning log


