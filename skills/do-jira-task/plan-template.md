# PLAN.md template

Copy into `hospa_<n>/PLAN.md` (or `sheye_<n>/PLAN.md`). Fill from Ingest + gate; leave Execution outline steps `blocked-by:…` until ready.

```markdown
# HOSPA-<n> — <summary>

- **Jira:** https://tasks.sberdevices.ru/browse/HOSPA-<n>
- **Sprint:** <name or n/a>
- **Components:** <BI | ETL | …>
- **Status (Jira):** …
- **Gate:** pass | thin | blocked
- **PLAN updated:** YYYY-MM-DD

## Goal

<one paragraph>

## Non-goals

- …

## Known facts

- … (source: Jira description | comment | file | URL)

## Context map

| Kind | Ref | Notes |
|------|-----|-------|
| Metabase | | |
| Warehouse / dbt | | |
| mdm | | |
| analytics-context | | |
| Local folder | hospa_<n>/ | |
| People | | |

## Gate checklist

<!-- paste relevant rows from docs/agents/context-gate.md with ok/missing/n/a -->

| Check | Result | Note |
|-------|--------|------|
| U1 Goal | | |
| U3 DoD | | |
| … | | |

## Gaps

- BLOCKER: …
- …

## Proposed next questions

1. …
2. …

## Proposed Jira description edits

<!-- draft only; apply after user OK -->

## Execution outline

| # | Step | status |
|---|------|--------|
| 1 | … | ready \| blocked-by:… |

## Retro notes

<!-- filled at session end -->
```
