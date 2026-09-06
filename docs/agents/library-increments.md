# Library increments

A **library increment** is one unit of improvement work on a skill on the canonical surface
(`CONTEXT.md` defines the term). This document is the standard every increment is checked
against, so "one unit of improvement work" does not get re-decided per ticket.

## The evidence bar

No ticket exists without an observed failure behind it. Three kinds of evidence are admissible:

1. **A rubric line the validator flags.** A concrete finding from
   `skills/reviewing-agent-context/scripts/audit_context.py` run over this repo — a rule that
   fires, with a path.
2. **A trigger eval that fires wrong.** A rung-2 trigger case where the skill claims a prompt it
   should disclaim, or disclaims one it should own.
3. **A transcript where the skill misbehaved in real use.** A recorded session from a consuming
   repo where the skill produced a wrong or degraded result, surfaced by `/retrospective`.

**Another repo's skill library is not evidence.** How another skill library solves a problem is
input to a ticket's *solution*; it is never the justification for opening one. A ticket whose
only motivation is "library X does this and we don't" is refused — take the idea to a ticket
that carries its own cited failure.

The backlog is seeded by `/reviewing-agent-context` over this repo and kept fed by
`/retrospective` over work-repo transcripts.

## The eval ladder

Three rungs of ascending cost, so "what eval should this skill have?" is not always answered
"an expensive one".

| Rung | What it is | Cost | Applies to |
| --- | --- | --- | --- |
| 1 | `audit_context.py` — deterministic validator, no model | Free | Every skill |
| 2 | `skills/<name>/evals/cases.json` — execution expectations always; trigger cases only for auto-triggerable skills | Deterministic half free; model-in-the-loop half opt-in | Every skill |
| 3 | `labs/` A/B against answer keys | Real money and minutes; one skill at a time (ADR-0003) | Prose output only |

**The tier rule:** if a change can alter the model's output on identical input, it needs an eval.
Everything else is structural and goes straight to `skills/`. Under this rule only `sprint-digest`
and arguably `dataviz` ever touch rung 3, which frees the other five skills from the
one-candidate-at-a-time throttle in ADR-0003.

### Declared remainder

Green over the canonical surface currently carries one named exception: R7.1 keeps firing for
`sprint-digest`, `triage-analytics`, and `retrospective`, whose rung-2 cases are deferred to
batch 2. It is recorded here so the warning stays legible. Any *other* R7.1 finding is a
regression.

## Definition of done

An increment is done when all of the following hold:

1. **Evidence cited.** The issue file names the observed failure and which of the three
   admissible kinds it is.
2. **The change is made** — the edit that addresses that failure, and nothing else.
3. **The validator is green over the canonical surface** — `audit_context.py` reports no errors,
   the declared remainder above aside.
4. **Rung-2 cases pass for every touched skill.** If the increment edits a skill that has a
   rung-2 cases file (`skills/<name>/evals/cases.json`), its cases pass.
5. **`/telegram-git-diff` has been invoked.** It has produced either a draft or an omit verdict
   ("no post warranted", with a reason). The draft is a ticket step, enforced here rather than
   by memory.
