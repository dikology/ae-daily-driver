# 06: Clear the remaining validator findings

**What to build:** The last mile to a clean canonical surface. Four small defects remain once the
portability contract is applied and the audit is scoped, and each is a case of the Library saying
something about itself that is not true.

`README.md` advertises a diagram that is not where it says. `AGENTS.md` describes a runtime copy of
`sprint-digest` in a location that does not contain one — the repo's entry-point document
describing a layout that no longer exists. `triage-analytics`'s description says what the skill
does but never states when to use it, so an agent choosing between skills has to read the body.
`persona.md` is a 184-line reference with no table of contents, so finding one register means
loading the whole file.

**This ticket lands green, with one declared remainder.** R7.1 will still fire for the skills whose
rung-2 cases are deferred to batch 2. That exception must be named — the three skills, and the
batch that closes it — so it stays a stated remainder rather than a warning everyone slowly stops
seeing.

**Blocked by:** 04, 05.

**Status:** ready-for-agent

- [ ] `README.md`'s diagram reference resolves, or is removed if the diagram is gone
- [ ] `AGENTS.md` no longer claims a runtime copy of `sprint-digest` that does not exist
- [ ] `triage-analytics`'s description states its trigger condition as well as what it does, and
      remains within the description length limit
- [ ] `persona.md` has a table of contents, and the anti-corpus and register sections are reachable
      from it
- [ ] The validator, scoped to the canonical surface, reports zero errors and zero warnings other
      than R7.1
- [ ] The remaining R7.1 findings are named explicitly in `docs/agents/library-increments.md` as
      the declared batch-1 remainder, listing the skills and the batch that closes them
- [ ] `triage-analytics` is command-only, so its description change alters no auto-trigger
      behaviour and needs no rung-3 run
