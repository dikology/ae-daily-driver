# Report template

Eight sections, in this order. Sections 1–2 come from the validator. Sections 3–6 are
judgment with required evidence. Section 7 is the decision. Section 8 is the proof.

## Contents

- Header
- 1 — Context inventory
- 2 — Load map
- 3 — Duplicate and conflicting guidance
- 4 — Missing context
- 5 — Stale material and unsupported claims
- 6 — Context-cost hotspots
- 7 — Recommended relocation (the ladder)
- 8 — Evaluation suite
- Unverified

---

## Header

State: repo audited, commit SHA, whether the `context-engineering` skill was available,
validator version/exit code, and the headline number — always-on token budget, before and
proposed.

## 1 — Context inventory

Every artifact an agent can see. One row each.

| Path | Kind | Lines | Est. tokens | Owner surface |
|---|---|---|---|---|

`Kind` ∈ instruction file · scoped rule · skill · reference · doc · tool/MCP config ·
generated artifact. `Owner surface` is which agent reads it (all, Claude Code, Cursor,
CI, humans only). Mark human-only files — they are not agent context and must not be
counted in the budget.

## 2 — Load map

| Tier | Trigger | Artifacts | Est. tokens |
|---|---|---|---|
| Always | Every request | | |
| Task | Skill invoked / description matched | | |
| Path | A matching file is touched | | |
| Query | Agent asks a tool | | |

Frontmatter descriptions are always-loaded even when the skill body is not — count them in
the Always tier. Call out any artifact in no tier: nothing loads it, so it is either dead
or mis-filed.

## 3 — Duplicate and conflicting guidance

| Topic | Locations | Type | Which wins today | Resolution |
|---|---|---|---|---|

`Type` ∈ verbatim duplicate · paraphrase · **conflict**. Conflicts rank first — two files
telling an agent different things is worse than either being verbose. A skill duplicating
its own reference file is not a finding.

## 4 — Missing context

Only what an agent has demonstrably re-discovered. Each row needs an observation.

| Fact re-discovered | Evidence | Cost per occurrence | Destination rung |
|---|---|---|---|

Evidence means a transcript, a repeated correction, or a repeated exploration in history.
Items without evidence go under Unverified.

## 5 — Stale material and unsupported claims

| Claim | Location | Reality | Action |
|---|---|---|---|

Three classes: paths and files referenced that do not exist (validator-detected);
statements about tooling or process that no longer hold; and time-sensitive text (R8.1).
Action is fix, delete, or move to an "old patterns" section.

## 6 — Context-cost hotspots

Rank by tokens × load frequency, not by size alone. A 4,000-token skill loaded on 5% of
tasks costs less than a 400-token always-on file.

| Artifact | Est. tokens | Load frequency | Weighted cost | What the tokens buy |
|---|---|---|---|---|

State how frequency was estimated. If it is a guess, say so.

## 7 — Recommended relocation

Every keep-worthy piece of context lands on exactly one rung. Move down the ladder
whenever the rung's test allows it.

| Rung | Holds | Test it must pass | Disqualifier |
|---|---|---|---|
| **Root instruction** (`CLAUDE.md`, `AGENTS.md`) | Facts needed on nearly every task: stack, commands, hard boundaries | "An agent that skips this gets a wrong answer on a typical task" | Applies to one file type, one workflow, or one skill |
| **Scoped rule** (`.cursor/rules/*.mdc`, path-globbed config) | Conventions tied to a file pattern | "A glob names exactly when this applies" | The trigger is a user intent, not a path |
| **Skill** (`SKILL.md`) | A procedure with steps and a completion condition | "A user could ask for this by name" | It is a fact, not a procedure |
| **Reference** (`references/*.md`) | Detail a skill needs sometimes | "Linked from exactly one SKILL.md, one level deep" | Two or more skills need it — hoist it and link from each, never chain |
| **Tool query** (MCP, CLI, API) | Facts that change without the repo changing | "The live source is authoritative and reachable" | The tool is not wired up in the consuming environment |
| **CI check** (script, hook, lint) | Rules an agent can violate silently | "A script can decide pass/fail" | Enforcement needs human judgment |

Then the moves:

| # | Content | From | To (rung + path) | Why | Token delta |
|---|---|---|---|---|---|

Rank by token delta on the Always tier first, then by conflicts resolved. A move that adds
a root instruction file needs an explicit justification — the ladder's default direction is
down.

## 8 — Evaluation suite

At least three cases. Each targets a specific finding from sections 3–6 and must fail, or
waste measurable context, on the current structure.

Use this shape (Anthropic's evaluation structure; `expectations` are behaviors, not
phrasings):

```json
{
  "id": 1,
  "targets": "Section 3, row 2 — conflicting triage vocabulary",
  "skills": ["<skill under test>"],
  "prompt": "<a realistic user ask>",
  "expected_behavior": [
    "<observable behavior the current structure fails to produce>"
  ],
  "baseline": "<what actually happened before the change, recorded on the pre-change tree>",
  "result": "<what happened after>"
}
```

Also record the two structural numbers, which need no model run:

| Metric | Before | After |
|---|---|---|
| Always-tier tokens | | |
| Validator errors | | |

Procedure:

1. Record every baseline on the **pre-change** tree. A baseline written after the change is
   not a baseline.
2. Apply the section 7 moves.
3. Re-run all cases and the validator.
4. Report each case as improved / unchanged / regressed. Report regressions.

An audit whose cases all pass before the change proved nothing — either the findings were
cosmetic or the cases are too easy. Say which.

## Unverified

Everything considered and not established: findings without evidence, load frequencies that
were guessed, claims that could not be checked. This section is required. An empty one
means the audit did not look hard enough.
