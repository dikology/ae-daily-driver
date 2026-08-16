# Context gate

Fail-closed checklist. Score each item: `ok` | `missing` | `n/a`.

Shared by `/triage-analytics` (fill until pass — primary) and `/do-jira-task` (re-score; bounce on fail). Do not duplicate this list inside either skill.

**Gate result**

- **pass** — no `missing` on required items for this component type. Triage: `ready-for-agent`. Execute: Plan.
- **thin** — goal/DoD mostly clear, but 1–2 non-blocking gaps. Triage: `ready-for-human`, or `ready-for-agent` only if remaining gaps cannot block the brief. Execute: Plan with gaps; Execute only independent steps.
- **blocked** — any required item is `missing`, or status is Need Info without a written resolution path. Triage: grill or `needs-info`. Execute: bounce to `/triage-analytics`. Do not Execute.

Mark blockers with `BLOCKER:` in triage notes and in PLAN.md Gaps.

---

## Universal (every ticket)

| # | Check | Required |
|---|--------|----------|
| U1 | Goal clear from description + comments (not summary alone) | yes |
| U2 | Non-goals or out-of-scope stated, or explicitly “none” | prefer |
| U3 | Definition of Done is verifiable (artifact + acceptance) | yes |
| U4 | Stakeholder / requester known if clarification needed | prefer; **yes** if Need Info |
| U5 | Links present or marked n/a: Metabase / Confluence / Figma / sibling path / contract | yes (each must be link or n/a) |

Issue type **Bug** still uses Universal plus the matching component section (often ETL). Reproduction belongs in triage verify, not as a substitute for these rows.

---

## By component

Use the HOSPA component(s) from triage. If multiple, apply **all** matching sections. Never invent a component.

### BI

| # | Check |
|---|--------|
| B1 | Target dashboard and/or collection (URL or id) |
| B2 | Metric grain (user / device / session / other — named) |
| B3 | Event map **or** warehouse model/table named (not both empty) |
| B4 | Funnel/chart list or “single KPI” stated |
| B5 | Filters / segments / platforms in scope |

### ETL

| # | Check |
|---|--------|
| E1 | Source relation (schema.table or system + owner) |
| E2 | Target relation / delivery (warehouse, cloud path, consumer API) |
| E3 | Freshness / update cadence |
| E4 | Consumer named (who reads the result) |
| E5 | Volume / coverage expectation if completeness matters |

### Ad-hoc

| # | Check |
|---|--------|
| A1 | Number or question in one sentence |
| A2 | Time range, grain, and filters |
| A3 | Where to look (model / table / dashboard) or “unknown — discovery first” |
| A4 | Delivery and “enough when…” (comment, sheet, Slack) |

### Discovery

| # | Check |
|---|--------|
| D1 | Research question in one sentence |
| D2 | Done criterion (“enough when…”) |
| D3 | Where to start lineage (OpenMetadata / dbt / metabase / code path) |
| D4 | Scope boundaries (which `*_state` / features / products) |

### A/B

| # | Check |
|---|--------|
| AB1 | Experiment / flag / variant names |
| AB2 | Metric(s) and grain |
| AB3 | Exposure / assignment source |
| AB4 | Window and guardrails |

### DataOps

| # | Check |
|---|--------|
| O1 | Scope of change (dashboard / collection / all / chart list) |
| O2 | Tooling/stack named (metabase API, script location, language) |
| O3 | Safety path (copy-first, dry-run, rollback) |
| O4 | Acceptance test (compare old vs new query results) |
| O5 | Pilot target for first run |

### Docs

| # | Check |
|---|--------|
| C1 | Source artifact (Figma / Confluence / ticket links) |
| C2 | Deliverable location (Confluence page, repo path, analytics-context, …) |
| C3 | Audience and format (event map table, diagram, both) |
| C4 | Relationship to existing docs (replace / extend / new) |

### Report

| # | Check |
|---|--------|
| R1 | Audience and occasion |
| R2 | Artifact type and location (slides, doc) |
| R3 | Source charts/numbers listed or already agreed |
| R4 | Sign-off owner |

### Goal

| # | Check |
|---|--------|
| G1 | Outcome in one sentence |
| G2 | Child tickets exist, or explicit “wrapper only — split next” |

---

## Cross-repo hints

When gate mentions models/contracts/catalog:

| Need | Look in |
|------|---------|
| ClickHouse gold/silver SQL | `ch_dbt` |
| DWS/Postgres marts | `dbt-smarthome` |
| Ad-hoc SQL / EDA | `tasks` (`hospa_*`) |

Do not edit sibling repos while scoring or executing — append OUTBOX in `tasks` when a lasting fix belongs elsewhere.
