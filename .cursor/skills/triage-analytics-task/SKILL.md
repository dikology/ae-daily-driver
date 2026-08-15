---
name: triage-analytics-task
description: Classify and normalize an incoming analytics engineering request into a task type (bi, etl, adhoc, infra, data-quality), resolve the owning repo, and draft a ticket ready for the tracker. Use when a new request, Slack message, or ad hoc ask needs to become a properly scoped ticket before it enters sprint planning.
---

# Triage Analytics Task

This skill turns a loose request ("can we get a dashboard for X", "the events pipeline is
lagging", "someone asked for a one-off number") into a normalized, tracker-ready ticket.
It exists because your sprints pull tasks from many repos and domains rather than one
project — every ticket needs the same shape before `/plan-analytics-sprint` can use it.

## When to use

- A new request lands (Slack, email, verbal ask, or your own idea) and needs to become
  a ticket.
- An existing ticket is missing a type label, owning repo, or acceptance criteria.
- Before running `/plan-analytics-sprint`, to make sure every candidate ticket is
  normalized.

## Step 1 — Classify the type

Ask yourself (or the user, if ambiguous) which bucket this falls into. Do not guess if
more than one fits equally well — ask.

- **bi** — dashboard, report, metric definition, semantic layer change (Cube/Lightdash),
  visualization request. Output is consumed directly by a stakeholder.
- **etl** — pipeline, ingestion, transformation (dbt model, ClickHouse table/materialized
  view), scheduling, data contract change. Output is a data asset other work depends on.
- **adhoc** — one-off question, number pull, investigation with no lasting artifact beyond
  an answer.
- **data-quality** — bug in existing data, discrepancy, broken test/contract, backfill.
- **infra** — tooling, CI/CD, warehouse cost/perf, access, repo scaffolding.

If the request is genuinely a research question rather than an execution task (e.g.
"can we even do X"), route it to `/research` instead of turning it into an implementation
ticket.

## Step 2 — Resolve the owning repo

State explicitly which repo/codebase this belongs to. If it touches more than one repo,
say so and note the ticket will need `/to-tickets` to split it into per-repo units with
blocking edges — do not silently pick one repo.

If you don't know the repo mapping, ask once and remember the answer in this repo's
`CONTEXT.md` (or ADR) so future triage doesn't re-ask.

## Step 3 — Draft the ticket

Produce this exact shape, ready to paste into the tracker configured by
`/setup-matt-pocock-skills`:

```
Title: <verb-first, specific — "Add churn cohort to Cube semantic layer", not "Churn dashboard">
Type: bi | etl | adhoc | data-quality | infra
Repo: <repo name>
Cross-repo: yes/no — if yes, list the other repos involved
Acceptance criteria:
- <concrete, testable — a stakeholder or reviewer could verify each line>
Context / why now:
- <who asked, what decision or downstream work depends on it>
Estimate: S / M / L (rough — used for sprint packing, not a commitment)
```

## Step 4 — Apply labels and file

Use the labels configured in `/setup-matt-pocock-skills` (usually `type:<bucket>` plus
`repo:<name>`). File the ticket on the tracker directly if you have write access; otherwise
hand the drafted block back to the user to file.

## Boundaries

- This skill only classifies and drafts — it does not plan a sprint (`/plan-analytics-sprint`)
  or implement anything (`/implement`, `/research`).
- If the request is too vague to write concrete acceptance criteria, use `/grill-me` first,
  then come back to this skill.
