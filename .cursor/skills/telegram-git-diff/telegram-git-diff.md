---
name: telegram-git-diff
description: Create a concise Telegram release/update post from the current Git diff, a specified Git diff range, or staged changes. Use when the user asks to announce, summarize, or turn code changes into a Telegram post.
disable-model-invocation: true
---

# Telegram post from Git diff

Turn the repository's actual Git changes into an accurate, reader-friendly Telegram post. This skill drafts content only: never publish, send, or call Telegram APIs.

## Workflow

1. Identify the comparison scope in this order:
   - If the user provides a Git range, tag, commit, branch, PR base, or explicit command, use it.
   - If the user explicitly asks about staged work, run `git diff --cached`.
   - Otherwise run `git status --short` and `git diff`.
   - If the working-tree diff is empty, inspect the latest commit with `git show --stat --oneline HEAD` and `git show --format= --no-ext-diff HEAD`.
2. Inspect the diff and relevant surrounding code or documentation when needed to understand user-visible behavior. Treat code as the source of truth; do not infer features that are not evidenced by the diff.
3. Identify the audience and language from the request. If absent, write in the repository's primary documentation language. If that is unclear, ask which language and audience to use before drafting.
4. Produce one ready-to-paste Telegram post using the format below.

## Writing rules

- Lead with the concrete user or business outcome, not implementation details.
- Use a short headline with one relevant emoji, followed by 2–5 compact bullets.
- Mention technical implementation only when it matters to readers, such as a migration, breaking change, downtime, performance impact, or developer-facing capability.
- Do not claim release, deployment, availability, performance gains, security improvements, or bug resolution unless the diff or user explicitly confirms it.
- State limitations, migration steps, configuration requirements, or breaking changes clearly.
- Avoid generic filler such as “excited to announce,” “game-changing,” and “under the hood.”
- Use at most 2 emojis total and at most 3 hashtags. Do not include hashtags unless the user asks for them or the project convention clearly uses them.
- Never expose secrets, tokens, private URLs, internal hostnames, customer data, file paths, or raw stack traces found in the diff.
- Preserve uncertainty: if the diff makes intent unclear, say what changed narrowly rather than guessing why.

## Output format

Return only the post in a fenced `text` block, unless the user requests variants or an explanation.

```text
<emoji> <specific headline>

• <user-visible change or outcome>
• <second important change>
• <action needed, limitation, or availability detail when supported>

<short CTA or next step only if supported>
```

## Optional variants

When requested, provide exactly three labeled versions:

- `Concise` — 300 characters or fewer.
- `Standard` — the default format above.
- `Technical` — retain relevant API/configuration/migration detail.

Each version must remain grounded in the same diff.

## Example invocation

`/telegram-git-diff Draft a Russian Telegram post for the changes against origin/main. Audience: analytics engineers. Tone: practical; include migration notes if any.`
