# Spec — Library increment program, batch 1

Status: ready-for-agent

## Problem Statement

The Library's canonical surface — root `skills/` plus `.claude/skills/telegram-git-diff` — has
grown to seven skills authored at different times against different assumptions. They are copied
into consuming repos and used there, so their defects are felt at work, not here.

Three things are wrong at once, and each one hides the others:

**The standard is not enforced anywhere.** The deterministic validator that would enforce it
already exists inside `reviewing-agent-context`, but nothing runs it as a gate. Run today it
reports 10 errors and 31 warnings. Some of those are genuine defects; many are noise from the
`.cursor/` sandbox, which holds dogfood and experiments that are *supposed* to be unfinished.
Because signal and noise arrive in one undifferentiated list, no finding can be treated as
actionable, and a new regression is indistinguishable from the existing pile.

**Skills lie about their surroundings.** Every one of the 10 errors is the same defect wearing
ten hats: skills link shared Library docs with `../../../`, a depth that resolves above the repo
root from `skills/<name>/`. The paths were written for an installed location, not the canonical
one. Twelve further findings are path claims (`analyses/`, `.cursor/WORKSPACE.md`,
`.out-of-scope/`) that resolve in a consuming repo and nowhere here. There is no rule saying what
a skill may assume exists outside its own directory, so every author has invented one.

**Nothing measures behaviour.** Five of seven skills have no evaluations at all. The rubric check
that is supposed to catch this (R7.1) passes on the existence of a directory named `evals/`, so it
is satisfied by `mkdir`. The one skill that has an `evals/cases.json` has no runner: nothing
executes it, and its schema is incompatible with the unrelated `cases.json` that `labs/` uses.
The expensive rung — `labs/`'s model-in-the-loop A/B — works, but it holds one skill at a time and
costs real money, so it cannot be the only rung.

The consequence is that improving a skill is indistinguishable from rewriting it. Without a
measured "before", any edit is a preference, and borrowing structure from other people's skill
libraries — the obvious next move — would produce a rewrite wearing the costume of an improvement.

## Solution

A standing process for **library increments**, plus the first batch of ten of them.

The process has three parts:

**An evidence bar.** No ticket exists without an observed failure behind it: a rubric line the
validator flags, a trigger eval that fires wrong, or a transcript where the skill misbehaved in
real use. Other people's skill libraries are input to a ticket's *solution*; they are never its
justification. The backlog is seeded by running `/reviewing-agent-context` over this repo and kept
fed by running `/retrospective` over work-repo transcripts.

**An eval ladder** with three rungs of ascending cost, so "what eval should this skill have?" has
an answer that does not always come back "an expensive one":

| Rung | What it is | Applies to |
| --- | --- | --- |
| 1 | The `audit_context.py` validator — deterministic, free, no model | every skill |
| 2 | `skills/<name>/evals/cases.json` — execution expectations always; trigger cases only for auto-triggerable skills | every skill |
| 3 | `labs/` A/B against answer keys — expensive, one skill at a time | prose output only |

The tier rule: **if a change can alter the model's output on identical input, it needs an eval.**
Everything else is structural and goes straight to `skills/`. Under this rule, only
`sprint-digest` and arguably `dataviz` ever touch rung 3, which unblocks the other five skills
from the one-candidate-at-a-time throttle in ADR-0003.

**A portability contract.** A skill may reference the world outside its own directory, but it must
*declare* what it expects rather than pointing a relative path at it. Declarations replace links;
the validator checks that declarations exist rather than trying to resolve paths that are correct
in exactly one of the two places a skill lives.

Batch 1 then makes the validator green over the canonical surface, so that from the next batch
onward a finding means something. Green here carries one declared remainder: R7.1 continues to fire
for `sprint-digest`, `triage-analytics`, and `retrospective`, whose rung-2 cases are deliberately
deferred to batch 2. That exception is named in the process document rather than left as a warning
everyone slowly stops seeing.

## User Stories

1. As the Library author, I want a written definition of a library increment, so that "one unit of
   improvement work" means the same thing in every ticket rather than being re-decided each time.
2. As the Library author, I want the word "increment" to keep its client-facing meaning from
   `sprint-digest`, so that a term already shipped in a skill is not quietly overloaded by the
   Library's own process vocabulary.
3. As the Library author, I want the evidence bar written down as a rule, so that I can refuse my
   own tickets when they are motivated by envy of another repo rather than by a defect.
4. As the Library author, I want the increment process to live in `docs/agents/` with a pointer in
   `AGENTS.md`, so that three process rules do not tax every session's always-loaded context to
   serve only the sessions that work on the Library.
5. As the Library author, I want `CONTEXT.md` to define canonical surface, sandbox, library
   increment, eval ladder, and portability contract, so that later tickets can use those words
   without re-explaining them.
6. As the Library author, I want the existing `Install` glossary entry sharpened to say skills are
   copied from `skills/` into the consuming repo's agent folder, so that the glossary matches how
   I actually distribute them.
7. As the Library author, I want the validator scoped to the canonical surface, so that
   deliberately-unfinished sandbox experiments stop generating findings I must mentally discard.
8. As the Library author, I want the sandbox exclusion to be a declared scope rather than silence,
   so that a reader can tell the difference between "checked and clean" and "never looked at".
9. As the Library author, I want a green validator to be reachable, so that the next finding that
   appears is a regression rather than another entry in a permanent backlog.
10. As the Library author, I want R7.1 to require an eval file that parses, so that the check
    cannot be satisfied by creating an empty directory.
11. As the Library author, I want R7.1 to demand trigger cases only from auto-triggerable skills,
    so that command-only skills are not forced to write ownership cases that nothing can exercise.
12. As a consuming-repo user, I want a skill to declare what it needs from my repo, so that I learn
    at install time what I must provide rather than when a path silently fails to resolve.
13. As a consuming-repo user, I want skills to stop linking Library-internal docs with relative
    paths, so that copying a skill into my repo does not produce links pointing above my repo root.
14. As a consuming-repo user, I want a skill that cannot find a declared dependency to say so, so
    that it degrades with a stated reason instead of behaving as though the document were empty.
15. As the Library author, I want the portability contract recorded as an ADR, so that a future
    reader understands why skills declare dependencies instead of linking them.
16. As the Library author, I want `sprint-digest`'s boundary table to be legitimate under the
    contract, so that naming skills that live in my work repos is a declared expectation rather
    than a broken reference.
17. As the Library author, I want the `context-gate.md` single-sourcing to survive the change, so
    that the gate is not duplicated into three skills that then drift apart.
18. As the Library author, I want `README.md`'s dead diagram link fixed, so that the showcase
    surface does not advertise a file that is not there.
19. As the Library author, I want `AGENTS.md`'s claim about `.cursor/skills/sprint-digest/`
    corrected, so that the entry-point document does not describe a layout that no longer exists.
20. As an agent choosing between skills, I want `triage-analytics`'s description to state its
    trigger condition, so that I can tell when to use it without reading its body.
21. As an agent loading `persona.md`, I want a table of contents in a 184-line reference, so that I
    can find the register I need without loading the whole file.
22. As the Library author, I want a runner that executes `skills/<name>/evals/cases.json`, so that
    rung 2 is a check rather than a documented format nobody runs.
23. As the Library author, I want the runner and the R7.1 check to share one schema definition, so
    that the two-incompatible-`cases.json` situation cannot recur.
24. As the Library author, I want the runner's deterministic half to run without a model, so that
    schema errors and bad negative-owner references are caught for free in CI.
25. As the Library author, I want the model-in-the-loop half to be opt-in, so that eval cost is
    incurred deliberately, matching how `labs/` already behaves.
26. As the Library author, I want trigger cases exercised for `dataviz`, `retrospective`, and
    `reviewing-agent-context`, so that the three skills genuinely competing for the same analytics
    prompts are the ones whose boundaries get tested.
27. As the Library author, I want one worked execution-expectation example on `do-jira-task`, so
    that "I don't know what eval to write" becomes a template to copy.
28. As the Library author, I want to find out whether the `cases.json` shape survives a second
    skill before committing four more tickets to it, so that a bad format is discovered at a cost
    of one ticket rather than five.
29. As the Library author, I want `/telegram-git-diff` to read the increment's issue file alongside
    the diff, so that a post describes what got better rather than which files moved.
30. As the Library author, I want `/telegram-git-diff` to be able to return an omit verdict, so
    that a link-fix increment produces a stated "no post warranted" instead of forced prose.
31. As the Library author, I want the omit verdict itself covered by an execution case, so that a
    decline rule does not quietly stop declining.
32. As the Library author, I want the Telegram draft to be a step in every increment's definition
    of done, so that the habit is enforced by the ticket rather than by memory.
33. As the Library author, I want `telegram-git-diff` to stay repo-local tooling in
    `.claude/skills/`, so that a persona specific to my own channel is not presented as stealable
    kit.
34. As the Library author, I want the `.cursor/` sandbox left untouched, so that experiments can
    stay unfinished without becoming a source of tickets.

## Implementation Decisions

**Scope of the canonical surface.** `skills/` plus `.claude/skills/`. The `.cursor/skills/`
directory in this repo is the **sandbox**: dogfood and experiments not yet in the Library. It is
excluded from the validator's scope, and `close-analytics-task` and `plan-analytics-sprint` remain
there unpromoted. Distribution to work repos stays a manual copy from `skills/` into that repo's
agent folder; drift between here and those copies is explicitly not addressed by this batch.

**Process documentation.** A new `docs/agents/library-increments.md` holds the evidence bar, the
eval ladder, and the increment definition of done. `AGENTS.md` gains a one-line pointer, matching
its existing treatment of the issue tracker, triage labels, context gate, and domain docs. This
keeps the repo's only always-tier file at pointer weight.

**Glossary.** `CONTEXT.md` gains five terms: **library increment** (one issue file, one commit,
one Telegram draft — with an `_Avoid_` line reserving plain "increment" for `sprint-digest`'s
client-facing meaning), **canonical surface**, **sandbox**, **eval ladder** (with its three rungs),
and **portability contract**. The existing **Install** entry is sharpened to name the copy
direction and the destination agent folder.

**ADR-0004 — portability contract.** A skill may depend on things outside its directory, but must
declare them in a "Requires from the consuming repo" section rather than linking them relatively.
`sprint-digest` already carries a prose version of such a section; it is the shape the others
adopt. The ADR records the rejected alternatives: full self-containment (kills the single-sourced
context gate and the boundary tables) and status quo (a class of breakage that is invisible in the
repo where the skill is authored and only fires where it is used).

**Declared dependencies replace shared-doc links.** `do-jira-task`, `sprint-digest`,
`triage-analytics`, and the `labs/sprint-digest` candidate copy stop linking
`../../../docs/agents/context-gate.md`. They name the document and its expected location, and state
what to do when it is absent. `context-gate.md` stays single-sourced; it is not copied into the
skills.

**`audit_context.py` gains two changes**, both inside `reviewing-agent-context`, both covered by
the existing test harness:

- A scope mechanism restricting the audit to the canonical surface, so sandbox skills stop
  producing findings. The exclusion is reported as a declared scope, not omitted silently.
- R7.1 becomes substantive: it requires an eval file that parses against the rung-2 schema, and it
  branches on `disable-model-invocation` — trigger cases are demanded only from auto-triggerable
  skills, execution expectations from all.

**The rung-2 runner lives in `skills/reviewing-agent-context/scripts/`.** That skill's own rubric
already scores R6 "executable validators and feedback loops" and R7 "evaluation-driven iteration",
so running the evals is inside its stated job rather than an expansion of it. The decisive
consequence is that the runner and the R7.1 check share one schema definition in one file. Cost
accepted knowingly: the skill widens from "audits" to "audits and runs", and it ships to consuming
repos under ADR-0004 like everything else.

**Rung-2 schema.** The shape already in `reviewing-agent-context/evals/cases.json` is the
convention, promoted to `skills/<name>/evals/cases.json` repo-wide: a `trigger` object with
`positive` (prompt, `top_k`) and `negative` (prompt, `owner`) arrays, and an `evals` array of
execution cases with a `prompt`, an `expected_output`, and named `expectations`. The `labs/`
`cases.json` is a different artifact for rung 3 and is not unified with it.

**Trigger cases are conditional.** Skills with `disable-model-invocation: true` — `do-jira-task`,
`sprint-digest`, `triage-analytics`, `telegram-git-diff` — never compete for auto-trigger, so
ownership cases test nothing for them and are not required. `dataviz`, `retrospective`, and
`reviewing-agent-context` are auto-triggerable and do require them. The `labs/` cases file
currently writes trigger negatives for the command-only `sprint-digest`; that inconsistency is
noted, not fixed in this batch.

**`telegram-git-diff` changes.** It reads the increment's issue file alongside the diff, so it can
speak to intent rather than to file movement. It gains an **omit verdict**: a stated "no post
warranted" with a reason, replacing forced prose for increments with no audience consequence. The
story-worthiness idea in `sprint-digest/references/increment-rubric.md` (headline / watch / omit)
is the model for the bar; the rubric is referenced as prior art, not imported. The skill stays in
`.claude/skills/` as repo-local tooling and remains draft-only — it never sends.

**Definition of done for every library increment**, recorded in `library-increments.md`: the
observed failure is cited; the change is made; the validator is green over the canonical surface;
any rung-2 cases for touched skills pass; `/telegram-git-diff` has been invoked and has either
produced a draft or returned an omit verdict.

**Ordering.** Three dependencies are real: the process doc and the `telegram-git-diff` changes come
first, because they define the definition of done every later ticket must satisfy; ADR-0004
precedes the work that applies it; the runner precedes the first cases files.

Two corrections the ticket cut made to this spec's original sequencing, both worth stating because
the mistakes are easy to repeat. **R7.1's tightening belongs with the runner, not with the
validator scoping** — the tightened check requires an eval file that parses against the rung-2
schema, and that schema does not exist until the runner is built; putting them in one ticket is
also what delivers the single shared schema definition that justified the runner's home in the
first place. And **applying the portability contract is one edit per skill, not two passes across
all of them** — adding a skill's declarations and removing its relative links are the same change,
so splitting them by change-type touches every skill twice and leaves each half-converted in
between.

## Testing Decisions

**What a good test is here.** These tests assert on externally observable results — which rubric
rules fire over a given repo tree, and what verdict rows a runner emits for a given cases file.
They do not assert on how a check is implemented, which internal helper it calls, or the exact
wording of a finding. A test that breaks when a check is refactored but its behaviour is unchanged
is a bad test and should be rewritten.

**Seam 1 — `audit_context.py`'s check functions.** The existing seam, and the highest one
available. `test_audit_context.py` already establishes the pattern: build a throwaway repo in a
temporary directory, run the checks over it, and assert on the set of rules that fire. This one
seam covers the whole documentation half of the batch — the ADR's application, the declared
dependencies, the "Requires" headers, the dead link and false path claim, the trigger condition and
the reference table of contents are all verified as "these rules stop firing over this tree",
rather than by bespoke per-ticket tests. The scope mechanism and the tightened R7.1 are tested at
the same seam: a tree containing a sandbox directory, and trees with an empty `evals/`, a
malformed cases file, and a valid one against both auto-triggerable and command-only skills.

**Seam 2 — the rung-2 runner's command-line surface.** New, and kept at the same altitude as seam
1 deliberately. Tests build a synthetic skills tree and assert on the runner's verdict rows. The
model call is injectable, which splits the runner in two: the deterministic half — schema parsing,
`disable-model-invocation` branching, resolution of `negative.owner` to a skill that exists —
runs free on every commit; the model-in-the-loop half is opt-in, matching how `labs/` already
separates free grader unit tests from paid runs.

**Prior art.** `skills/reviewing-agent-context/scripts/test_audit_context.py` for the tmpdir-tree
pattern and the rule-set assertion style. `labs/evals/test_graders.py` for the convention that
grader logic is unit-tested for free and separately from anything that spawns a model.
`labs/evals/run_evals.py` for the arm/case/report structure, as a shape to echo rather than code to
share — the two runners stay separate.

**Not covered by tests.** Prose quality in `CONTEXT.md`, `library-increments.md`, and ADR-0004; the
usefulness of a Telegram draft as opposed to its grounding. The `telegram-git-diff` omit verdict is
tested through seam 2 as an execution expectation, which checks that a link-fix diff produces a
decline — not that the resulting prose is good.

## Out of Scope

- **The `.cursor/` sandbox.** Not audited, not promoted, not deleted. `close-analytics-task` and
  `plan-analytics-sprint` stay as they are.
- **Drift between `skills/` and the copies in work repos.** Distribution remains a manual copy. No
  sync mechanism, no marketplace, no per-skill changelog in this batch.
- **Importing skills from other skill libraries.** They inform solutions; they do not seed the
  backlog. No new skills are added.
- **Rung-2 cases for `sprint-digest`, `triage-analytics`, and `retrospective`.** Deferred to batch
  2, on purpose: the format gets tested against three worked examples — one execution, one trigger,
  one omit verdict — before more tickets are committed to it. A bad format then costs one ticket to
  discover rather than five.
- **Any rung-3 work.** `sprint-digest`'s `labs/` cycle and its `digest-contract.md` are untouched;
  the contract is coupled to the graders, so changing it is expensive and belongs in its own batch.
- **Extracting a shared HTML-report reference between `dataviz` and `sprint-digest`.** Only
  revisited if batch 2's trigger evals demonstrate a real collision.
- **The `labs/` cases file's trigger negatives for a command-only skill.** Noted, deferred.
- **`telegram-git-diff`'s audience and register work.** Deferred until a draft actually comes out
  wrong.
- **Making the validator a git hook or CI gate.** This batch makes green reachable; enforcing it
  automatically is a later decision.

## Further Notes

The batch is eight tickets, published as one file each under `.scratch/skill-library/issues/`:

| # | Ticket | Blocked by |
| --- | --- | --- |
| 01 | Library increment process and glossary | — |
| 02 | `telegram-git-diff` reads the issue file and can decline | 01 |
| 03 | ADR-0004 — portability contract | 01, 02 |
| 04 | Apply the portability contract across the canonical surface | 03 |
| 05 | Scope the validator to the canonical surface | 01, 02 |
| 06 | Clear the remaining validator findings | 04, 05 |
| 07 | Rung-2 runner, shared schema, and a substantive R7.1 | 03, 05 |
| 08 | First cases files: execution, trigger, and the omit verdict | 02, 07 |

The graph forks once, at 05: it is independent of the ADR work, so 03→04 and 05 can proceed in
either order or together. Everything else is a chain.

Two facts worth carrying into implementation, because both were discovered by measurement rather
than by reading and neither is obvious from the code:

- R7.1 currently passes on the existence of a path named `evals/`. Any skill in any repo that has
  copied `reviewing-agent-context` is being told it has evaluations when it may have an empty
  directory. Ticket 04 tightens this, which is a rule change for those consumers.
- `reviewing-agent-context/evals/cases.json` and `labs/evals/cases.json` share a filename and
  nothing else. They are different artifacts at different rungs and stay that way; the shared name
  is a trap for anyone who assumes otherwise.

ADR-0003's constraint that `labs/` holds one candidate at a time is unchanged. The eval ladder is
what makes that constraint survivable: it moves five of seven skills onto rungs that do not queue.
