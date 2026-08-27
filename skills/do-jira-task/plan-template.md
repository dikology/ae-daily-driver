# PLAN.md template

Copy into the ticket working directory as `PLAN.md` (create `{issue-key}/` if the consuming repo uses per-ticket folders). Fill from Ingest + gate; leave Execution outline steps `blocked-by:…` until ready.

```markdown
# {ISSUE-KEY} — <summary>

- **Issue:** <issue-tracker browse URL>
- **Sprint:** <name or n/a>
- **Components:** <BI | ETL | …>
- **Status (tracker):** …
- **Gate:** pass | thin | blocked
- **PLAN updated:** YYYY-MM-DD

## Goal

<one paragraph>

## Non-goals

- …

## Known facts

- … (source: issue description | comment | file | URL)

## Context map

| Kind | Ref | Notes |
|------|-----|-------|
| Metabase | | |
| Warehouse / dbt | | |
| Semantic layer | | |
| Dashboard catalog | | |
| Local folder | {issue-key}/ | |
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

## Proposed issue description edits

<!-- draft only; apply after user OK -->

## Execution outline

| # | Step | status |
|---|------|--------|
| 1 | … | ready \| blocked-by:… |

## Retro notes

<!-- filled at session end -->
```
