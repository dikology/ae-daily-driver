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

**Status:** ready-for-agent

- [ ] `do-jira-task` has an `evals/cases.json` with execution expectations, including one covering
      its refusal to execute on a context-gate fail, and no trigger cases
- [ ] `dataviz` has trigger cases: positives for prompts it should own, and negatives naming
      `sprint-digest` and `triage-analytics` as the owners of prompts it should not
- [ ] `telegram-git-diff` has an execution case asserting that a link-fix-shaped diff yields an
      omit verdict with a reason, and one asserting a substantive diff still yields a draft
- [ ] All three files parse against the rung-2 schema and pass the runner's deterministic half
- [ ] The model-in-the-loop half has been run once against these three, deliberately, and the
      result recorded
- [ ] R7.1 no longer fires for these three skills
- [ ] The declared remainder in `docs/agents/library-increments.md` is updated to the three skills
      that are left
- [ ] Anything the format could not express is written down, so batch 2 changes the schema once
      rather than working around it five times
