# Context audit — ae-daily-driver

| | |
|---|---|
| Commit | `5d8cbc7` (clean tree at audit time) |
| Validator | `skills/reviewing-agent-context/scripts/audit_context.py` — exit 1, 8 errors, 22 warnings |
| `context-engineering` skill | Not installed in this repo. Read from a local clone of `addyosmani/agent-skills`; the audit therefore cites it, but `--locate-context-engineering` reports NOT FOUND until it is installed. |
| Always-tier budget | **~1,079 tokens today → ~1,079 proposed** (see §7 — the wins here are correctness and task-tier cost, not always-tier bytes) |

Headline: the always-tier budget is small and healthy. The damage is elsewhere — **eight
unresolvable links to the one document five skills depend on**, and a documented layout
policy that four of nine skills violate.

---

## 1 — Context inventory

Agent-loaded artifacts, by cost. Full table in the validator output.

| Path | Kind | Lines | Est. tokens | Owner surface |
|---|---|---:|---:|---|
| `skills/dataviz/SKILL.md` | skill | 363 | 6,919 | all |
| `skills/triage-analytics/SKILL.md` | skill | 199 | 2,351 | all |
| `.cursor/skills/telegram-git-diff/persona.md` | reference | 184 | 2,144 | Cursor |
| `skills/retrospective/SKILL.md` | skill | 180 | 2,112 | all |
| `skills/sprint-digest/SKILL.md` | skill | 169 | 1,605 | all |
| `skills/do-jira-task/SKILL.md` | skill | 106 | 1,181 | all |
| `.cursor/skills/telegram-git-diff/SKILL.md` | skill | 88 | 1,148 | Cursor |
| `docs/agents/context-gate.md` | doc | 130 | 1,144 | all (via 5 skills) |
| `.cursor/skills/plan-analytics-sprint/SKILL.md` | skill | 85 | 832 | Cursor |
| `skills/sprint-digest/references/digest-contract.md` | reference | 95 | 656 | all |
| `.cursor/skills/close-analytics-task/SKILL.md` | skill | 66 | 616 | Cursor |
| `skills/sprint-digest/references/increment-rubric.md` | reference | 58 | 608 | all |
| `skills/do-jira-task/task-quality.md` | reference | 75 | 576 | all |
| `docs/agents/domain.md` | doc | 52 | 484 | all |
| `docs/agents/issue-tracker.md` | doc | 31 | 452 | all |
| `.cursor/rules/excalidraw.mdc` | scoped rule | 35 | 451 | Cursor |
| `skills/do-jira-task/plan-template.md` | reference | 72 | 317 | all |
| `docs/agents/triage-labels.md` | doc | 16 | 261 | all |
| `AGENTS.md` | instruction file | 26 | 248 | all |
| `docs/adr/0001…`, `docs/adr/0002…` | doc | 4, 4 | 104, 97 | all |
| `skills/retrospective/*.py` (4 files) | script | 988 | 7,713 | on-exec |
| `skills/retrospective/scenarios/*.yaml` (9) | skill test data | 319 | 2,071 | on-exec |
| `skills/reviewing-agent-context/**` | skill + refs + scripts | 969 | 10,082 | all / on-exec |
| `CONTEXT.md` | doc | 81 | 1,289 | all (see §2 correction) |
| `README.md` | doc | 65 | 742 | **humans only** |
| `diagrams/scheme.excalidraw` | generated artifact | 1,034 | 6,428 | on-request only |

MCPs/tools: **none wired.** `CONTEXT.md`, `README.md` and ADR-0002 all describe an `mcp/`
directory as the home for MCP config examples. It does not exist. No MCP server is
configured anywhere in the repo, so the "query" tier of the load map is empty.

## 2 — Load map

| Tier | Trigger | Files | Est. tokens |
|---|---|---:|---:|
| Always | Every request | 1 file + 9 frontmatter descriptions | **1,079** |
| Task | Skill invoked or description matched | 23 | 28,793 |
| Path | A matching file is touched | 1 (`.cursor/rules/excalidraw.mdc`, `**/*.excalidraw`) | 451 |
| Query | Agent asks a tool | 0 | 0 |
| On-exec | A script reads it | 15 | 18,132 |

Always-tier composition: `AGENTS.md` 248 tokens + nine skill descriptions totalling 831.
Descriptions are the larger half; they ship in the system prompt whether or not any skill
body is ever read.

**Corrections to the validator's tiering, with evidence:**

1. `CONTEXT.md` (1,289 tokens) is classified `none`. It is in fact **task-tier**, reached by
   the chain `AGENTS.md → docs/agents/domain.md → CONTEXT.md`. Evidence: `docs/agents/domain.md:7`
   instructs "Before exploring, read these — `CONTEXT.md` at the repo root". That is a
   two-hop chain from an always-tier file, which is the R4.2 failure shape applied to
   instruction files: an agent previewing `domain.md` may never reach the glossary.
2. `README.md` (742 tokens) is correctly outside every agent tier and should stay there —
   it is the human-facing pitch. It is not counted in any budget below.
3. `diagrams/scheme.excalidraw` (6,428 tokens) is agent-readable via the `.excalidraw`
   scoped rule but is never referenced from a skill. It loads only if a human names it.

**Nothing loads:** `.gitignore`, `.env`, `diagrams/empty.excalidraw` (48 tokens, no
elements). `.scratch/` and `confidential/` are empty directories.

## 3 — Duplicate and conflicting guidance

| # | Topic | Locations | Type | Which wins today | Resolution |
|---|---|---|---|---|---|
| 3.1 | Where canonical skills live | `docs/adr/0002`, `CONTEXT.md:80`, `README.md:30` say root `skills/` is canonical and `.cursor/` holds copies — but `close-analytics-task`, `plan-analytics-sprint` and `telegram-git-diff` exist **only** under `.cursor/skills/` | **conflict** | Reality wins; the policy is aspirational | Either promote the three to root `skills/` or amend ADR-0002 to admit Cursor-only skills. Do not leave both stories in the repo. |
| 3.2 | Gate outcome vocabulary | `docs/agents/context-gate.md:11` and `skills/triage-analytics/SKILL.md` share a 12-word passage on the *thin* verdict (validator R8.2) | paraphrase | Ambiguous | `context-gate.md:5` already says "Do not duplicate this list inside either skill." Enforce it: cut the restatement from `triage-analytics` and link. |
| 3.3 | Skill install location | `skills/retrospective/SKILL.md:178` tells the agent to `cd .cursor/skills/retrospective`; the skill is at `skills/retrospective/`. The eight broken `../../../` links (§5.1) encode the same wrong assumption. | **conflict** | Neither — both paths fail | Same root cause as 3.1. Fix once the canonical location is decided. |

Not counted as duplication: `sprint-digest/SKILL.md` and its two reference files, or
`do-jira-task/SKILL.md` and `task-quality.md`. That is progressive disclosure working.

## 4 — Missing context

No agent transcripts were available for this audit, so demonstrated re-discovery could be
established for only one item. The rest are in Unverified.

| Fact re-discovered | Evidence | Cost per occurrence | Destination rung |
|---|---|---|---|
| Where `context-gate.md` actually lives | Eight links across four files resolve outside the repo (validator R4.3). Any agent following one gets a miss and must search. The same wrong depth appears independently in five files, which means it was re-derived rather than copied once. | 1 failed read + 1–2 searches ≈ 500–1,500 tokens, on the highest-traffic shared doc in the repo | Fix in place (skill), then a **CI check** — the validator already detects it |

## 5 — Stale material and unsupported claims

| # | Claim | Location | Reality | Action |
|---|---|---|---|---|
| 5.1 | `../../../docs/agents/context-gate.md` | `do-jira-task/SKILL.md:16,50,100`, `do-jira-task/task-quality.md:3,9`, `sprint-digest/SKILL.md:25`, `triage-analytics/SKILL.md:15,130` | Resolves above the repo root. Correct depth from `skills/<name>/` is `../../` | **Fix** — 8 edits |
| 5.2 | "runtime copy under `.cursor/skills/sprint-digest/`" | `AGENTS.md:25` | No such directory | **Delete** the clause |
| 5.3 | "Useful skills already installed under `.cursor/skills/`: `grill-with-docs`, `domain-modeling`, `wayfinder`, `to-tickets`, `writing-for-agents`" | `README.md:55` | None of the five exist | **Delete**. Human-facing, so no agent cost — but it is why 5.4 and 5.5 were written |
| 5.4 | "Wayfinding operations — Used by `/wayfinder`" (8 of 31 lines) | `docs/agents/issue-tracker.md:22-31` | `/wayfinder` is not installed | **Delete** the section (~150 agent-loaded tokens) |
| 5.5 | "`/domain-modeling` (reached via `/grill-with-docs` and `/improve-codebase-architecture`) creates them lazily" | `docs/agents/domain.md:11` | None of the three skills exist here | **Fix** — drop the skill names, keep the "proceed silently" rule |
| 5.6 | Root `mcp/` holds MCP config examples | `CONTEXT.md:3,80`, `README.md:21,30`, `docs/adr/0002:1` | Directory does not exist | **Fix** — state it as planned in one place (README's Status list already does), remove from the other three |
| 5.7 | Label mapping table, both columns identical | `docs/agents/triage-labels.md` (261 tokens) | Carries zero information as written, and `triage-analytics` uses Jira components, not these labels | **Fix or delete** — see §7 |
| 5.8 | `analyses/2026-08-20_sprint-26-08-21-digest.html` as an example output path | `sprint-digest/references/digest-contract.md:13` | Dated filename in an instruction file (R8.1 in spirit) | **Fix** — use a shaped placeholder |

Path claims that correctly refer to a **consuming** repo, not this one, and are *not*
findings: `.cursor/WORKSPACE.md`, `.cursor/memory/`, `analyses/`, `.out-of-scope/`,
`subagents/`. The validator flags these at warn level for exactly this reason.

## 6 — Context-cost hotspots

Load frequency below is estimated from each skill's trigger breadth, not measured — see
Unverified.

| # | Artifact | Est. tokens | Load frequency | Weighted | What the tokens buy |
|---|---|---:|---|---:|---|
| 6.1 | `skills/dataviz/SKILL.md` | 6,919 | med — 2 modes, 5 output formats | high | Sections A/C/D/E are the analytics work. **Section B (motion & interaction, lines 87–261) is 4,004 tokens — 57% of the skill** — and applies only to the canvas output format (§E, `Section E`, line 343). Every chart review pays for it. |
| 6.2 | Nine frontmatter descriptions | 831, always | 100% | high | Correct spend, but `telegram-git-diff`, `close-analytics-task` and `plan-analytics-sprint` are Cursor-only and carry `disable-model-invocation` or no trigger clause — they pay always-tier rent for routing that cannot fire |
| 6.3 | `.cursor/skills/telegram-git-diff/persona.md` | 2,144 | low | low | A voice guide for one Telegram channel. Correctly a reference, correctly one level deep. Fine where it is; it needs a TOC (R4.4). |
| 6.4 | `docs/agents/context-gate.md` | 1,144 | high — 5 skills | high | The most-shared doc in the repo, and the one with eight broken links to it. Highest-value fix per token. |
| 6.5 | `diagrams/scheme.excalidraw` | 6,428 | ~0 | ~0 | Not a hotspot. Listed because raw size invites a wrong cut — nothing loads it. |

## 7 — Recommended relocation

Ranked by weighted cost, then by conflicts resolved.

| # | Content | From | To (rung + path) | Why | Token delta |
|---|---|---|---|---|---|
| 7.1 | 8 links to `context-gate.md` | `../../../` | Same rung (skill), path `../../docs/agents/context-gate.md` | Rung is right, path is wrong. Fixes §4 and §5.1 | 0 loaded; −500–1,500 per wasted lookup |
| 7.2 | Link-depth and path-resolution enforcement | nowhere | **CI check** — `python3 skills/reviewing-agent-context/scripts/audit_context.py . --fail-on error` | Passes the rung test: a script decides pass/fail. Prevents 7.1 recurring | 0 |
| 7.3 | dataviz Section B (motion & interaction) | `skills/dataviz/SKILL.md` body | **Reference** — `skills/dataviz/references/motion.md`, linked once from SKILL.md | R3.3: it is conditional detail for one output format. One level deep, so R4.2 holds | −4,004 on every dataviz load that is not canvas work |
| 7.4 | Canonical-location decision | contradictory across ADR-0002 / CONTEXT.md / AGENTS.md / README | **Root instruction** — one sentence in `AGENTS.md`, ADR-0002 amended to match | Passes the root-instruction test: an agent that gets this wrong writes files in the wrong place. Resolves §3.1 and §3.3 | +~20 always |
| 7.5 | Thin-verdict restatement | `triage-analytics/SKILL.md` | **Reference** — delete, keep the existing link to `context-gate.md` | `context-gate.md:5` already forbids the duplicate | −60 |
| 7.6 | `/wayfinder` section | `docs/agents/issue-tracker.md:22-31` | Delete | Documents a skill that is not installed | −150 |
| 7.7 | `triage-labels.md` | `docs/agents/` | **Delete**, or fold the four surviving rows into `context-gate.md` | Fails every rung test as written: identical columns, wrong vocabulary for a Jira-component workflow | −261 |
| 7.8 | `mcp/` claims | `CONTEXT.md`, ADR-0002 | Keep only the README Status entry | A planned directory is not a layout fact | −40 |
| 7.9 | `CONTEXT.md` entry point | reached only via `docs/agents/domain.md` | **Root instruction** — link `CONTEXT.md` directly from `AGENTS.md` | Removes a two-hop chain from the always tier (§2 correction 1) | +~15 always |

Net: always tier +35 tokens (1,079 → ~1,114), task tier −4,515, and eight broken links plus
two policy conflicts resolved. **No new instruction file is proposed** — 7.4 and 7.9 add two
lines to the file that already exists.

Deliberately not recommended: cutting `persona.md`, `scheme.excalidraw`, or the retrospective
test fixtures. None are loaded on a path where they cost anything.

## 8 — Evaluation suite

Three cases, each targeting a specific finding. **All baselines below are structural — they
are measured by the validator on the pre-change tree and need no model run.** The behavioral
column is stated but not yet run; see Unverified.

| Metric | Before (measured, `5d8cbc7`) | After (target) |
|---|---:|---:|
| Validator errors | 8 | 0 |
| Validator warnings | 22 | ≤ 14 |
| Always-tier tokens | 1,079 | ~1,114 |
| Task-tier tokens | 28,793 | ~24,278 |
| Unresolvable links | 8 | 0 |

```json
[
  {
    "id": 1,
    "targets": "§4 / §5.1 — eight unresolvable links to context-gate.md",
    "skills": ["do-jira-task"],
    "prompt": "Score PROJ-123 against the context gate before executing it.",
    "expected_behavior": [
      "Reads docs/agents/context-gate.md successfully on the first attempt",
      "Scores against the component section, not an invented checklist"
    ],
    "baseline": "Pre-change: the link in do-jira-task/SKILL.md:50 resolves outside the repo; a first read attempt fails. Structural baseline: 8 R4.3 errors.",
    "result": null
  },
  {
    "id": 2,
    "targets": "§6.1 / §7.3 — dataviz Section B loaded on non-canvas work",
    "skills": ["dataviz"],
    "prompt": "Review this bar chart's encoding and tell me what's wrong with it.",
    "expected_behavior": [
      "Applies Section A grammar rules and the Review-mode flow",
      "Does not read the motion and interaction material for a static review"
    ],
    "baseline": "Pre-change: 6,919 tokens loaded, of which 4,004 (57%) are motion rules irrelevant to the request. Post-change target: 2,915 tokens for the same request.",
    "result": null
  },
  {
    "id": 3,
    "targets": "§3.1 / §3.3 — contradictory canonical-location policy",
    "skills": [],
    "prompt": "Add a new skill called sprint-health to this repo.",
    "expected_behavior": [
      "Creates it at the canonical location without asking which of the two the repo means",
      "Does not create a second copy under .cursor/skills/ unless the amended policy calls for one"
    ],
    "baseline": "Pre-change: ADR-0002 and CONTEXT.md say root skills/ is canonical; three of nine skills live only under .cursor/skills/. Structural baseline: 2 conflicting statements, 0 authoritative.",
    "result": null
  }
]
```

Procedure: record baselines on `5d8cbc7` (done — the numbers above), apply §7, re-run
`audit_context.py` and the three cases, then report each as improved / unchanged /
regressed.

**Validator calibration.** Run against `addyosmani/agent-skills` (25 skills, its own CI
enforcing link and frontmatter rules), the same validator reports **0 errors, 57 warnings**.
Against this repo it reports **8 errors, 22 warnings**. The error classes it flags here are
absent from a repo that already enforces them, which is evidence the checks are calibrated
rather than fitted to this codebase.

Honest note on case 3: it has no structural assertion that a script can decide. Its
baseline is a documented contradiction, and its result will be a judgment call about
whether an agent hesitated. It is the weakest of the three and should be treated as
supporting evidence, not proof.

## Unverified

- **Load frequencies in §6 are estimates**, derived from reading each skill's trigger
  breadth. No routing telemetry or transcript sample was available. Every "weighted cost"
  ranking inherits that uncertainty. The §6.1 dataviz finding does not: its 57% figure is
  measured, and only the frequency term is estimated.
- **Missing context (§4) is nearly empty by design.** Without transcripts, "facts agents
  re-discover" cannot be evidenced. Candidates that were considered and rejected for lack
  of evidence: no `CLAUDE.md` exists (only `AGENTS.md`) — plausible cost, unmeasured;
  no skill states which Jira instance or MCP the tracker skills expect — plausible, but no
  observed instance of an agent asking.
- **The behavioral half of §8 has not been run.** Only the structural baselines are
  measured. Cases 1–3 are specified and ready; running them requires a model invocation
  that this audit did not perform.
- **The `context-engineering` skill is not installed here.** It was read from a local
  clone, so its anti-patterns are cited accurately, but `--locate-context-engineering`
  will report NOT FOUND until it is installed.
- **`skills/reviewing-agent-context/` audits itself** in these numbers (10,082 tokens
  on-exec plus 1,307 task). Its own findings were not exempted, but a reader should know
  the auditor is inside the sample.
- **Whether the three Cursor-only skills should be promoted or the ADR amended** is a
  product decision, not an audit finding. §7.4 requires the contradiction to be resolved;
  it does not pick a side.
