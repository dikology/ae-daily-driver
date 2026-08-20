# Increment rubric (story-worthiness)

Score each **clustered increment**, not each raw Jira ticket. Distinct from
`docs/agents/context-gate.md` (implementation readiness).

## Required fields

An increment is story-worthy only when all four are established (or marked
**unresolved** after Pass 2 grill):

| # | Field | Meaning |
|---|--------|---------|
| S1 | **Outcome / capability** | What became true, shippable, or learnable — not the ticket title alone |
| S2 | **Evidence** | Jira comment, MR, dashboard URL, query result, local `hospa_*` artifact, changelog — named and linkable |
| S3 | **Audience** | Who cares (stakeholder role, product area, team) |
| S4 | **Consequence / next decision** | Why it matters now, or what decision it unlocks / blocks |

Fail closed: if S1–S4 cannot be filled without invention, **omit** or keep as
**watch** with `unresolved` labels — do not promote to headline.

## Evidence strength

| Level | Criteria |
| --- | --- |
| **strong** | External artifact or reproducible number + clear audience consequence |
| **medium** | Ticket body/comments agree on outcome; consequence inferred with labeled **synthesis** |
| **weak** | Summary-only or status change with no “so what” |

Prefer **strong** for headlines. **Weak** never leads the digest.

## Buckets

| Bucket | When |
| --- | --- |
| **headline** | Strong (or medium after grill) S1–S4; material for this audience |
| **supporting** | Enables or deepens a headline; or solid on its own but secondary |
| **watch** | High value but blocked / Need Info / decision pending; or strong risk |
| **omit** | Hygiene, renames, routine ETL without consumer impact, duplicate work, cancelled noise |

Multiple tickets may form **one** increment when they share one outcome (e.g. ETL
+ BI for the same dashboard). Name the cluster; list all keys under Evidence.

## Claim labels

Use in drafts and in the HTML:

- **observed** — directly supported by fetched evidence
- **synthesis** — editorial compression of observed facts (still no invented numbers)
- **unresolved** — audience or consequence still open after grill (or grill declined)

## Anti-patterns

- Equating Done count with impact
- Using context-gate **pass** as proof of story-worthiness
- One chart per ticket “because we have data”
- Inventing “$ saved” / “% uplift” without a fetched source
- Forced narrative conflict when the increment is “capability shipped”
