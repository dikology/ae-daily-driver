# ae-daily-driver

A curated showcase library of agent skills, rules, MCP wiring, and diagrams for analytics engineering. It is a workflow kit only. Durable entity descriptions live in sibling homes. AE sessions run in consuming repos after per-repo install. Canonical kit content lives under root `skills/` and `mcp/`. The Library's own `.scratch/` is only for developing the Library — never for unwrap closeout.

## Language

**Library**:
This repository: presentable, stealable skills, rules, agents, MCP configs, diagrams, and domain docs. No entity content. No AE session artifacts.
_Avoid_: daily driver (as primary identity), wiki, knowledge base, semantic layer, session store

**Consuming repo**:
A sibling (or other) repository where Library skills are installed or invoked during real AE work.
_Avoid_: host, runtime (ambiguous)

**Sibling home**:
The consuming repo that owns durable truth for a class of entities (e.g. a semantic-layer repo for metrics and glossary terms, a dashboard catalog for Metabase unwrap, a dbt project for models, warehouse/catalog for sources).
_Avoid_: source of truth (ambiguous), mirror, cache

**AE session**:
Any analytics-engineering work period in a consuming repo that touches data entities. Not limited to a Jira task. Not hosted in the Library.
_Avoid_: ticket-only workflow, session-in-library

**Entity**:
A named data or semantic object subject to the touch-map and the adequate-context OR-bar. v1 kinds: dashboard, source, dbt model, metric, glossary term.
_Avoid_: asset (until defined), table (use source or dbt model), anything, adhoc (out of v1)

**Dashboard**:
A Metabase (or similar) presentation surface whose business context, usage, and lineage can be unwrapped.
_Avoid_: report, chart (too narrow)

**Source**:
An upstream table or raw input that feeds models or dashboards, before or outside the dbt model graph as treated in unwrap.
_Avoid_: table (alone), dataset (overloaded with semantic-layer dataset)

**dbt model**:
A model in a dbt project (warehouse or ClickHouse sibling home) representing transformed data.
_Avoid_: table, mart (unless specified)

**Metric**:
A governed business measure defined in the semantic layer, not an ad-hoc calculation in a chart.
_Avoid_: KPI (unless synonymous there), measure (ambiguous)

**Glossary term**:
A human-curated business definition in the semantic layer (or equivalent), distinct from a metric.
_Avoid_: concept, definition (alone)

**Unwrap**:
Surfacing which entities an AE session touches and whether each already has adequate context. Implemented by Library skills; executed in consuming repos.
_Avoid_: document, catalog, migrate

**Closeout**:
The end-of-session check (default on, skippable) for touched entities. The unwrap skill reports pass/gap in chat; it does not write Jira. Sibling-home (or OpenMetadata) updates and any Jira gap notes are human-driven or owned by other skills (e.g. `do-jira-task`).
_Avoid_: audit, certification, library scratch report, silent Jira edits from unwrap

**Adequate context**:
v1 closeout uses a single OR-bar: an entity passes when either (a) documents exist in its sibling home, or (b) it is discoverable via MCP with enough context — typically an OpenMetadata description filled in. Not two separate gates. Which MCPs are wired is left to the consuming repo; the Library will hold examples later.
_Avoid_: described (use adequate context), discoverable (alone as a second gate), documented (vague), complete, certified

**Gap**:
A touched entity that lacks adequate context at closeout. Listed in the chat closeout report with proposed sibling-home / OpenMetadata edits. Applying those edits or filing Jira is outside the unwrap skill's write path unless the human asks.
_Avoid_: TODO, debt (alone), silent applies

**Touch-map**:
The set of entities an AE session contacted. Built from Jira issue signals (fields/links/attachments) when a ticket exists, plus agent observation of in-session tool use and paths — then confirmed with the human.
_Avoid_: full lineage graph, inventory dump

**Install**:
Copying a Library skill from root `skills/` into the consuming repo's agent folder (e.g. `.claude/skills/` or `.cursor/skills/`) — per-repo, one direction, source to destination. The showcase story is steal-by-copy; there is no shared runtime package assumed. First dogfood target: a consuming analytics repo.
_Avoid_: symlink-from-library, global-only distribution, install-into-Library (the copy never lands back here)

**do-jira-task**:
An existing skill (lives elsewhere today; to be brought into the Library later) for working a Jira task end-to-end. Not the same as unwrap; relationship to unwrap still being sharpened.
_Avoid_: treating unwrap as the Jira workflow

**Unwrap skill**:
Library skill that builds a touch-map and runs closeout against the adequate-context OR-bar (list gaps + propose edits; no Jira writes). Canonical name and composition with `do-jira-task` deferred until that skill is imported.
_Avoid_: catalog sync, full governance migration, Jira writeback

**Showcase layout**:
Canonical Library content lives at repo-root `skills/` and `mcp/` for presentability; copied into `.cursor/` (and peers) as needed for agent use. Not a second source of entity truth.
_Avoid_: .cursor-only as the showcase surface, submodule runtime

**Library increment**:
One unit of improvement work on a Library skill: one issue file, one commit, one Telegram draft (or a recorded omit verdict), justified by one cited defect. Its definition of done lives in `docs/agents/library-increments.md`. The collision with `sprint-digest`'s "increment" is recorded here, not resolved — qualify as "library increment" in this repo's process talk.
_Avoid_: "increment" alone (that is `sprint-digest`'s client-facing term for a story-worthy clustered outcome), rewrite, refactor pass, "improvement" (unmeasured)

**Canonical surface**:
The skills the Library owns and distributes: root `skills/` plus `.claude/skills/` (whose sole current occupant is `telegram-git-diff`). This is the tree the validator (`skills/reviewing-agent-context/scripts/audit_context.py --scope canonical`) restricts its findings to and the tree an increment must leave green.
_Avoid_: all skills (the sandbox is excluded), canonical source (a sibling home owns that), surface area

**Sandbox**:
`.cursor/skills/` *in this repo* — dogfood and experiments not yet promoted into the Library (`close-analytics-task`, `plan-analytics-sprint`). Out of scope: not audited, not promoted, not deleted, excluded from the standard and the validator's scope. The exclusion is declared, not silent.
_Avoid_: sandbox for `.cursor/` in a consuming repo (there it is a real agent folder), test fixtures, scratch

**Eval ladder**:
Three rungs of ascending cost for measuring a skill's behaviour. Rung 1 — the `audit_context.py` validator (deterministic, free). Rung 2 — `skills/<name>/evals/cases.json` (execution expectations, plus trigger cases for auto-triggerable skills). Rung 3 — `labs/` A/B against answer keys (expensive, prose output only). The tier rule and per-rung detail live in `docs/agents/library-increments.md`.
_Avoid_: the evals (unqualified — name the rung), test pyramid, CI matrix

**Portability contract**:
A skill may depend on things outside its own directory but must *declare* what it expects from the consuming repo rather than point a relative path at it. The validator then checks that the declaration exists instead of resolving a path that is correct in only one of the two places a skill lives. Recorded in [ADR-0004](docs/adr/0004-portability-contract.md); the declaration mechanism is a `Requires from the consuming repo` section.
_Avoid_: full self-containment (breaks the single-sourced context gate and the boundary tables), "just fix the paths", vendoring
