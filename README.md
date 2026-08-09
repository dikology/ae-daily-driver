# ae-daily-driver

Curated **showcase library** of agent skills, rules, MCP examples, and diagrams for analytics engineering.

Steal the kit. Run it in the repos where the work happens. This repo is not a wiki, semantic layer, or session store.

## What this is

| This Library | Sibling homes / consuming repos |
| --- | --- |
| Skills, rules, MCP wiring, diagrams | Durable entity descriptions |
| Presentable, copy-installable kit | Where AE sessions actually run |
| Glossary + ADRs for the kit itself | Dashboards, sources, dbt models, metrics, glossary |

**Install model:** copy into each consuming repo (first dogfood target: `tasks`). No shared runtime package.

## Intended layout

```
skills/          # canonical skill sources (showcase)
mcp/             # MCP config examples (coming)
diagrams/        # concept diagrams
docs/adr/        # architectural decisions
docs/agents/     # issue tracker, triage, domain-doc rules
CONTEXT.md       # ubiquitous language for this Library
AGENTS.md        # agent entrypoint for working on the Library
.cursor/         # runtime copies for Cursor in this repo
```

Canonical kit content belongs under root `skills/` and `mcp/` (see [ADR-0002](docs/adr/0002-showcase-layout-skills-and-mcp-at-root.md)). Agent directories like `.cursor/` get copies as needed.

## Core idea: unwrap

In a consuming repo, an **AE session** that touches data **entities** should:

1. Build a **touch-map** (Jira signals + in-session observation → human confirm)
2. Run **closeout** against a single **adequate context** OR-bar:
   - docs exist in the sibling home, **or**
   - discoverable via MCP with enough context (e.g. OpenMetadata description filled)
3. Report gaps in chat and **propose** sibling-home / OM edits — no silent Jira writes from unwrap

v1 entity kinds: dashboard, source, dbt model, metric, glossary term.

See [CONTEXT.md](CONTEXT.md) for definitions, and [diagrams/scheme.excalidraw](diagrams/scheme.excalidraw) for the task → entity picture.

## Decisions

- [ADR-0001 — Library is workflow kit only](docs/adr/0001-library-is-workflow-kit-only.md)
- [ADR-0002 — Showcase layout: `skills/` and `mcp/` at root](docs/adr/0002-showcase-layout-skills-and-mcp-at-root.md)

## Working on this repo

Library development uses local markdown issues under `.scratch/` (see [docs/agents/issue-tracker.md](docs/agents/issue-tracker.md)). That tracker is for evolving the kit — not for AE unwrap closeout.

Useful skills already installed under `.cursor/skills/` (Matt Pocock set + local): `grill-with-docs`, `domain-modeling`, `wayfinder`, `to-tickets`, `writing-for-agents`, and others.

## Status / next

- [x] Domain language + ADRs
- [ ] Root `skills/` / `mcp/` populated as the showcase surface
- [ ] Import `do-jira-task` from elsewhere; compose with unwrap
- [ ] Ship unwrap skill; dogfood in `tasks`
- [ ] MCP examples

Glossary terms and deferred items live in [CONTEXT.md](CONTEXT.md).
