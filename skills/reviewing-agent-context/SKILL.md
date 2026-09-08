---
name: reviewing-agent-context
description: Audits a repository's agent context — instruction files, rules, skills, docs, MCP tools, generated artifacts — and reports what to keep, merge, move, or delete. Runs the context-engineering operating model over the repo, then scores every finding against Anthropic's skill-authoring rubric. Use when asked to audit or review agent context, when CLAUDE.md / AGENTS.md / .cursor/rules or a skills library has grown unmanaged, when agents repeatedly re-discover the same facts or ignore documented conventions, or when output quality degrades across a whole repo rather than one session.
---

# Reviewing Agent Context

## What this is

A wrapper. It contributes no context theory of its own. It composes two existing sources:

| Source | Role | Where |
|---|---|---|
| `context-engineering` skill | The operating model — context hierarchy, packing strategies, MCP access, anti-patterns | addyosmani/agent-skills, under skills/context-engineering/ |
| Anthropic skill-authoring best practices | The acceptance criteria every finding is scored against | [references/rubric.md](references/rubric.md) |

If a finding is not traceable to one of those two, it does not belong in the report.

## Requires from the consuming repo

Outside dependencies, declared here rather than linked (ADR-0004).

- **`context-engineering` skill** — the operating model half of the audit. Expected
  wherever skills install in the consuming repo; Step 1's
  `--locate-context-engineering` call finds it. Absent: note "context-engineering
  skill not installed — rubric-only audit" in the report header and run the
  deterministic and rubric halves without it. Do not reconstruct the operating model
  from memory.

`references/rubric.md` and `references/report-template.md` ship inside this skill, so
they are not consuming-repo dependencies.

## Workflow

Copy this checklist and check items off as you go:

```
Context Audit Progress:
- [ ] Step 1: Load the two sources
- [ ] Step 2: Run the validator (deterministic pass)
- [ ] Step 3: Build inventory + load map from validator output
- [ ] Step 4: Judgment pass (duplication, gaps, staleness, hotspots)
- [ ] Step 5: Apply the relocation ladder
- [ ] Step 6: Write the report
- [ ] Step 7: Build the before/after eval suite
```

### Step 1 — Load the two sources

Locate the context-engineering skill and read it in full:

```bash
python3 scripts/audit_context.py --locate-context-engineering
```

If it is not installed, say so in the report's header and continue; the rubric half of the
audit still stands. Do not reconstruct its content from memory — the operating model must
come from the file.

Then read [references/rubric.md](references/rubric.md).

### Step 2 — Run the validator

```bash
python3 scripts/audit_context.py <repo-root>          # markdown report
python3 scripts/audit_context.py <repo-root> --json    # machine-readable
```

Execute it; do not read it. It produces the deterministic half of the audit: per-file token cost, load-tier
classification, always-on budget, rubric violations, broken and over-deep links, path
claims that do not resolve, and near-duplicate passages. Everything it emits is a fact.
Do not restate its findings as your own judgment, and do not re-derive by hand what it
already measured.

**Scope.** By default every file under `<repo-root>` is audited. Pass `--scope canonical`
to restrict findings to `skills/` and `.claude/skills/` when the repo keeps
deliberately-unfinished work elsewhere (this Library's `.cursor/` sandbox) that would
otherwise bury real findings; the report then opens with a **Scope** section naming each
excluded directory and its skipped-file count, so "checked and clean" stays distinct from
"never looked at". Don't pass it in a repo where `.cursor/skills/` is a live agent folder
rather than a sandbox.

### Step 3 — Inventory and load map

Take both directly from validator output. Correct the load tier only where you have
evidence the heuristic is wrong (for example, a rules file whose glob never matches a
real path). State every correction and its evidence.

### Step 4 — Judgment pass

The validator flags candidates; you decide. For each candidate, name the specific
anti-pattern from the context-engineering skill or the specific rubric line it violates.
Sections 3–6 of [references/report-template.md](references/report-template.md) say what
evidence each finding class requires.

For "missing context agents repeatedly re-discover", evidence means observed repetition —
transcripts, repeated user corrections, or the same question answered twice in git
history. Absent that evidence, label the item speculative or drop it.

### Step 5 — Apply the relocation ladder

Every keep-worthy piece of context gets exactly one destination on the ladder:

`root instruction → scoped rule → skill → reference → tool query → CI check`

The placement rules, and what disqualifies a rung, are in
[references/report-template.md](references/report-template.md).

### Step 6 — Write the report

Follow [references/report-template.md](references/report-template.md). All eight sections,
in order. Anything you could not verify goes under Unverified, not into the findings.

### Step 7 — Build the eval suite

The audit is a hypothesis until it is measured. Build the before/after suite described in
section 8 of the template: at least three cases that fail (or waste context) on the current
structure and pass on the proposed one, with the baseline recorded before any change lands.

## Verification

The audit is complete when:

- [ ] Every finding cites a rubric line or a named context-engineering anti-pattern
- [ ] Every recommendation names a source path, a destination rung, and a reason
- [ ] The always-on token budget is stated as a before/after number
- [ ] At least three eval cases exist, with baselines recorded before any change
- [ ] `python3 scripts/audit_context.py <repo-root>` exits 0, or every remaining error is listed as accepted with a reason
- [ ] `python3 scripts/test_audit_context.py` passes, if the validator was changed during the audit

## Red flags

- A finding whose only support is "this seems verbose" — measure it or drop it
- Recommending a new instruction file; the ladder moves context down, not up
- Reporting duplication between a skill and its own reference file (that is progressive disclosure working)
- Proposing a rewrite of content the audit never showed an agent reading
- Skipping step 7 because the improvements look obvious
