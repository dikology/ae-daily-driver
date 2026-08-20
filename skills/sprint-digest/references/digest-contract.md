# Digest contract

Default deliverables: **single-file HTML** + **3–5 bullet chat summary**.

## File naming

```
analyses/YYYY-MM-DD_<sprint-slug>-digest.html
```

Examples:

- `analyses/2026-08-20_hospa-26-08-21-digest.html`
- Sprint slug: lowercase, hyphens; prefer sprint name from Jira.

Optional markdown twin (only if asked): `sprint_<id>/DIGEST.md`.

## Chat summary

Exactly 3–5 bullets:

1. Sprint headline (conclusion sentence)
2. Top 1–2 increments (keys + one line each)
3. One watch/decision ask if any
4. Path to the HTML file

No full ticket dump in chat.

## HTML document structure

Single column. No site chrome, no dashboard widget kit.

```
header
  title (conclusion) + meta (board, sprint, window, n, generated-at)

section.headline
  1–2 paragraph narrative arc (context → what changed → so what)

section.increments  (3–5 max)
  article.increment
    h2 conclusion title
    .claim-meta  (observed | synthesis | unresolved)
    .what-changed
    .evidence  (keys as browse links, URLs, artifact paths)
    .why-it-matters
    optional: one chart + table of same numbers

section.watch
  decisions / risks needing a human (key, reason, evidence, ask)

section.appendix
  methodology (how issues were fetched)
  coverage counts (scope / done / in progress / need info — must reconcile)
  omissions table (key → bucket omit → one-line reason)
  source links (board id, sprint id, field coverage)
```

### Title rules

- Page `h1` and each increment `h2` are **conclusions**, not “Sprint digest” or
  “Chart 1”.
- Russian body by default for HOSPA stakeholder briefings; keep Jira keys and
  status names verbatim.

### Charts

Optional. Only when they support a claim already stated in prose.

- One claim per visual
- Table of the same numbers beside the chart
- Do not invent series; omit chart if field missing (e.g. story points)

### Counts

Appendix counts must reconcile with the sprint issue set used for Pass 1.
Never claim capacity or burndown without fetched fields.

### Trust labels

Every increment block shows claim strength. Unresolved claims stay visible —
do not silently drop them from the lead without moving them to **watch** or
**omit** with a reason in the appendix.

## Visual system

In `tasks`: follow root `DESIGN.md` / `PRODUCT.md` (Plasma-adapted editorial
report). After write: impeccable `audit` → `distill` / `typeset` / `layout` /
`polish`. No `bolder` / `delight` / `overdrive` / `colorize`.

## Reads vs writes

- Default: Jira MCP read-only.
- Do not post digest content to Jira unless the user names an issue and confirms.
