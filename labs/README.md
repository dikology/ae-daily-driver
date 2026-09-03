# labs/ — where skills get iterated on

`skills/` is the showcase surface. Everything there is meant to be copied into a
consuming repo and used as-is, so it should not churn under people who depend on it.

`labs/` is the opposite: a working copy of one skill plus the evidence that a change
to it is an improvement rather than a rewrite.

```
skills/sprint-digest/     STABLE   — what other repos copy. Changes only via promotion.
labs/sprint-digest/       CANDIDATE — edit freely; nobody consumes this directly.
labs/evals/               the harness that decides whether candidate beats stable.
```

## Why an eval harness at all

`sprint-digest` produces prose. Prose degrades in ways a diff cannot show you: a
prompt edit that sharpens the headline can quietly teach the model to fabricate an
impact number, or to split a three-ticket outcome back into three rows. You cannot
see that by reading the SKILL.md diff, and you cannot see it from one good-looking
run either — the failure is probabilistic.

So the loop is: change the candidate, run both arms on the same fixtures, and look
at the delta. A change that does not move the number is not an improvement, it is a
preference.

## The Jira problem, and the fixtures

`labs/evals/mock_jira_mcp.py` is a stdio MCP server exposing the four tools the
skill actually calls (`jira_get_agile_boards`, `jira_get_sprints_from_board`,
`jira_get_sprint_issues`, `jira_get_issue`) over fixture JSON. The skill runs
**completely unmodified** — its step 2 executes verbatim — so anything the evals
prove here transfers to the consuming repo.

The shim is deliberately faithful about the awkward parts:

- `jira_get_sprint_issues` caps a page at 50 and withholds comments and changelog,
  so the skill has to paginate and has to fetch detail per candidate.
- Every call is appended to a JSONL trace, which lets graders score *how the
  evidence was gathered*, not just the HTML that came out.

### One real sprint, not committed

The fixture is a real sprint export — `HOSPA 26-09-04`, 83 issues, Russian. It and
its answer key are **built from `confidential/` and gitignored** (client data). If
`labs/evals/fixtures/` is empty on your machine, regenerate:

```bash
python3 confidential/build_hospa_fixture.py
```

That script reads two hand-maintained files and writes two generated ones:

| Source (`confidential/`, kept by hand) | Output (`labs/evals/fixtures/`, generated) |
| --- | --- |
| `hospa-26-09-04-sprint.json` — raw export, flat issues, no comments | `sprints/hospa-26-09-04.json` — Jira-shaped, with synthesised comments on the story keys |
| `hospa-26-09-04-eval-clusters.json` — which cluster is headline / watch / omit | `keys/hospa-26-09-04.json` — the grader answer key |

The export carries no comments, so the build script injects a short synthesised
comment onto each story-bearing key, drawn from that issue's own description and the
threads it links. That is the one place the fixture is not verbatim.

### The traps planted in this sprint

| Planted | Correct handling | Failure it catches |
| --- | --- | --- |
| HOSPA-1634 + 1635 + 1636 (backfill + Airflow + Metabase) | **one** headline increment | One row per Jira key instead of one row per outcome |
| HOSPA-1454, titled "Посчитать результаты" | headline or supporting | A generic title hiding a shipped product decision |
| HOSPA-1609, "обновление методики" | headline or supporting | Skipping a change to a base metric because it reads as chore |
| HOSPA-1744, DAG failure, still In Progress | watch, with the ask named | Burying a live incident that needs a human |
| HOSPA-1666 + 1667 + 1699 + 1700 | **one** watch entry | Reporting a blocked multi-stage pipeline as a clean win, or as four rows |
| HOSPA-1725, Need Info on OpenMetadata | watch | Listing a blocked item among completed work |
| HOSPA-1747 + 1714 + 1685 + 1562 | appendix | Reading Done-count as impact |
| No story-points / capacity / money field anywhere | no velocity/burndown/₽ | Fabricating the metric the reader expects |

That last one is why a controlled fixture beats live Jira: because we know what
fields exist, we can prove a number was invented rather than merely unsourced.

## Running it

One-time:

```bash
python3 -m venv labs/evals/.venv && labs/evals/.venv/bin/pip install pytest
```

Grader unit tests — free, instant, run these before every eval run:

```bash
./labs/evals/.venv/bin/python -m pytest labs/evals/test_graders.py -q
```

The evals themselves (each run spawns a real `claude -p` session, so they cost money
and take a few minutes):

```bash
python3 labs/evals/run_evals.py                            # both arms, 3 cases, 2 runs
python3 labs/evals/run_evals.py --arm candidate --runs 1   # fast iteration
python3 labs/evals/run_evals.py --case core-digest --no-judge --keep-temp
python3 labs/evals/run_evals.py --tag fail-closed
```

A full default run spawns 6 agent sessions plus judge calls and can cost
**$10–15**. For incremental editing use the cheap loop:

```bash
./labs/evals/.venv/bin/python -m pytest labs/evals/test_graders.py -q          # free
python3 labs/evals/run_evals.py --arm candidate --runs 1 --no-judge \
        --case core-digest --keep-temp                                          # ~$0.30–0.60
```

`--keep-temp` copies each produced digest into `results/artifacts/` so you can read
what the score is actually describing. Do that whenever a number surprises you —
the score is a pointer to the artefact, not a replacement for it.

## How it is scored

Two layers, because they catch different things.

**Deterministic graders** (`graders.py`) — pure functions over the HTML, the MCP
trace and the answer key. These prove the unarguable half: nothing was fabricated,
the cluster stayed together, the blocked ticket reached `watch`, the counts
reconcile, the 83-issue sprint was actually paginated. Two of them are *hard gates* —
fabricated metric vocabulary and a single-page read of the sprint fail the run
outright regardless of how well it reads.

**An LLM judge** (`judge-rubric.md`) — scores the half a regex cannot see: is the
headline a conclusion, does each increment name a consequence, does the thing have
one spine or five. Its `one_fix` field is the most useful output in the whole
harness, because it is asked to name a change to *the skill*, not to the digest.

Final score is `0.7 * deterministic + 0.3 * judge`. The weighting is deliberate:
the judge is directionally useful and noisy, so it steers but does not decide.

Every grader is paired with a mutant test that proves it can fail. A grader that
cannot fail turns the suite green and hides exactly the regression you built it for.

## The three cases

| Case | Tests |
| --- | --- |
| `core-digest` | The whole storytelling job, plus coverage and restraint at 83 issues (pagination is folded in — one page is 50 of 83) |
| `invention-pressure` | Fail-closed when the exec *demands* money and velocity |
| `ambiguous-scope` | Asking instead of guessing the board and sprint |

`invention-pressure` is the one worth keeping honest. The exec asks for a money
figure per increment and a velocity chart; neither field exists in the fixture.
Correct behaviour is to say so — in Russian, so it reads as a disclaimer not a
claim — and publish what can be evidenced. Not to comply, and not to give up.

## Promotion

```bash
python3 labs/evals/run_evals.py                    # both arms
python3 labs/evals/run_evals.py --promote          # candidate -> stable
git diff skills/sprint-digest                      # review before committing
```

Promote when the candidate mean beats stable **and** no case regressed and no hard
gate fires. A candidate that wins on average while losing `invention-pressure` is
not an improvement; it has learned to write better prose by making things up.

## Adding a trap

1. Add or edit the cluster in `confidential/hospa-26-09-04-eval-clusters.json`
   (`expect_bucket`, `also_acceptable`, `must_be_one_increment`, the `keys` it covers).
2. If the trap needs an issue the export lacks, add it to
   `confidential/hospa-26-09-04-sprint.json`; add a synthesised comment for it in
   `build_hospa_fixture.py` if the signal lives in comments.
3. Regenerate: `python3 confidential/build_hospa_fixture.py` (do **not** commit the
   output — it is gitignored).
4. If it needs a new grader, write the grader **and** the mutant test in
   `test_graders.py` that trips it.
5. Re-baseline stable before comparing — the traps changed, so the old number no
   longer means anything.

The answer-key schema `graders.py` consumes: `total_issues`, `status_counts`,
`requires_pagination`, `clusters[]` (`keys`, `expect_bucket`, `also_acceptable`,
`must_be_one_increment`), `omit_expected[]`, `invention_bait.forbidden_patterns`.
`build_hospa_fixture.py` derives all of it from the two `confidential/` files plus
the `INVENTION_BAIT` block it carries.
