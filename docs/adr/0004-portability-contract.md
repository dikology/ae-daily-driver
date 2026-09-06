# ADR-0004 — Portability contract: declare outside dependencies, do not link them

Status: accepted
Date: 2026-09-06

## Context

A skill on the canonical surface lives at `skills/<name>/`. When it is installed
into a consuming repo it lives one level deeper — `.claude/skills/<name>/` or
`.cursor/skills/<name>/`. A relative path written from one of those depths is wrong
at the other. Nobody wrote down which depth to assume, so each author picked one,
and three defect classes fell out of that gap:

- **Shared Library documents.** Three skills link `docs/agents/context-gate.md`
  (`sprint-digest`, `do-jira-task`, `triage-analytics`; the increment rubric links
  it in prose too) with a `../../../` depth that resolves to the repo root only
  from a three-deep install location. From the canonical
  `skills/<name>/` surface — the surface the validator checks and the one a reader
  browses — every one of those links resolves *above* the repo root. The document
  is real and single-sourced on purpose; the link to it is broken exactly where the
  skill is authored.

- **Sibling skills that live in consuming repos.** `sprint-digest`'s boundary table
  routes work away to `generate-status-report`, `jira-sprint-dashboard`, and
  `plan-analytics-sprint`. None is on the canonical surface; two exist only in work
  repos. Read as references they look broken; they are actually legitimate
  cross-repo expectations with no way to say so.

- **Paths that resolve only where the skill runs.** Twelve backticked path claims
  across five skills — an output directory for analyses, an OUTBOX file, a
  consuming-repo PRODUCT or DESIGN doc, an impeccable-skill script path, a
  project-relative Cursor skills directory — assert locations that exist in a
  consuming repo mid-session and nowhere on the canonical surface. The validator
  flags them (R8.6); a reader cannot tell a genuine typo from a correct reference
  to a consuming-repo directory.

All three are the same missing rule: what may a skill assume exists outside its own
directory, and how does it say so.

`sprint-digest` already carries a prose version of the answer — a "Needs from the
consuming repo (ask if missing)" line that names its Jira inputs instead of
pointing a path at them. That is the shape the rest adopt.

## Decision

**A skill may depend on the world outside its own directory, but must declare the
dependency rather than point a relative path at it.**

**The mechanism is a `Requires from the consuming repo` section** in `SKILL.md`.
Each entry names:

1. **What** the dependency is — a document, a sibling skill, a directory.
2. **Where** it is expected to be found, as a description, not a resolvable
   relative link (`docs/agents/context-gate.md` at the repo root of a repo that has
   installed the context gate; a `PRODUCT.md` / `DESIGN.md` at the consuming repo
   root; an analyses output directory in the consuming repo, created if absent).
3. **What the skill does when it is absent** — degrade with a stated reason. The
   skill announces the specific dependency it could not find and the step it is
   therefore skipping or narrowing, then asks or proceeds in the reduced mode. It
   must not carry on as though the missing document were present but empty: a
   `context-gate.md` that cannot be found is reported as "context-gate cross-check
   skipped: no context-gate.md at the repo root", never silently treated as a gate
   with nothing in it.

The three finding classes resolve under this one rule:

- **Shared Library documents** are declared, not linked. The context gate stays
  single-sourced in `docs/agents/context-gate.md` — it is not copied into the
  skills, which its own opening line forbids. Skills stop linking it with a
  cross-repo-relative path and instead declare it as a required document with a
  stated fallback.
- **Sibling skills in consuming repos** are declared as consuming-repo
  expectations. `sprint-digest`'s boundary-table siblings are recorded as "expected
  in the consuming repo; if absent, this skill still runs and says so" rather than
  read as broken references.
- **Paths that resolve only where the skill runs** become declared expectations
  about the consuming repo's layout, not assertions about a directory on the
  canonical surface.

## Consequences

**This tightens the contract for anyone who has already copied these skills.**
Consumers who installed an earlier copy have skills whose relative links happened
to resolve at their three-deep install depth. After conversion those links are
gone, replaced by a declared section they may need to satisfy (or explicitly
accept the degraded path for). This is a deliberate, one-time cost paid to make the
canonical surface the authoritative one.

**The validator checks for a declaration, not a resolvable path.** Rule R4.3 stops
firing on the shared-document links because the links are gone; R8.6 stops firing
on consuming-repo path claims because they move into the declared section. A skill
that depends on something outside itself without declaring it becomes the new
finding.

**Skills gain a uniform header.** Every canonical skill grows a
`Requires from the consuming repo` section even when short. The cost is a few lines
per `SKILL.md`; the return is that "what does this skill assume?" is answerable
from one place.

**Absent-dependency behaviour is now testable.** Because the rule says degrade with
a named reason, a rung-2 case can assert the skill emits that reason rather than
producing output that looks complete.

**`labs/` moves in step.** ADR-0003 keeps `labs/sprint-digest` as a byte-identical
candidate of the stable skill. It receives the same declaration edits in the same
increment, or the next eval run compares two arms that differ by more than the
change under test.

## Alternatives rejected

**Full self-containment — a skill references nothing outside itself.** This would
force the context gate to be copied into every skill that consults it, producing
three-plus copies that drift, and it is the exact thing `context-gate.md`'s opening
line forbids. It would also delete the boundary tables, which route work correctly
precisely by naming skills that live elsewhere. Both the single-sourced gate and
the boundary tables earn their keep; a rule that outlaws them costs more than the
breakage it prevents.

**Status quo — keep relative links, fix the depths.** Picking "three deep" and
correcting every path would make today's links resolve at install time, but the
breakage would simply move: it would be invisible in the repo where a skill is
authored and the validator runs, and would fire only in the repo where the skill
is used. That is the worst available place to discover it — a consumer hits a dead
link in a skill they copied and cannot tell whether they installed it wrong. The
declaration is checkable on the canonical surface, where the author can see it.
