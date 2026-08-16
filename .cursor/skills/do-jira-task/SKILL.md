---
name: do-jira-task
description: >-
  Execute a HOSPA Jira ticket only after a fail-closed context-gate re-score.
  Use when the user says "сделай эту Jira задачу", "do HOSPA-…", "/do-jira-task",
  or asks to implement a sprint ticket without inventing missing business/data context.
disable-model-invocation: true
---

# Do Jira Task

Run a ticket end-to-end **only with enough context**. Prefer bouncing to
`/triage-analytics` over guessing event maps, metrics, sources, or DoD.

The fill loop (context gate + grill) lives in triage. This skill **re-scores** the same
[context gate](../../../docs/agents/context-gate.md) and refuses to Execute on a fail.

Inspiration: this workspace’s cross-repo map (`CONTEXT.md`, `.cursor/WORKSPACE.md`, OUTBOX.md).

## When invoked

User names a key (`HOSPA-1399`) or points at the open ticket. If ambiguous, ask which key — do not pick one.

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
2. **Local folder** — `hospa_<n>/` if present (SQL, notes, prior PLAN).
3. **Repo context** — this repo’s `CONTEXT.md`, `OUTBOX.md`.
4. **Workspace** — `.cursor/WORKSPACE.md` for sibling paths (`dbt-smarthome`, `ch_dbt`, `tasks`).
5. **Light scan** — only what the ticket already points to (Metabase URL → eye MCP; table name → OM/CH/DWS). Do not deep-explore the whole warehouse “just in case”.

Output a short **Known facts** bullet list (cited: Jira field / comment / file / URL).

## Phase 2 — Context gate (re-score)

Read [context-gate.md](../../../docs/agents/context-gate.md). Score **pass / thin / blocked**.

- Any **BLOCKER** → gate fails. Go to Bounce. **Do not Execute.** Do not open a discovery grill.
- **thin** → Plan with explicit gaps; Execute only steps that do not depend on gaps, and only after user OK. If the gaps are requester-owned, Bounce those instead of planning around them.
- **pass** → Plan, then wait for confirmation before Execute.

Anti-patterns (always fail or refuse that step):

- Inventing event names, funnel steps, or metric grains
- Assuming a gold/table name without finding it in dbt/mdm/Metabase
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

1. What should triage or the gate have caught earlier?
2. Propose 1–3 concrete edits to this skill, [context-gate.md](../../../docs/agents/context-gate.md), or [task-quality.md](task-quality.md).
3. Apply skill edits only if the user asks; otherwise leave proposals in the reply (and optionally under `hospa_<n>/RETRO.md`).

## Culture loop

Ticket quality compounds: gaps found at triage (or on an execute bounce) become checklist items in [task-quality.md](task-quality.md). Prefer fixing the ticket + PLAN over papering over ambiguity in code.
