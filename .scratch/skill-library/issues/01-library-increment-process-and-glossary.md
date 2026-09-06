# 01: Library increment process and glossary

**What to build:** A written definition of what a library increment is and when one is done, so
that every later ticket in this batch has a standard to be checked against. Today "one unit of
improvement work" is re-decided per ticket, and the vocabulary the rest of the batch depends on —
canonical surface, sandbox, eval ladder, portability contract — exists only in conversation.

The process document carries three rules: the **evidence bar** (no ticket without an observed
failure behind it — a rubric line the validator flags, a trigger eval that fires wrong, or a
transcript where a skill misbehaved in real use; other skill libraries inform a solution but never
justify a ticket), the **eval ladder** with its three rungs and the tier rule that decides which
rung a change needs, and the **definition of done** for an increment.

It lives in `docs/agents/` with a one-line pointer from `AGENTS.md`, matching how the issue
tracker, triage labels, context gate, and domain docs are already handled. `AGENTS.md` is the only
always-tier file in the repo; inlining three process rules there would tax every session to serve
only the sessions that work on the Library.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] `docs/agents/library-increments.md` exists and states the evidence bar, naming the three
      admissible kinds of evidence and stating explicitly that another repo's skill is not evidence
- [x] The same document states the eval ladder as three rungs with what each costs and which skills
      it applies to, plus the tier rule: if a change can alter the model's output on identical
      input, it needs an eval; otherwise it is structural
- [x] The same document states the increment definition of done: evidence cited, change made,
      validator green over the canonical surface, rung-2 cases for touched skills pass, and
      `/telegram-git-diff` invoked with either a draft or an omit verdict as the result
- [x] `AGENTS.md` gains a one-line pointer under its own heading, in the style of the existing
      pointers; no process rule is inlined there
- [x] `CONTEXT.md` defines **library increment**, **canonical surface**, **sandbox**, **eval
      ladder**, and **portability contract**, each with an `_Avoid_` line, following the existing
      entry format
- [x] The **library increment** entry's `_Avoid_` line reserves bare "increment" for
      `sprint-digest`'s client-facing meaning, so the collision is recorded rather than resolved by
      accident
- [x] The **sandbox** entry scopes itself to `.cursor/skills/` *in this repo* and states that it is
      dogfood and experiments, out of scope, and excluded from the standard
- [x] The existing **Install** entry is sharpened to name the copy direction and destination: from
      `skills/` into the consuming repo's agent folder
- [x] The validator's always-tier token budget has not materially grown as a result of this ticket
      (1344 → 1381 always-tier tokens, +2.7%, from the AGENTS.md pointer)
