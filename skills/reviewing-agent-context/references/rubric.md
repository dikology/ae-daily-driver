# Acceptance rubric

The audit's scoring criteria, taken from Anthropic's [skill authoring best
practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).
This file restates the criteria as checks; the guide is the authority.

## Contents

- R1 — Token discipline
- R2 — Discovery descriptions
- R3 — Progressive disclosure
- R4 — One-level references
- R5 — Appropriately constrained workflows
- R6 — Executable validators and feedback loops
- R7 — Evaluation-driven iteration
- R8 — Content hygiene
- Scoring
- Auto vs. judgment

---

## R1 — Token discipline

- R1.1 SKILL.md body is under 500 lines.
- R1.2 The skill adds only context the model does not already have. Explanations of
  well-known formats, libraries, or concepts are cut.
- R1.3 Content that is always loaded (root instruction files, always-apply rules, every
  skill's frontmatter description) is justified by being needed on nearly every task.
- R1.4 Large reference material sits in files that are read on demand, not inlined.

Violation evidence: a measured line or token count, plus what the tokens buy.

## R2 — Discovery descriptions

- R2.1 `name` is at most 64 characters, lowercase letters/numbers/hyphens only, and does
  not contain the reserved words "anthropic" or "claude".
- R2.2 `name` is specific — not `helper`, `utils`, `tools`, `docs`, `data`.
- R2.3 `description` is non-empty and at most 1024 characters.
- R2.4 `description` is third person. No "I can…", no "You can use this to…".
- R2.5 `description` states both what the skill does **and** when to use it, using the
  vocabulary a user would actually type.
- R2.6 No two descriptions in the catalog collide such that the wrong one wins routing.

Violation evidence: the description text, plus a realistic user prompt that would route
wrong.

## R3 — Progressive disclosure

- R3.1 SKILL.md reads as an overview that points at detail, not as the detail itself.
- R3.2 Content is split by domain or by task branch, so an unrelated branch costs nothing.
- R3.3 Advanced or conditional material is behind a link, not inline.
- R3.4 Every bundled file is actually reachable from SKILL.md; unreferenced files are dead
  weight.

## R4 — One-level references

- R4.1 Every reference file links directly from SKILL.md.
- R4.2 No chain SKILL.md → a.md → b.md. A reference that needs another reference is a
  signal to link both from SKILL.md.
- R4.3 Every relative link resolves from the file that contains it, at the path the skill
  is actually installed to.
- R4.4 Reference files over 100 lines open with a table of contents.
- R4.5 All paths use forward slashes.

## R5 — Appropriately constrained workflows

Freedom must match the fragility of the task.

| Task shape | Correct form |
|---|---|
| Many valid approaches, context decides | Prose heuristics (high freedom) |
| A preferred pattern with acceptable variation | Parameterized template or pseudocode (medium) |
| Fragile, order-dependent, or destructive | An exact command to run, with "do not modify" (low) |

- R5.1 Fragile or destructive operations are pinned to exact commands, not described.
- R5.2 Open-ended judgment work is not over-scripted into false precision.
- R5.3 Multi-step work provides a checklist the agent can copy and track.
- R5.4 The skill offers one default path, with escape hatches — not a menu of options.

## R6 — Executable validators and feedback loops

- R6.1 Deterministic checks are scripts the agent runs, not instructions it follows.
- R6.2 The skill states plainly whether a script is to be **executed** or **read**.
- R6.3 Quality-critical output has a validate → fix → re-validate loop with an explicit
  "only proceed when it passes".
- R6.4 Scripts handle their own error conditions rather than deferring to the agent.
- R6.5 No unexplained constants; every threshold carries its reasoning.

## R7 — Evaluation-driven iteration

- R7.1 At least three evaluations exist for the skill.
- R7.2 Each evaluation states expected behaviors, not expected phrasings.
- R7.3 A baseline without the skill was recorded, so improvement is measurable.
- R7.4 Evaluations were written from observed failures, not imagined ones.

## R8 — Content hygiene

- R8.1 No time-sensitive statements ("as of…", "coming soon", a bare future date). Historic
  material goes in a collapsed "old patterns" section.
- R8.2 One term per concept throughout.
- R8.3 Examples are concrete, not abstract placeholders.
- R8.4 MCP tools are named fully qualified as `ServerName:tool_name`.
- R8.5 Dependencies are stated, not assumed present.
- R8.6 Claims about the repository's own layout resolve to paths that exist.

---

## Scoring

Score each rubric line per artifact:

| Score | Meaning |
|---|---|
| **pass** | Meets the criterion |
| **warn** | Meets it, but at a cost worth naming (e.g. 480-line SKILL.md) |
| **fail** | Violates it; the report must state the fix and the destination rung |
| **n/a** | Criterion does not apply (e.g. R6 for a markdown-only skill) |

A rubric line scored **fail** requires a concrete fix. "Consider revising" is not a fix.

## Auto vs. judgment

`scripts/audit_context.py` decides R1.1, R2.1, R2.3, R2.4, R3.4, R4.1–R4.5, R7.1, R8.1,
R8.6, and near-duplicate detection for R8.2. Do not re-check those by hand — read them off
the validator.

Everything else is judgment: R1.2–R1.4, R2.2, R2.5, R2.6, R3.1–R3.3, all of R5, R6.2–R6.5,
R7.2–R7.4, R8.3–R8.5. Each judgment finding needs evidence a reader can check.
