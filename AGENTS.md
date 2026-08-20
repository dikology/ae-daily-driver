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

### Sprint digest

Narrative briefing of story-worthy increments from a Jira sprint (HTML + chat summary). Canonical: `skills/sprint-digest/`; runtime copy under `.cursor/skills/sprint-digest/`. Distinct from status reports, WIP dashboards, sprint packing, and context-gate triage — see the skill boundary table.
