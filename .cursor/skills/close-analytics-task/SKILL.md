---
name: close-analytics-task
description: Write the tracker closing comment for a finished bi, etl, adhoc, infra, or data-quality ticket and update the sprint's Obsidian note with the outcome. Use immediately after /implement or /research finishes a ticket, before moving to the next one.
---

# Close Analytics Task

A good closing comment lets a reviewer or future-you understand what happened without
re-reading the diff or thread. This skill drafts that comment and keeps the sprint's
Obsidian note in sync, so sprint status is always visible without re-deriving it from
the tracker.

## Step 1 — Gather what actually happened

- For code tickets: the diff since the ticket started (what `/code-review` reviewed),
  and its verdict.
- For adhoc/research tickets: the findings produced by `/research`, and where they were
  saved.
- Any acceptance criteria from the original ticket (drafted by `/triage-analytics-task`)
  — check them off explicitly, one by one. If any criterion was not met, say so — do not
  omit it.

## Step 2 — Draft the closing comment

Match the shape to the ticket type:

**bi / etl / infra / data-quality:**
```
Done. <one-line summary of what changed and why>

Acceptance criteria:
- [x]/[ ] <criterion> — <note if partial or not met>

Changed: <files/models/dashboards touched, at a glance>
Validated: <how — tests, query diff, manual check, stakeholder confirmation>
Follow-ups: <anything deliberately deferred, filed as a new ticket if non-trivial>
```

**adhoc:**
```
Answer: <the actual finding, up front>

Method: <how it was derived — query, notebook, source>
Caveats: <sampling, time range, known limitations>
Findings doc: <link to the /research output file, if one was produced>
```

Post this to the tracker ticket. Keep it factual and specific — no filler like "made
some changes" or "looked into it."

## Step 3 — Update the sprint note

In the Obsidian sprint note created by `/plan-analytics-sprint`, find this ticket's line
and:
- Check its box.
- Append a short outcome, e.g. `— shipped, +18% query speed` or `— answered: churn is
  concentrated in cohort X`.
- If a follow-up ticket was filed, add it as a new unchecked line under the same repo.

## Boundaries

- Does not re-review the work — trust `/code-review`'s verdict, or the `/research`
  output, as the source of truth for what happened.
- If acceptance criteria can't be verified as met, flag that in the comment rather than
  closing the ticket as fully done.
