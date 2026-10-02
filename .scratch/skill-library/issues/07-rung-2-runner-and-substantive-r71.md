# 07: Rung-2 runner, shared schema, and a substantive R7.1

**What to build:** Rung 2 of the eval ladder currently does not exist as a check. One skill has an
`evals/cases.json`; nothing executes it. The rubric line that is supposed to require evaluations
passes on the *existence of a directory named `evals/`*, so it is satisfied by `mkdir` — and any
repo that has already copied this skill is being told it has evaluations when it may have an empty
folder. Separately, two files named `cases.json` in this repo share a filename and nothing else:
one is the rung-2 shape, the other belongs to the rung-3 harness and is read by a different runner.

This ticket makes rung 2 real and closes the gap that let the two schemas diverge, by putting the
runner and the check that enforces the schema in the same place, sharing one definition of it.

The runner lives alongside the existing validator inside `reviewing-agent-context`. That skill's
own rubric already scores executable validators and evaluation-driven iteration, so running the
evals is inside its stated job. The cost, accepted knowingly: the skill widens from "audits" to
"audits and runs", and it ships to consuming repos under ADR-0004 like everything else.

The runner splits in two. The deterministic half — schema parsing, branching on
`disable-model-invocation`, resolving each negative case's declared owner to a skill that actually
exists — needs no model and runs on every commit. The model-in-the-loop half is opt-in, matching
how the rung-3 harness already separates free grader tests from paid runs.

R7.1 becomes substantive in the same change: it requires an eval file that parses against the
schema, and it demands trigger cases only from auto-triggerable skills. Four of the seven skills on
the canonical surface are command-only, so ownership cases would test nothing for them.

No new cases file is needed to demonstrate this: the runner is demoable against the cases file
`reviewing-agent-context` already carries and that has never been executed.

**Blocked by:** 03, 05.

**Status:** ready-for-agent

- [ ] A runner reads a skill's `evals/cases.json` and reports per-case verdicts
- [ ] The rung-2 schema is defined once and used by both the runner and the R7.1 check
- [ ] The deterministic half runs with no model and catches: a file that does not parse, trigger
      cases on a command-only skill, and a negative case naming an owner that does not exist
- [ ] The model-in-the-loop half is opt-in and is not required for the free suite to pass
- [ ] R7.1 requires an eval file that parses, and no longer passes on an empty directory
- [ ] R7.1 requires execution expectations from every skill, and trigger cases only from skills
      without `disable-model-invocation`
- [ ] Running the runner against `reviewing-agent-context`'s existing cases file produces verdicts
- [ ] Tests cover both seams following the existing tempdir-tree pattern, and the free suite passes
- [ ] The rung-3 harness and its own cases file are untouched; the two remain separate artifacts
- [ ] `reviewing-agent-context`'s `SKILL.md` documents the runner and the widened scope, and the
      runner itself conforms to ADR-0004
- [ ] The R7.1 tightening is recorded as a rule change for repos that already copied this skill

## Comments

**2026-10-02 — implemented.** Evidence: validator finding (kind 1) — R7.1 passed on the existence
of a path named `evals/`, and the one cases file on the canonical surface had never been executed.

- The schema is its own module, `scripts/cases_schema.py`, imported by both `audit_context.py`
  (R7.1) and the new `scripts/run_skill_evals.py`. A third file rather than a home in either
  consumer, because the runner already imports the validator and the reverse import would be a
  cycle.
- **The first run of the runner failed the existing cases file.** Both negative cases named owners
  that are not skills in this repo (`context-engineering`, `code-review-and-quality`). They were
  re-pointed at `retrospective` and `dataviz-reports`, with new prompts. Open for the author: a
  cases file ships with its skill, so these owners now fail in a consuming repo that lacks those
  two skills, exactly as the old ones failed here. The format has no way to say "owner lives in the
  consuming repo" — a candidate for ticket 08's "what the format could not express" list.
- An owner must be *another auto-triggerable* skill: the runner fails an owner that is the skill
  itself or is command-only, since neither can win a prompt.
- A negative case whose owner resolves is a `skip` without a model, not a `pass` — the ranking is
  undecided. The deterministic run over this repo is 1 pass (schema), 0 fail, 9 skip.
- R7.1 severity: a missing cases file stays a warning; a present file that fails the schema is an
  error. The schema enforces at least one execution case, not the rubric's three — ticket 08 gives
  `telegram-git-diff` two and expects R7.1 to stop firing.
- `retrospective` now fires R7.1, as the declared remainder anticipated; its row is updated.
- **Not done here, found on the way:** the declared-remainder table is out of step with the tree.
  `generate-status-report` is on the canonical surface, fires R7.1 plus one R2.5 and two R3.4, and
  is not in the table; the table says `dataviz` where the skill is `dataviz-reports`. Both predate
  this ticket.
- The model-in-the-loop half is covered by tests through an injected fake only. It has not been run
  against a real model; ticket 08 does that deliberately.
- The runner discovers skills under `.cursor/skills/` as well, because that is a live agent folder
  in a consuming repo. In this repo it means a sandbox skill can resolve as an owner.
- Free suites: `test_audit_context.py` 25 pass, `test_run_skill_evals.py` 19 pass,
  `labs/evals/test_graders.py` 24 pass. `labs/` untouched.
- `/telegram-git-diff`: draft produced (in the session reply).
