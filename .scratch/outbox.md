# Outbox — cross-repo signals

Append-only. One entry per change made in **this repo** that matters *beyond*
this repo:

- something the `agents across repos` series can now claim,
- something that unblocks or changes the AFK pilot,
- a shift in the project narrative.

Consumed by `/wdwgfh` in the tapestry vault. wdwgfh tracks a high-water mark
per repo and only reads entries dated after its last run, so **do not delete
entries** — it decides what is already folded in.

Not a changelog. Routine commits do not belong here. If you can't name the
cross-repo stake in one sentence, it isn't an outbox entry.

## Format

```
### YYYY-MM-DD — <short title>
<2–4 lines: what changed, and why it matters outside this repo.>
Refs: <commit / file / issue>
```

---

## Entries

### 2026-09-09 — Outbox created
Cross-repo signal channel from this repo to the wdwgfh strategic review — the
first mechanism of the "cross-repo context" initiative under `agents across
repos`. Before this, wdwgfh only learned of changes here by scanning git log
and re-inferring their stakes.
Refs: `AGENTS.md` "Cross-repo signals"; `tapestry/projects/agents across repos.md`

### 2026-10-02 — Rung 2 of the eval ladder is executable; R7.1 tightened
`reviewing-agent-context` now ships a runner for `skills/<name>/evals/cases.json` and a
shared schema, and R7.1 no longer passes on an empty `evals/` directory. Any repo that
copied the skill will see R7.1 fire for skills it used to pass once it updates its copy —
a rule change for consumers, and the first cheap, model-free eval the series can point at.
Refs: `skills/reviewing-agent-context/scripts/run_skill_evals.py`; `.scratch/skill-library/issues/07-rung-2-runner-and-substantive-r71.md`
