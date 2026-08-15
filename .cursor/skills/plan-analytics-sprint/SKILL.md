---
name: plan-analytics-sprint
description: Assemble a sprint plan from a pool of already-triaged analytics engineering tickets spanning multiple repos and task types (bi, etl, adhoc, infra, data-quality). Groups by repo/domain, flags cross-repo dependencies, sizes the sprint, and writes the plan to the Obsidian vault. Use at the start of a sprint, once candidate tickets exist.
---

# Plan Analytics Sprint

Unlike a single-repo feature (what `/wayfinder` is built for), an analytics engineering
sprint here is a bag of unrelated tickets across repos and domains. This skill's job is
packing and sequencing that bag — not decomposing any one ticket's implementation.

## Prerequisites

- Every candidate ticket has been through `/triage-analytics-task` (has type, repo,
  acceptance criteria, estimate). If any ticket is missing these, run that skill on it
  first — don't guess the fields yourself.

## Step 1 — Collect the candidate pool

Pull all triaged, unstarted tickets tagged for this sprint from the tracker(s) configured
in `/setup-matt-pocock-skills`. List them with: title, type, repo, estimate.

## Step 2 — Group and flag dependencies

- Group tickets by repo, then by type within repo.
- For any ticket marked cross-repo (or where you can see one ticket's output feeds
  another, e.g. an etl ticket a bi ticket depends on), draw the dependency explicitly:
  `<ticket A> blocks <ticket B>`. Use `/to-tickets` on any ticket that is really several
  units of work hiding under one title.
- Flag same-repo collisions (two tickets touching the same dbt model / Cube view / table)
  so they can be sequenced instead of parallelized.

## Step 3 — Size and sequence

- Sum estimates per repo and overall against the sprint's capacity (ask the user for
  capacity if not stated — don't assume).
- Order tickets so blocking etl/infra work lands before the bi/adhoc work that depends
  on it.
- If the pool exceeds capacity, propose what to cut or defer — present the tradeoff,
  don't decide unilaterally.

## Step 4 — Write the sprint plan to Obsidian

Use the `obsidian-vault` skill's conventions for location/frontmatter. Create a note
shaped like:

```markdown
# Sprint <name/dates>

## Capacity
<team/person>: <capacity> — planned: <sum of estimates>

## By repo

### <repo A>
- [ ] [etl] <ticket title> — <estimate> — blocks: <ticket in repo B>
- [ ] [bi]  <ticket title> — <estimate> — blocked by: <ticket above>

### <repo B>
- [ ] [adhoc] <ticket title> — <estimate>

## Cross-repo dependencies
- <ticket A> → <ticket B>: <why>

## Deferred / cut
- <ticket> — <reason>
```

Link each ticket title to its tracker URL.

## Step 5 — Hand off to execution

For each ticket, execution is: `/implement` for bi/etl/infra/data-quality tickets,
`/research` for adhoc questions with no lasting code artifact. When a ticket closes,
use `/close-analytics-task` to write the closing comment and update this same Obsidian
note (check the box, add a one-line outcome).

## Boundaries

- Does not write code or specs for individual tickets — that's `/to-spec` and `/implement`.
- Does not re-triage — if a ticket lacks type/repo/acceptance criteria, send it back to
  `/triage-analytics-task` rather than inventing the missing fields here.
