# 03: ADR-0004 — portability contract

**What to build:** The rule that settles what a skill may assume exists outside its own directory,
recorded as an architectural decision because it shapes every skill's header and is expensive to
reverse once applied.

Three apparently separate defect classes are one missing rule. Skills link shared Library documents
with a relative depth that is correct in exactly one of the two places a skill lives — so every
such link resolves above the repo root from the canonical surface. `sprint-digest`'s boundary table
names sibling skills that live in the consuming repos, not here. Twelve path claims across five
skills point at directories that exist where a skill runs and nowhere where it is authored. Each
author invented their own convention because none was written down.

The decision: a skill may depend on the world outside its directory, but must **declare** the
dependency rather than point a relative path at it. `sprint-digest` already carries a prose version
of such a section; it is the shape the others adopt.

The ADR must record why the two obvious alternatives lose. Full self-containment — a skill
references nothing outside itself — kills the deliberately single-sourced context gate and the
boundary tables, both of which earn their keep. Status quo produces breakage that is invisible in
the repo where a skill is authored and only fires in the repo where it is used, which is the worst
available place to discover it.

**Blocked by:** 01, 02.

**Status:** ready-for-agent

- [ ] `docs/adr/0004-portability-contract.md` exists and follows the format of the three existing
      ADRs: status, date, context, decision, consequences, alternatives rejected
- [ ] The decision states that outside dependencies are declared, not linked, and names the
      "Requires from the consuming repo" section as the mechanism
- [ ] The decision states what a skill does when a declared dependency is absent, so it degrades
      with a stated reason rather than behaving as though the document were empty
- [ ] The ADR covers all three finding classes explicitly: shared Library documents, sibling skills
      that live in consuming repos, and paths that resolve only where the skill runs
- [ ] Both rejected alternatives are recorded with the reason each loses
- [ ] The consequence that this tightens expectations for anyone who has already copied these
      skills is stated rather than left implicit
- [ ] `README.md`'s Decisions list gains the new ADR
