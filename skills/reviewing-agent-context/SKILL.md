---
name: reviewing-agent-context
description: Audits a repository's agent context — instruction files, rules, skills, docs, MCP tools, generated artifacts — and reports what to keep, merge, move, or delete. Runs the context-engineering operating model over the repo, then scores every finding against Anthropic's skill-authoring rubric. Use when asked to audit or review agent context, when CLAUDE.md / AGENTS.md / .cursor/rules or a skills library has grown unmanaged, when agents repeatedly re-discover the same facts or ignore documented conventions, when output quality degrades across a whole repo rather than one session, or when a skill's `evals/cases.json` needs writing or running — it also executes those cases and reports a verdict per case.
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

- **A model command on `PATH`** — only for the eval runner's opt-in `--with-model` half
  (default `claude -p`; override with `--model-cmd`). Absent: the runner exits 2 naming
  the missing command. The deterministic half needs no model and still runs.
- **Sibling skills named as `owner` in a cases file** — expected under the consuming
  repo's `skills/`, `.claude/skills/` or `.cursor/skills/`. Absent: the runner fails
  that negative case and names the owner it could not find; it does not skip it.

`references/rubric.md` and `references/report-template.md` ship inside this skill, so
they are not consuming-repo dependencies.

## Scope: audits and runs

This skill audits agent context, and it also **runs** skills' evaluations. Both halves
read one schema, in `scripts/cases_schema.py`: the validator's R7.1 check demands a
cases file of that shape, and the runner executes it. The audit workflow below is the
main path; go to [Running a skill's evals](#running-a-skills-evals) when the task is to
execute or write a cases file.

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
- [ ] `python3 scripts/test_audit_context.py` and `python3 scripts/test_run_skill_evals.py` pass, if the validator, the schema, or the runner was changed during the audit

## Running a skill's evals

A skill's evaluations live in `evals/cases.json` inside the skill's own directory. The
shape — a `trigger` object with `positive` and `negative` cases, and an `evals` array of
execution cases — is documented at the top of `scripts/cases_schema.py`; read that
docstring before writing a cases file, and copy this skill's own `evals/cases.json` as a
worked example.

Execute the runner; do not read it:

```bash
python3 scripts/run_skill_evals.py <repo-root>                  # every skill with a cases file
python3 scripts/run_skill_evals.py <repo-root> --skill <name>   # one skill
python3 scripts/run_skill_evals.py <repo-root> --with-model     # opt-in, costs money
```

It prints one verdict row per case — `pass`, `fail`, or `skip` — and exits 1 if any case
failed. When a skill is installed under two roots, `--skill` runs the copies that carry a
cases file, and fails only when none does.

**The default run is deterministic and free.** It fails a cases file that does not parse
against the schema, trigger cases on a skill with `disable-model-invocation: true`, and
a negative case whose `owner` is not another auto-triggerable skill in the repo. Every
case only a model can decide — including a negative case whose owner resolves — is
reported as `skip`. A skip is not a pass: never report a skill's evals as passing on
a deterministic run alone — say which cases were skipped.

**`--with-model` is opt-in.** Each trigger case costs one model call and each execution
case two, so ask before running it. Positive trigger cases pass when the skill ranks
within `top_k`, negative ones when the owner outranks it, execution cases when a judge
finds every expectation met.

Fix a failing cases file, re-run, and only proceed when no row says `fail`.

### What R7.1 demands

- Every skill: an `evals/cases.json` that parses, with at least one execution case. That is
  the enforced floor; the rubric's "at least three evaluations" stays a judgment call.
- Auto-triggerable skills: at least one positive and one negative trigger case as well.
- Skills with `disable-model-invocation: true`: no trigger cases — they never compete
  for a prompt, so ownership cases would test nothing.

### Rule change for repos that already copied this skill

R7.1 used to pass on the mere existence of `evals/`, `evals.json`, a `scenarios` directory, or a
repo-level `evals/cases/<skill>.json`, so an empty directory satisfied it. It now
requires `evals/cases.json` in the skill's directory, parsing against the schema. After
updating a copy, expect R7.1 to fire for skills it previously passed: a missing cases
file is a warning, a present-but-malformed one is an error. Those findings are skills
that were never evaluated, not regressions.

## Red flags

- A finding whose only support is "this seems verbose" — measure it or drop it
- Recommending a new instruction file; the ladder moves context down, not up
- Reporting duplication between a skill and its own reference file (that is progressive disclosure working)
- Proposing a rewrite of content the audit never showed an agent reading
- Skipping step 7 because the improvements look obvious
