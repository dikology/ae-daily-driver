---
name: do-jira-task
description: >-
  Execute an issue-tracker (Jira) ticket only after a fail-closed context-gate re-score.
  Use when the user says "do this Jira ticket", "do {ISSUE-KEY}", "/do-jira-task",
  or asks to implement a sprint ticket without inventing missing business/data context.
disable-model-invocation: true
---

# Do Jira Task

Run a ticket end-to-end **only with enough context**. Prefer bouncing to
`/triage-analytics` over guessing event maps, metrics, sources, or DoD.

The fill loop (context gate + grill) lives in triage. This skill **re-scores** the same
context gate (declared under *Requires from the consuming repo*) and refuses to Execute
on a fail.

Inspiration: this workspace's cross-repo map — a repo `CONTEXT.md`, a workspace map
(`WORKSPACE.md`, kept under `.cursor/` here), and an `OUTBOX.md`.

## Requires from the consuming repo

Outside dependencies, declared here rather than linked (ADR-0004).

- **Context gate** — the shared checklist re-scored before Execute, stored at
  `docs/agents/context-gate.md` in repos that carry it. Absent: emit `context-gate
  re-score skipped: no context-gate.md at the repo root`, then bounce to
  `/triage-analytics` instead of Executing an unscored ticket.
- **`triage-analytics` skill** — the fill-and-grill loop this skill bounces to. Expected
  installed alongside this skill. Absent: say so, Plan only from Known facts, and stop
  at any BLOCKER instead of bouncing.
- **Workspace map** — a `WORKSPACE.md` (or equivalent) at the workspace root naming
  sibling-home paths (dbt projects, catalog, scratch); this repo keeps it under
  `.cursor/`. Absent: ask the user for sibling-home locations; do not guess them.
- **Repo `CONTEXT.md` and `OUTBOX.md`** at the consuming repo root. Absent: proceed
  without the cross-repo map and flag lasting cross-repo work in chat instead of an
  OUTBOX entry.
- **Ticket working directory** — a `{issue-key}/` folder for scratch, SQL, `PLAN.md`,
  `RETRO.md`. Created in the consuming repo if absent.

## When invoked

User names a key (`PROJ-123`) or points at the open ticket. If ambiguous, ask which key — do not pick one.

Copy this checklist and keep it updated in the reply:

```
do-jira-task:
- [ ] Ingest
- [ ] Context gate (re-score)
- [ ] Bounce to triage (if blocked) / Plan (if passed or thin)
- [ ] User confirmed plan
- [ ] Execute
- [ ] Retro
```

## Phase 1 — Ingest

Gather facts. Do not invent.

1. **Jira** — `jira_get_issue` (summary, description, status, components, links, attachments). Read comments. Note stakeholders and open questions.
2. **Local folder** — ticket working dir if present (`{issue-key}/` or similar: SQL, notes, prior PLAN).
3. **Repo context** — this repo’s `CONTEXT.md`, `OUTBOX.md`.
4. **Workspace** — the workspace map (see *Requires from the consuming repo*) for sibling-home paths (dbt projects, catalog, ad-hoc scratch).
5. **Light scan** — only what the ticket already points to (Metabase URL → Metabase MCP; table name → catalog / warehouse). Do not deep-explore the whole warehouse “just in case”.

Output a short **Known facts** bullet list (cited: Jira field / comment / file / URL).

## Phase 2 — Context gate (re-score)

Read the context gate (`docs/agents/context-gate.md` — see *Requires from the consuming repo*). Score **pass / thin / blocked**.

- Any **BLOCKER** → gate fails. Go to Bounce. **Do not Execute.** Do not open a discovery grill.
- **thin** → Plan with explicit gaps; Execute only steps that do not depend on gaps, and only after user OK. If the gaps are requester-owned, Bounce those instead of planning around them.
- **pass** → Plan, then wait for confirmation before Execute.

Anti-patterns (always fail or refuse that step):

- Inventing event names, funnel steps, or metric grains
- Assuming a gold/table name without finding it in dbt / semantic layer / Metabase
- Editing sibling repos directly (use OUTBOX)
- Updating Jira without explicit user confirmation
- Writing SQL/charts “to see what happens” when the question is undefined

## Phase 3 — Bounce (gate failed)

Default: send the ticket back to `/triage-analytics`. Show the failed gate rows, draft
needs-info / description edits (do not apply until confirmed), and stop.

Do not run a clarify/grill session here. Environment facts you can look up (renamed
table, dead Metabase URL, comment vs dbt) belong in Known facts and the bounce notes —
finding facts is still this skill's job; deciding grain, DoD, or event maps is triage's.

If the user is present and answers in this session, treat the answers as triage: capture
them into proposed description edits, re-score the gate, then Plan only after **pass**
(or thin with named non-blocking gaps). Remaining BLOCKERs still mean Bounce, not Execute.

## Phase 4 — Plan

Create or update `{issue-key}/PLAN.md` using [plan-template.md](plan-template.md).

- Execution outline steps must be concrete and tied to Known facts.
- Mark each step `ready` | `blocked-by:<gap>`.
- Do not expand into implementation files yet.

Show the plan summary and **wait for user confirmation**.

## Phase 5 — Execute

Only after explicit OK.

1. Run only `ready` steps from PLAN.md.
2. Prefer working in `{issue-key}/` for ad-hoc; lasting models/contracts → flag OUTBOX toward the owning repo (see cross-repo-flag rule). Ask before any Jira comment/transition.
3. After material progress, update PLAN.md checkboxes / status.

## Phase 6 — Retro

Before ending the session (even if blocked):

1. What should triage or the gate have caught earlier?
2. Propose 1–3 concrete edits to this skill, the context gate (`docs/agents/context-gate.md`), or [task-quality.md](task-quality.md).
3. Apply skill edits only if the user asks; otherwise leave proposals in the reply (and optionally under `{issue-key}/RETRO.md`).

## Culture loop

Ticket quality compounds: gaps found at triage (or on an execute bounce) become checklist items in [task-quality.md](task-quality.md). Prefer fixing the ticket + PLAN over papering over ambiguity in code.
