---
name: do-jira-task
description: >-
  Execute a HOSPA Jira ticket only after a fail-closed context gate.
  Use when the user says "сделай эту Jira задачу", "do HOSPA-…", "/do-jira-task",
  or asks to implement a sprint ticket without inventing missing business/data context.
disable-model-invocation: true
---

# Do Jira Task

Run a ticket end-to-end **only with enough context**. Prefer stopping and repairing the ticket description over guessing event maps, metrics, sources, or DoD.

Inspiration: mattpocock grilling (align first) + this workspace’s cross-repo map (`CONTEXT.md`, `.cursor/WORKSPACE.md`, OUTBOX.md).

## When invoked

User names a key (`HOSPA-1399`) or points at the open ticket. If ambiguous, ask which key — do not pick one.

Copy this checklist and keep it updated in the reply:

```
do-jira-task:
- [ ] Ingest
- [ ] Context gate
- [ ] Clarify (if gate failed) / Plan (if passed)
- [ ] User confirmed plan
- [ ] Execute
- [ ] Retro
```

## Phase 1 — Ingest

Gather facts. Do not invent.

1. **Jira** — `jira_get_issue` (summary, description, status, components, links, attachments). Read comments. Note stakeholders and open questions.
2. **Local folder** — `hospa_<n>/` if present (SQL, notes, prior PLAN).
3. **Repo context** — this repo’s `CONTEXT.md`, `OUTBOX.md`.
4. **Workspace** — `.cursor/WORKSPACE.md` for sibling paths (`dbt-smarthome`, `ch_dbt`, `tasks`).
5. **Light scan** — only what the ticket already points to (Metabase URL → eye MCP; table name → OM/CH/DWS). Do not deep-explore the whole warehouse “just in case”.

Output a short **Known facts** bullet list (cited: Jira field / comment / file / URL).

## Phase 2 — Context gate

Read [context-gate.md](context-gate.md). Score **pass / thin / blocked**.

- Any **BLOCKER** → gate fails. Go to Clarify. **Do not Execute.**
- **thin** → Clarify or Plan with explicit gaps; Execute only steps that do not depend on gaps, and only after user OK.
- **pass** → Plan, then wait for confirmation before Execute.

Anti-patterns (always fail or refuse that step):

- Inventing event names, funnel steps, or metric grains
- Assuming a gold/table name without finding it in dbt/mdm/Metabase
- Editing sibling repos directly (use OUTBOX)
- Updating Jira without explicit user confirmation
- Writing SQL/charts “to see what happens” when the question is undefined

## Phase 3 — Clarify (gate failed or thin)

Work like a grilling frontier: ask only questions that are unblocked by known facts. Number them; recommend an answer when you have one.

Also draft (do not apply until confirmed):

- Proposed Jira description / DoD / links to add
- Which sibling repo should own a lasting artifact (mdm contract, dbt model, analytics-context doc)

Stop and wait. After answers, re-run the gate.

## Phase 4 — Plan

Create or update `hospa_<n>/PLAN.md` using [plan-template.md](plan-template.md).

- Execution outline steps must be concrete and tied to Known facts.
- Mark each step `ready` | `blocked-by:<gap>`.
- Do not expand into implementation files yet.

Show the plan summary and **wait for user confirmation**.

## Phase 5 — Execute

Only after explicit OK.

1. Run only `ready` steps from PLAN.md.
2. Prefer working in `hospa_<n>/` for ad-hoc; lasting models/contracts → flag OUTBOX toward the owning repo (see cross-repo-flag rule). Ask before any Jira comment/transition.
3. After material progress, update PLAN.md checkboxes / status.

## Phase 6 — Retro

Before ending the session (even if blocked):

1. What should the gate have caught earlier?
2. Propose 1–3 concrete edits to this skill, [context-gate.md](context-gate.md), or [task-quality.md](task-quality.md).
3. Apply skill edits only if the user asks; otherwise leave proposals in the reply (and optionally under `hospa_<n>/RETRO.md`).

## Culture loop

Ticket quality compounds: gaps found in Clarify become checklist items in [task-quality.md](task-quality.md). Prefer fixing the ticket + PLAN over papering over ambiguity in code.
