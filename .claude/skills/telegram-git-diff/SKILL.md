---
name: telegram-git-diff
description: >-
  Draft a Telegram post from a Git diff in the voice of the channel
  «Извини, что не писал» (@ididnotwrite). Use when the user asks to announce,
  summarize, or turn code changes into a Telegram post, or when they invoke
  /telegram-git-diff. Drafts only — never publish, send, or call Telegram APIs
  except for an explicit style refresh.
disable-model-invocation: true
---

# Telegram post from Git diff

Turn the repository's actual Git changes into a Telegram post that sounds like
the author of [@ididnotwrite](https://t.me/ididnotwrite), not like a changelog
and not like an LLM paraphraser.

Read [persona.md](persona.md) before writing. That file is the mouth. The diff
is the source of truth.

## Workflow

1. Identify the comparison scope in this order:
   - If the user provides a Git range, tag, commit, branch, PR base, or explicit command, use it.
   - If the user explicitly asks about staged work, run `git diff --cached`.
   - Otherwise run `git status --short` and `git diff`.
   - If the working-tree diff is empty, inspect the latest commit with `git show --stat --oneline HEAD` and `git show --format= --no-ext-diff HEAD`.
2. Inspect the diff and relevant surrounding code or documentation when needed to understand user-visible behavior. Treat code as the source of truth; do not infer features that are not evidenced by the diff.
3. Read `persona.md`. Identify language and register:
   - Language: use the user's request. If absent, Russian (channel default).
   - Register: **Update** unless the user asks for a letter, a milestone telling, or variants.
   - If the user names a work audience (analytics engineers, stakeholders), keep the same voice DNA and drop the letter costume — see persona.md.
4. Draft one post. Then silently run the humanizer pass in persona.md (embedded: no audit dump). If the draft could sit next to the anti-corpus quotes, rewrite it.
5. Return only the post in a fenced `text` block, unless the user requests variants or an explanation.

## Writing rules

- Lead with the concrete user-visible outcome, in prose, not in a headline + bullets.
- Mention technical implementation only when it matters to readers: migration, breaking change, downtime, performance, or a developer-facing capability.
- Do not claim release, deployment, availability, performance gains, security improvements, or bug resolution unless the diff or user explicitly confirms it.
- State limitations, migration steps, configuration requirements, or breaking changes clearly — plainly, not as a metaphor.
- Do not fabricate personal context (illness, dog, Anki, weather, mood). If it is not in the diff or the user's message, it does not go in the post.
- Never expose secrets, tokens, private URLs, internal hostnames, customer data, file paths, or raw stack traces found in the diff.
- Preserve uncertainty: if the diff makes intent unclear, say what changed narrowly rather than guessing why.
- No product-marketing filler: “excited to announce,” “game-changing,” “under the hood,” emoji headers, theme hashtags.

## Output format

Default is **Update**: 1–4 short paragraphs. No emoji headline. No bullet list unless the user asks for one.

```text
<what exists now that did not exist before>

<optional second beat, or a next step evidenced by the diff>

<optional honest limit — "пока так" if the work is unfinished>
```

## Optional variants

When requested, provide exactly the labeled versions asked for, otherwise these three:

- `Concise` — one or two sentences, ~300 characters or fewer. Match the short few-shots in persona.md.
- `Update` — the default above.
- `Letter` — optional `Извини, что давно не писал`, then the same facts as a letter to an imaginary friend. Still no invented life beats.
- `Technical` — same mouth, retain relevant API / configuration / migration detail in prose.

Each version must remain grounded in the same diff.

## Style refresh

Only when the user says `refresh style` / `update persona`: follow the Refresh
section in persona.md. Use telegram-mcp `list_messages` on `ididnotwrite`.
Do not fetch the channel on an ordinary git-diff run.

## Safety

This skill drafts content only. Never `send_message`. Do not `save_draft`
unless the user explicitly asks to park the text in Telegram.

## Example invocation

`/telegram-git-diff Draft a Russian Telegram post for the changes against origin/main.`

`/telegram-git-diff Letter register, Russian, for the App Store release commit.`

`/telegram-git-diff English, audience: analytics engineers, include migration notes if any.`
