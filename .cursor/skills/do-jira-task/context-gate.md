# Context gate

Fail-closed checklist. Score each item: `ok` | `missing` | `n/a`.

**Gate result**

- **pass** — no `missing` on required items for this component type
- **thin** — goal/DoD mostly clear, but 1–2 non-blocking gaps; Execute only independent steps
- **blocked** — any required item is `missing`, or status is Need Info without a written resolution path

Mark blockers with `BLOCKER:` in PLAN.md Gaps.

---

## Universal (every ticket)

| # | Check | Required |
|---|--------|----------|
| U1 | Goal clear from description + comments (not summary alone) | yes |
| U2 | Non-goals or out-of-scope stated, or explicitly “none” | prefer |
| U3 | Definition of Done is verifiable (artifact + acceptance) | yes |
| U4 | Stakeholder / requester known if clarification needed | prefer; **yes** if Need Info |
| U5 | Links present or marked n/a: Metabase / Confluence / Figma / sibling path / mdm contract | yes (each must be link or n/a) |

---

## By component

Use Jira Components (BI, ETL, Discovery, DataOps, Docs). If multiple, apply **all** matching sections.

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

### Discovery

| # | Check |
|---|--------|
| D1 | Research question in one sentence |
| D2 | Done criterion (“enough when…”) |
| D3 | Where to start lineage (OpenMetadata / dbt / eye / code path) |
| D4 | Scope boundaries (which `*_state` / features / products) |

### DataOps

| # | Check |
|---|--------|
| O1 | Scope of change (dashboard / collection / all / chart list) |
| O2 | Tooling/stack named (eye API, script location, language) |
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

---

## Cross-repo hints

When gate mentions models/contracts/catalog:

| Need | Look in |
|------|---------|
| Metric / dataset contract | `mdm` |
| ClickHouse gold/silver SQL | `ch_dbt` |
| DWS/Postgres marts | `dbt-smarthome` |
| Metabase asset docs | `analytics-context` |
| Ad-hoc SQL / EDA | `tasks` (`hospa_*`) |
| Agent sync mapping | `fenxi` (do not invent; OUTBOX if drift) |

Do not edit siblings from this skill — append OUTBOX in `tasks` when a lasting fix belongs elsewhere.
