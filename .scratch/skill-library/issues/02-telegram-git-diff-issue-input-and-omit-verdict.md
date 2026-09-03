# 02: telegram-git-diff reads the issue file and can decline

**What to build:** `/telegram-git-diff` is about to run at the end of every library increment. Two
things make that workable rather than noisy.

First, it reads the increment's issue file alongside the diff. A diff alone shows which files
moved; the issue file states what was supposed to get better. Without it, a post about a
portability-contract increment describes relative paths changing rather than skills no longer
lying about their surroundings.

Second, it can return an **omit verdict**: a stated "no post warranted", with a reason, instead of
forcing prose out of an increment with no audience consequence. Some increments in this very batch
are link fixes. A rule that produces a post for those trains its own author to ignore it.

`sprint-digest/references/increment-rubric.md` already encodes story-worthiness as headline /
watch / omit. It is prior art for the bar, referenced rather than imported — the two skills stay
separate.

The skill stays repo-local tooling in `.claude/skills/` and stays draft-only. It never sends.

Verification here is manual: run it against a real link-fix diff and confirm the decline. The
automated case for the omit verdict arrives in ticket 08, once a runner exists to execute it.

**Blocked by:** 01 (the definition of a library increment and the DoD determine what it reads and
when declining is correct).

**Status:** ready-for-agent

- [ ] Given an increment with an issue file, the skill reads that file as well as the diff, and the
      workflow in `SKILL.md` says so
- [ ] The diff remains the source of truth for what changed; the issue file supplies intent only,
      and the skill still does not claim outcomes the diff does not evidence
- [ ] The skill can return an omit verdict with a stated reason instead of a draft
- [ ] The bar for declining is written down in `SKILL.md`, citing the story-worthiness idea in
      `sprint-digest`'s increment rubric as prior art without copying it
- [ ] Running it on a link-fix-shaped diff produces an omit verdict, not a post
- [ ] Running it on a substantive increment still produces a draft in the existing register and
      output format
- [ ] The skill remains in `.claude/skills/`, remains `disable-model-invocation: true`, and still
      never sends or saves a draft to Telegram
