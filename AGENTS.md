# ae-daily-driver

Library of skills, rules, and agent workflows for analytics engineering daily work across sibling repos.

## Agent skills

### Issue tracker

Issues and specs live as local markdown under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default role labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Context gate

Shared fail-closed ticket bar. `/triage-analytics` fills until pass; `/do-jira-task` re-scores and bounces on fail. See `docs/agents/context-gate.md`.

### Domain docs

Single-context layout (`CONTEXT.md` + `docs/adr/`). See `docs/agents/domain.md`.

### Skill iteration

`skills/` is the stable surface; `labs/` holds the candidate under development plus
its eval harness. Do not edit `skills/sprint-digest/` directly — edit
`labs/sprint-digest/`, run `labs/evals/run_evals.py`, and promote when it wins. See
[labs/README.md](labs/README.md) and `docs/adr/0003-*`.

Grader unit tests are free and must pass before any eval run:
`./labs/evals/.venv/bin/python -m pytest labs/evals/test_graders.py -q`

### Library increments

Evidence bar, eval ladder, and definition of done for improving a Library skill. See `docs/agents/library-increments.md`.

### Sprint digest

Narrative briefing of story-worthy increments from a Jira sprint (HTML + chat summary). Canonical: `skills/sprint-digest/`; runtime copy under `.cursor/skills/sprint-digest/`. Distinct from status reports, WIP dashboards, sprint packing, and context-gate triage — see the skill boundary table.
