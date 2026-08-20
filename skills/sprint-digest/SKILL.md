---
name: sprint-digest
description: >-
  Turn a Jira sprint into a narrative digest of evidence-backed, story-worthy
  increments (HTML briefing + short chat summary). Use when the user asks for a
  sprint digest, sprint story, meaningful increments, or stakeholder briefing —
  not a status dump, WIP dashboard, or sprint plan.
disable-model-invocation: true
---

# Sprint Digest

Narrative briefing of **meaningful increments** from a Jira sprint — not counts,
not a WIP board, not a packing plan.

| Sibling skill | Use that instead when… |
| --- | --- |
| `generate-status-report` | Prose standup / blockers / weekly status |
| `jira-sprint-dashboard` | Visual WIP snapshot (Canvas / fixed dashboard model) |
| `plan-analytics-sprint` | Packing already-triaged tickets into a sprint |
| `triage-analytics` | Filling a weak ticket until context-gate pass |
| `dataviz` | Everyday product-analytics exploration / insight cards |

**Story-worthiness ≠ context gate.** Implementation readiness
([context-gate.md](../../../docs/agents/context-gate.md)) is orthogonal. A Done
ticket with no audience consequence is omit; a thin ticket that unlocked a
stakeholder decision can be a headline.

In consuming Jira repos (e.g. `tasks`), read
`docs/agents/atlassian-skills.md` before querying. Default project **HOSPA**.
Browse links: `https://tasks.sberdevices.ru/browse/{KEY}`.

Jira is **read-only** unless the user separately confirms a write.

## Workflow

Copy this checklist and track progress:

```
Sprint digest:
- [ ] 1. Scope
- [ ] 2. Gather evidence
- [ ] 3. Cluster → candidates (Pass 1)
- [ ] 4. Shortlist grill (Pass 2)
- [ ] 5. Compose digest
- [ ] 6. Publish HTML + chat summary
- [ ] 7. Visual pass (impeccable, if HTML in tasks)
```

### 1. Scope

Clarify before querying:

- Project / board / sprint (do not guess; ask if ambiguous)
- Audience (stakeholder briefing vs team retro)
- Language (default Russian for stakeholder HTML in HOSPA)
- Window (sprint dates, or named sprint)

### 2. Gather evidence

Prefer: `jira_get_agile_boards` → `jira_get_sprints_from_board` →
`jira_get_sprint_issues` (paginate `limit` ≤ 50).

For every **candidate** (not every ticket on first pass):

1. `jira_get_issue` with comments (`comment_limit` high enough) and changelog if useful.
2. Read description, components, links, related keys.
3. Consult local domain: `CONTEXT.md`, ticket folders (`hospa_*`), sibling OUTBOX,
   OpenMetadata / Metabase / warehouse only when the claim needs verification.
4. Do **not** invent metrics, story points, burndown, or impact numbers.

Fields baseline: `summary,status,priority,assignee,updated,created,issuetype,components,description,comment,issuelinks,resolutiondate`.

### 3. Cluster → candidates (Pass 1)

Cluster related tickets into **increments** (one outcome / capability / learning),
not one row per Jira key. Score each candidate with
[increment-rubric.md](references/increment-rubric.md).

Rank into exactly one bucket:

| Bucket | Role in digest |
| --- | --- |
| **headline** | Lead story (usually 1; rarely 2) |
| **supporting** | Enables or deepens the headline |
| **watch** | Decision / risk / blocked value |
| **omit** | Routine delivery; appendix only |

Keep routine delivery stats (counts by status/owner) out of the lead — they belong
in the source appendix.

Present Pass 1 shortlist to the user as a compact table before writing HTML:

| Increment | Bucket | Keys | Evidence strength | Ambiguous? |

### 4. Shortlist grill (Pass 2)

Only grill **ambiguous high-value** candidates (headline or supporting with weak
consequence/audience). Do **not** run full `/triage-analytics` or context-gate
pass on every ticket.

Questioning discipline (from triage / grilling):

- One frontier round at a time; prefer recommended answers the user can accept.
- Agent looks up facts; user decides impact, audience, and “so what”.
- After answers, re-score the rubric; update the increment draft.
- Draft only. No Jira description/comment writes from this skill.

If the user declines grilling, publish with explicit **unresolved** labels on those
claims (see digest contract).

### 5. Compose digest

Follow [digest-contract.md](references/digest-contract.md).

Story structure (adapted from data-storytelling; fail closed on invention):

1. **Headline** — conclusion-first: what became true this sprint.
2. **Context** — baseline the reader needs (one short block).
3. **Increments** — what changed → evidence → why it matters / next decision.
4. **Watch** — decisions and risks that need a human.
5. **Appendix** — methodology, coverage, omissions, Jira links, counts.

Label every non-trivial claim as **observed** | **synthesis** | **unresolved**.

Prohibit:

- Invented causality (“X caused Y”) without evidence
- Quantified impact without a fetched number
- Forced “conflict” when the evidence only supports a capability or learning
- Dressing status dumps as narrative

### 6. Publish

**Default:**

1. Single-file HTML at `analyses/YYYY-MM-DD_<sprint-slug>-digest.html` in the
   consuming repo (create `analyses/` if needed).
2. Chat: 3–5 bullets — headline + top increments + one ask if any.

**HTML rules (consuming repos with PRODUCT/DESIGN):**

- Single self-contained file; inline CSS/JS; data as JSON if charts used.
- Follow root `DESIGN.md` / `PRODUCT.md` (Plasma-adapted editorial report surface).
- Charts optional and subordinate; if present, one claim per visual + table of the
  same numbers (`dataviz` Section A).
- Keep Jira keys and status names verbatim; body language per PRODUCT.md.

**Optional:** also write `sprint_<id>/DIGEST.md` if the user asks for markdown.

### 7. Visual pass

In `tasks` (or any repo with impeccable): after HTML exists,

```bash
node .cursor/skills/impeccable/scripts/context.mjs --target analyses/<file>.html
```

Then `/impeccable audit` → `distill` / `typeset` / `layout` / `polish`.  
Do **not** run `bolder` / `delight` / `overdrive` / `colorize`.  
Impeccable must not change facts, encodings, or editorial claims.

## Boundaries

- Do not merge this skill into `generate-status-report` or `jira-sprint-dashboard`.
- Do not treat context-gate pass/fail as story-worthiness.
- Do not write to Jira, Confluence, or sibling repos from this skill.
- Cross-repo gaps → propose OUTBOX entries; do not edit siblings silently.
