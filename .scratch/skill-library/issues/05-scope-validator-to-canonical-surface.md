# 05: Scope the validator to the canonical surface

**What to build:** The audit currently walks the whole repository, so findings from the `.cursor/`
sandbox — dogfood and experiments that are *supposed* to be unfinished — arrive in the same
undifferentiated list as findings from skills people actually copy. A large share of the current
warnings come from there. Because signal and noise are mixed, no finding can be treated as
actionable and a new regression is indistinguishable from the existing pile.

The audit gains a scope restricted to the canonical surface: `skills/` and `.claude/skills/`. The
sandbox is reported as **declared excluded**, not silently dropped — a reader must be able to tell
"checked and clean" from "never looked at".

This is a change to a published skill's script, so it is a library increment like any other, and it
is covered for free by the existing test harness.

**Blocked by:** 01, 02.

**Status:** ready-for-agent

- [ ] The audit can be run scoped to the canonical surface, and that scope is what the increment
      definition of done refers to when it says "green"
- [ ] Excluded directories are named in the report output as a declared exclusion, with the count
      of what was skipped
- [ ] Findings for files on the canonical surface are unchanged by this ticket — scoping removes
      noise, it does not weaken a check
- [ ] Tests at the existing seam cover a tree containing a sandbox directory, asserting which rules
      fire and which are excluded, following the established build-a-tree-in-a-tempdir pattern
- [ ] The free test suite passes
- [ ] `reviewing-agent-context`'s own documentation describes the scope behaviour, since consuming
      repos get this script too
