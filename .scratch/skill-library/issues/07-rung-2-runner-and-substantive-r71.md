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
