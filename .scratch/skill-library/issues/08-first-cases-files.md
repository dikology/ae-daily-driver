# 08: First cases files — execution, trigger, and the omit verdict

**What to build:** Three worked examples that turn "I don't know what eval to write" into a
template, and that find out whether the rung-2 shape survives contact with a second and third skill
before four more tickets are committed to it. That is the point of stopping at three: a bad format
costs one ticket to discover, not five.

**`do-jira-task` — the execution half.** Command-only, so it needs expectations and no trigger
cases. It is the natural first example because its behaviour is already specified: it re-scores the
context gate and refuses to execute on a fail. An eval that lets a fail through would be catching a
real regression, not a hypothetical.

**`dataviz` — the trigger half.** Auto-triggerable, and the skill most likely to collide with
others: analytics prompts sit between it, `sprint-digest`, and `triage-analytics`, and boundary
bleed between those three is the defect rung 2 exists to catch. Its negative cases name the sibling
that should win instead.

**`telegram-git-diff` — the omit verdict.** Ticket 02 built a decline rule and verified it by hand.
An untested decline rule is exactly the kind of thing that quietly stops declining, and this skill
now runs at the end of every increment, so the failure would be silent and frequent.

After this ticket, R7.1's declared remainder is `sprint-digest`, `triage-analytics`, and
`retrospective`, closing in batch 2.

**Blocked by:** 02, 07.

**Status:** ready-for-human

- [x] `do-jira-task` has an `evals/cases.json` with execution expectations, including one covering
      its refusal to execute on a context-gate fail, and no trigger cases
- [ ] `dataviz` has trigger cases: positives for prompts it should own, and negatives naming
      `sprint-digest` and `triage-analytics` as the owners of prompts it should not
- [x] `telegram-git-diff` has an execution case asserting that a link-fix-shaped diff yields an
      omit verdict with a reason, and one asserting a substantive diff still yields a draft
- [x] All three files parse against the rung-2 schema and pass the runner's deterministic half
- [x] The model-in-the-loop half has been run once against these three, deliberately, and the
      result recorded
- [x] R7.1 no longer fires for these three skills
- [x] The declared remainder in `docs/agents/library-increments.md` is updated to the three skills
      that are left
- [x] Anything the format could not express is written down, so batch 2 changes the schema once
      rather than working around it five times

## Comments

**2026-10-11 — implemented, with one criterion not met as written.** Evidence: validator finding
(kind 1) — R7.1 fired for `do-jira-task`, `dataviz-reports` and `telegram-git-diff`.

Status is `ready-for-human` rather than closed because of the first point below.

- **The `dataviz` criterion cannot be met as written, and is left unticked.** It asks for negatives
  naming `sprint-digest` and `triage-analytics` as owners. Both carry
  `disable-model-invocation: true`, and ticket 07's runner fails an owner that is command-only,
  since it can never win a prompt. That criterion and "pass the runner's deterministic half"
  exclude each other. The file names the three owners that do resolve — `generate-status-report`,
  `reviewing-agent-context`, `retrospective` — so the sprint-report and "review this" collisions
  are covered, and the triage collision is not covered at all. Decision for the author: accept
  this, or let batch 2 add an ownerless negative (first item in the list below).
- The skill is `dataviz-reports`; the ticket and the old remainder table said `dataviz`.
- Each file carries three execution cases, the floor rubric line R7.1 states, although the schema
  enforces one. `telegram-git-diff`'s third covers ticket 02's other rule: an outcome the issue file
  promises and the diff does not evidence is not claimed.
- Execution prompts carry their inputs inline (a pasted ticket, a pasted diff) because a headless
  run has no Jira and should not depend on this repo's history.
- **Runner change, needed for the definition of done.** `--skill telegram-git-diff` failed with
  "no cases file" on the stale copy under `.cursor/skills/`, which shares the name. `--skill` now
  runs the copies of a named skill that carry a cases file and fails only when none does — so a
  copy without cases is now passed over without a row when a sibling copy has them. One new
  test; `SKILL.md` says so in one sentence.
- Validator `--scope canonical`: 0 errors, 7 warnings. R7.1 fires for `sprint-digest`,
  `triage-analytics`, `retrospective` (the declared remainder) and for `generate-status-report`,
  which also still fires one R2.5 and two R3.4. That skill is outside the table, as ticket 07
  already noted; this ticket was told to leave three and did.
- Free suites: `test_audit_context.py` 25 pass, `test_run_skill_evals.py` 20 pass,
  `labs/evals/test_graders.py` 24 pass. `labs/` untouched.
- `/telegram-git-diff`: draft produced (in the session reply).

### The model-in-the-loop run

Run once, 2026-10-11, `--with-model` with the default `claude -p`, one process per skill.
Deterministic half: 3 schema rows pass. Model half: 15 cases, 13 pass, 2 fail, 0 skip.

| Skill | Trigger + | Trigger − | Execution |
| --- | --- | --- | --- |
| `do-jira-task` | n/a | n/a | 3 of 3 |
| `dataviz-reports` | 3 of 3, all ranked 1 | 3 of 3 | 1 of 3 |
| `telegram-git-diff` | n/a | n/a | 3 of 3 |

The refusal on a context-gate fail held, and so did the omit verdict on a link-fix diff and the
draft on a substantive one.

The two failures, both `dataviz-reports`:

- **eval 1, "ends with a verdict line".** The runner does not keep the response it graded, so the
  prompt was run once more by hand. That response had a correct verdict ("Not approved", six Block
  findings) as its *first* line, where Section C says to end with it. A real, small deviation from
  the skill's text: admissible evidence for a ticket, not fixed here.
- **eval 3, "exactly one insight card".** Not explained. The by-hand rerun produced one card and
  said it was stopping at one, with three extra bullets of findings under it that a judge could
  count as further insights. Either the first response differed or the judge varies; one run cannot
  tell which.

No case was loosened to get a pass. The run left no files behind in the working tree.

After the run, review found three expectations that asked for more than their skill states, and
they were corrected without a rerun: `dataviz-reports` eval 2 no longer requires a table (Section E
allows one, it does not demand one), eval 3 no longer requires follow-up questions to be offered,
and `do-jira-task` eval 3 no longer fails a correct blocked reply for having no plan. None of the
three was the expectation behind a recorded failure, so the table above still describes the files
as committed, less those expectations.

### What the format could not express

For batch 2 to change the schema once.

1. **A negative with no auto-triggerable owner.** "This prompt belongs to a skill the user invokes
   by name, so nothing should claim it" has no shape. It is the case the ticket wanted for
   `sprint-digest` and `triage-analytics`. Candidate: a negative with `owner` omitted that passes
   when the skill is absent from the ranking.
2. **An owner that lives in the consuming repo** (carried from ticket 07). A cases file ships with
   its skill; its owners fail wherever the sibling is not installed.
3. **Inputs for an execution case.** No fixture, working-tree state or tool stub can be declared,
   so a diff or a ticket has to be pasted into the prompt. `do-jira-task`'s Jira read and
   `telegram-git-diff`'s scope detection are never exercised.
4. **More than one turn.** `do-jira-task` waits for confirmation and then executes, and re-scores
   when the user answers in session. A case is one prompt, so only the stop is tested.
5. **What the agent did, as opposed to what it said.** The judge sees the final reply only. "No
   file written", "nothing sent to Telegram" and "no Jira comment posted" are graded on the absence
   of a claim.
6. **The graded response is thrown away.** A `fail` row carries the unmet expectation and not the
   response, so a failure cannot be diagnosed without paying for a rerun that may not reproduce it.
   A runner gap, not a schema one.
7. **One run per case.** A single judge verdict cannot separate a flaky case from a failing skill
   (eval 3 above). The rung-3 harness has `--runs`; rung 2 has nothing.
8. **Unknown keys are accepted silently.** `reviewing-agent-context`'s cases carry `"kind":
   "execution"`, which nothing reads. A typo in a field name would pass the same way.
9. **A skill installed under two roots is ranked by whichever description is discovered last** —
   here the stale `.cursor/` copy. Harmless for the three skills in this ticket; it would matter
   for an auto-triggerable skill with a stale copy.
