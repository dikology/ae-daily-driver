# ADR-0003 — Stable skills in `skills/`, candidates in `labs/`, promotion gated on evals

Status: accepted
Date: 2026-09-02

## Context

`skills/sprint-digest` is meant to be copied into consuming repos and used as-is.
That makes it a published interface: churn in it costs other people work.

It is also the skill most in need of iteration. Its job is data storytelling, and
storytelling quality is not visible in a diff. A prompt edit that sharpens the
headline can simultaneously teach the model to fabricate an impact number or to
split one outcome back into three ticket rows. Neither shows up when reading the
change, and neither shows up reliably in a single run — the failure is
probabilistic, so it needs to be measured across repeated runs rather than
inspected.

The two needs are in direct tension: stability for consumers, churn for the author.

Complicating it: this Library has no Jira MCP and no real tickets. It is a workflow
kit, not a place where AE sessions run (ADR-0001), so the skill's own input is
absent from the repo that owns it.

## Decision

**Two copies, one gate.**

- `skills/<name>/` is the stable arm. It changes only by promotion.
- `labs/<name>/` is the candidate arm. It is edited freely and consumed by nobody.
- `labs/evals/` runs both arms against identical fixtures and reports the delta.
- Promotion (`run_evals.py --promote`) copies candidate over stable, and is
  justified by the eval delta rather than by the author's read of the diff.

**Fixtures stand in for Jira, through a real MCP server.**
`labs/evals/mock_jira_mcp.py` speaks MCP over stdio and serves checked-in sprint
JSON through the same four tool names the skill calls. The skill runs unmodified.

**Every fixture has an answer key.** Synthetic sprints plant deliberate traps —
a three-ticket cluster that is one outcome, a thin spike that decided a quarter, a
blocked ticket that needs a human, six routine tickets that must stay in the
appendix — and the key records the correct handling of each.

## Consequences

**We can prove fabrication, not just suspect it.** Because the fixtures contain no
story-points, capacity, or financial field, any velocity chart or dollar figure in
the output is provably invented rather than merely unsourced. Against real Jira that
distinction is unavailable, which is the strongest argument for synthetic data here
and the reason not to "upgrade" these fixtures to a real sprint export later.

**Evidence-gathering is gradable.** The shim traces every call, so the harness scores
whether the skill paginated and whether it fetched detail for candidates rather than
fanning out across every ticket — behaviour invisible in the final HTML.

**Structural graders are coupled to `digest-contract.md`.** Changing the contract
means updating graders in the same commit. This is deliberate: it is what stops the
contract from rotting into a document nothing enforces.

**Two copies can drift.** If `labs/` is abandoned mid-iteration, it becomes stale and
misleading. Mitigation: `labs/` holds one skill at a time, and the candidate starts
each cycle as a byte-identical copy of stable.

**Evals cost money and minutes.** Each case run spawns a real `claude -p` session.
The grader unit tests are free and run first; the model-in-the-loop suite is run
deliberately, not on every save.

## Alternatives rejected

**Git branches only.** No second copy on disk, but the runner can only see one arm
per checkout, so stable-vs-candidate comparison needs worktrees. The comparison is
the whole point, so it should be the cheap path.

**Versioned directories (`sprint-digest/v1/`, `v2/`).** Makes history visible, but
breaks the copy-install story in ADR-0002 — a consumer browsing `skills/` would have
to work out which directory to take.

**`claude plugin eval`.** The right tool, and the harness deliberately mirrors its
shape (cases with graders, a no-plugin baseline arm, JSON results). It is early
access and not enabled on this account. If that changes, the fixtures, answer keys
and judge rubric port over; only `run_evals.py` is thrown away.

**Fixture files read directly, no MCP.** Much less code, but step 2 of the skill —
gather evidence — would never execute as written, so the evals could not catch
evidence-gathering regressions at all.
