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
