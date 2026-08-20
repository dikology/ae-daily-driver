---
name: retrospective
description: Interactive post-session retrospective that captures learnings, updates skills, and saves memories. Use when the user says "/retrospective", "let's do a retro", "what did we learn", "session review", "retro", or "wrap up". Also use at the end of long productive Cursor sessions when significant patterns or corrections emerged. Supports multi-session mode — by default processes all of today's agent transcripts across projects.
---

# Retrospective

Interactive post-session retro. Scans Cursor agent transcripts, asks focused questions, proposes concrete actions the user approves in one step.

This is a **session** retro (skills, corrections, rules).

## Modes

### Single-session mode (default when inside a substantial conversation)
Scans the current conversation only.

### Multi-session mode (default when invoked with no args, or with "today", or with a date)
Scans all agent transcripts from a given day (default: today) across Cursor projects. Extracts user corrections, skill failures, and patterns.

**Trigger:** `/retrospective` at the start of a fresh session, or `/retrospective today`, or `/retrospective 2026-05-24`.

## Mode Selection Logic

When `/retrospective` is invoked:
1. If the current conversation has 10+ user messages → **single-session mode**
2. If the current conversation is short (just the `/retrospective` invocation) → **multi-session mode** (today)
3. If args contain a date (`today`, `yesterday`, `2026-05-24`) → **multi-session mode** for that date
4. If args contain `all` → **multi-session mode** for today

## Multi-Session Discovery

### Step 0 — Discover sessions

Run the scanner from this skill directory (completion: stdout lists every parent transcript for the date, or `Found 0 sessions`):

```bash
python3 scan_transcripts.py                  # today, all projects
python3 scan_transcripts.py --date 2026-05-24
python3 scan_transcripts.py --min-user-messages 3
```

The scanner reads `~/.cursor/projects/*/agent-transcripts/{uuid}/{uuid}.jsonl`, skips `subagents/`, and prints project, short id, query previews, tools, and skills touched.

Cite a past chat as `[short title](uuid)` using the folder uuid (no `.jsonl`).

Then continue to Step 1a with the combined findings. Each candidate action must note which session it came from (project name + short id).

## Single-Session Process

### Step 0 — Gate Check (silent)

Scan the conversation and estimate session depth. Look for tool calls (Read, StrReplace, Write, Shell, skill invocations), errors, and back-and-forth. Judge by feel:

- **Short session** (a quick question and answer, ~1-2 tasks) → **Fast mode** (Step 1b)
- **Substantial session** (multiple tasks, skill usage, errors, corrections) → **Full mode** (Step 1a)

### Step 1a — Full Mode

Silently scan the conversation (or scanner output) and collect:

1. **Skills invoked** — which succeeded, which failed, workarounds applied
2. **User corrections** — explicit "no, do it this way" moments (highest signal)
3. **Repeated patterns** — same error hit multiple times, same workaround applied
4. **Cross-skill workflows** — 3+ skills chained in sequence

Then read existing state:
- Memory: `{project}/.cursor/memory/MEMORY.md` plus any `feedback_*.md` / `project_*.md` there (skip if the directory does not exist)
- Skills invoked this session, in order: the path already known from the turn → `{project}/.cursor/skills/{name}/SKILL.md` → `~/.cursor/skills/{name}/SKILL.md` → `~/.agents/skills/{name}/SKILL.md`. Never edit `~/.cursor/skills-cursor/`
- Linear: configured when MCP server `user-Linear` (or another Linear server) is available. Discover the create-issue schema with GetMcpTools before calling it. If no Linear server → omit Linear task candidates

Generate up to **5 candidate actions**, ranked by signal strength:
1. User corrections (highest priority)
2. Failed/workarounded skills
3. Repeated patterns
4. Error patterns
5. Workflow patterns (lowest)

`retro_engine.py` ranks and dedups; you assign action types (skill vs AGENTS.md vs memory vs Linear).

**Dedup rules:**
- If a candidate's content overlaps with an existing memory file → drop it
- If a skill update candidate overlaps with existing skill file content → drop it
- If Linear is not configured → omit any Linear task candidates

Present everything in a **single AskQuestion call** (up to 4 questions):

| # | Question | Type |
|---|----------|------|
| 1 | "Quick session check?" | Single select: `Productive / Mixed / Rough / Skip retro` |
| 2 | "What felt slow or broken?" | Optional — user can pick Other |
| 3 | "Anything to carry forward as a rule?" | Optional — user can pick Other |
| 4 | "Which of these should I save?" | Multi-select (`allow_multiple: true`): generated candidates with descriptions. Always include a "Nothing / skip all" option. |

If Q1 = "Skip retro" → exit immediately.

If Q1 = "Rough" and Q2/Q3 are empty → exit with "Nothing to save — session closed."

### Step 1b — Fast Mode

Single AskQuestion call with one question:
- "Anything worth remembering from this session?" with options:
  - "Nothing, we're done" (default)
  - Other (free text)

If "Nothing" → exit. If free text → save as memory, exit.

### Step 2 — Execute (silent, no re-confirmation)

For each approved item from Q4 (plus any insights from Q2/Q3 free text):

1. **Read the target file** before writing
2. **Check for conflicts/duplicates** against current content
3. **Write the change** if clean
4. **Skip with warning** if conflict detected

Write into the **originating project** for that candidate (decoded path from the scanner), not whichever workspace happens to be open.

| Type | Target | Tool |
|------|--------|------|
| Skill update | `{project}/.cursor/skills/{name}/SKILL.md` (else `~/.cursor/skills/{name}/SKILL.md`) | StrReplace |
| Memory (feedback) | `{project}/.cursor/memory/feedback_*.md` + `MEMORY.md` | Write |
| Memory (project) | `{project}/.cursor/memory/project_*.md` + `MEMORY.md` | Write |
| AGENTS.md rule | `{project}/AGENTS.md` | StrReplace |
| Linear task | Linear MCP create-issue tool (schema from GetMcpTools) | CallMcpTool |

Create `.cursor/memory/` and a short `MEMORY.md` index on first memory write. Append one index line per new memory file.

### Step 3 — Summary (brief)

One-line per action taken:
```
Updated telegram skill — added chat type mismatch note
Saved memory — Qwen /api/chat not /api/generate
Skipped: pdf-generation update (already documented)
```

Done. No trailing commentary.

## Cursor Transcript Format

Parent transcripts: `~/.cursor/projects/{slug}/agent-transcripts/{uuid}/{uuid}.jsonl`

`{slug}` is the workspace path with `/` replaced by `-` and the leading `/` stripped (`/Users/me/src/foo` → `Users-me-src-foo`). The scanner resolves it back to a real directory when possible.

Each JSONL line is a JSON object. Relevant shapes:
- `role: user` — user message. Text in `message.content[]` where `type == "text"`. The actual prompt is inside `<user_query>...</user_query>` when present.
- `role: assistant` — model response. Text and `tool_use` blocks in `message.content[]`.
- `type: turn_ended` — skip.

Subagent transcripts live under `{uuid}/subagents/` — ignore them in discovery.

## Candidate Description Format

Each candidate in Q4 must have a description showing the **exact proposed content**, not just a title. The user judges candidates by reading descriptions, not by opening files.

Good: `"Add to telegram skill: get_chat_type() misclassifies private chats as channels — use Telethon client.send_message() directly for DMs"`

Bad: `"Update telegram skill with DM fix"`

## What This Skill Does NOT Do

This skill only captures session learnings. It does not review code quality, analyze PRs, create documentation, run tests, interview over journal dailies, or close a Jira ticket retro.

## Rules

- Never write learnings into this skill file itself — distribute to relevant skills or memory
- Cap candidates at 5 even if more findings exist
- User corrections always rank above tool failures
- The multi-select in Step 1a IS the approval — do not ask again per action
- If the session used no skills, only offer memory and AGENTS.md candidates
- Keep the entire interaction to 2 moments: one question call, then silent execution

## Testing

Engine + scanner tests:

```bash
cd .cursor/skills/retrospective && python3 -m pytest test_retro_engine.py test_scan_transcripts.py -v
```
