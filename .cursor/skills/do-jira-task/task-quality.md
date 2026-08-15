# Task quality (Jira culture)

Living checklist for how HOSPA/SHEYE tickets should look so `/do-jira-task` can pass the context gate without guessing. Grow this file from sprint retros — one bullet per repeated gap.

## Minimum ticket shape

1. **Summary** — outcome, not activity (“Воронка апсейла шаблонов на дашборде”, not “посмотреть события”).
2. **Description** — goal, scope, DoD, links. Comments are history; durable decisions move into description.
3. **Components** — BI / ETL / Discovery / DataOps / Docs (drives gate section).
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

### Docs

- Source + publish location + format

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

### 2026-08-10 — HOSPA-1398
- Gap: dual screen/source entry keys without documented multiIf order → room SHOWN mislabeled as main.
- Rule added: for BI funnels with screen+source, require explicit precedence in description/PLAN.
- Gap: event list lived only in comments; dash Upsale thin in analytics-context.
- Rule added: promote event map + chart decisions to description before Done; catalog tab docs when new dash tab ships.

