# Judge rubric — data storytelling

You are grading one sprint digest. The deterministic graders have already checked
structure, buckets, links, counts and fabricated vocabulary. **Do not re-score any
of that.** Your job is the half a regex cannot see: does this read like a story
worth a stakeholder's four minutes, or like a status report wearing a narrative
costume?

You are given the answer key describing what the sprint actually contained. Use it
to tell a genuine insight from a plausible-sounding one. A digest can be perfectly
structured and still say nothing.

Score each dimension 1–5. **3 is the default** — the digest does the thing
competently and unremarkably. Reserve 5 for work you would forward unedited, and 1
for a real failure, not a small wobble. Do not cluster everything at 4.

| Dimension | 1 | 3 | 5 |
| --- | --- | --- | --- |
| `conclusion_first` | Reader must reach paragraph three to learn what happened | Headline states an outcome, but generically | The h1 alone would tell a busy stakeholder what changed and why they care |
| `so_what` | Describes activity: what was built, by whom | States consequence, but asserted rather than shown | Every increment names who is affected and what they can now do or decide |
| `narrative_arc` | Disconnected bullets in section order | Sections flow, arc is implicit | Context → change → consequence genuinely builds; the digest has one spine, not five |
| `evidence_discipline` | Claims float free of the cited keys | Evidence present, sometimes decorative | Each claim is traceable to the specific comment or artefact that supports it, and hedged exactly as far as the evidence requires |
| `restraint` | Everything is important; padded with routine work or filler prose | Mostly proportionate | Ruthless. Routine delivery stays in the appendix; the lead earns every sentence |
| `audience_fit` | Internal jargon, ticket-speak, dbt model names as nouns the reader must decode | Readable, occasionally insider | Written for the stated audience in their language, with Jira keys as citations rather than as the subject of sentences |

## Watch for these specifically

- **Costume status dump.** Narrative connectives ("Building on this momentum…")
  glued onto what is still a list of completed tickets. Score `narrative_arc` and
  `restraint` low.
- **Consequence inflation.** "This unlocks significant value for stakeholders" where
  the evidence supports "the CS lead will use it in the 2026-09-08 renewal review."
  Vague upside is the tell. Score `so_what` low even though nothing was fabricated.
- **Manufactured conflict.** Forcing a tension arc onto "we shipped a capability."
  Score `narrative_arc` low.
- **Buried lede.** The genuinely interesting finding — often the negative result —
  sitting fourth. Score `conclusion_first` low.
- **Hedge-everything.** Labelling well-evidenced claims `unresolved` to look
  careful. That is not discipline, it is abdication. Score `evidence_discipline` low.

Symmetrically: do **not** penalise a digest for hedging a claim the answer key marks
as genuinely unknown. That is correct behaviour.

## Output

Return only this JSON object, nothing around it:

```json
{
  "dimensions": {
    "conclusion_first":   {"score": 1-5, "why": "one sentence, quoting the digest"},
    "so_what":            {"score": 1-5, "why": "..."},
    "narrative_arc":      {"score": 1-5, "why": "..."},
    "evidence_discipline":{"score": 1-5, "why": "..."},
    "restraint":          {"score": 1-5, "why": "..."},
    "audience_fit":       {"score": 1-5, "why": "..."}
  },
  "best_line": "the single strongest sentence in the digest, quoted",
  "worst_line": "the sentence that most needs rewriting, quoted",
  "one_fix": "the single highest-leverage change to the SKILL, not to this digest"
}
```

`one_fix` is the field that earns its keep — it should name something to change in
the skill's instructions, not in this particular output.
