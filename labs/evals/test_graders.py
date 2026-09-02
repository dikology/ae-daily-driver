"""Tests for graders.py.

A grader that cannot fail is worse than no grader — it turns every run green and
hides the regression you built the harness to catch. So each grader gets both a
digest that should satisfy it and a mutant that should trip it.

    python3 -m pytest labs/evals/test_graders.py -q
"""

import json
from pathlib import Path

import pytest

from graders import (
    bucket_of, grade, segment, visible_text,
    g_bucket_placement, g_claim_labels, g_cluster_unity, g_conclusion_titles,
    g_counts_reconcile, g_evidence_links, g_evidence_targeting, g_increment_count,
    g_lead_is_not_a_dump, g_no_invention, g_omit_discipline, g_pagination,
)

KEYS = Path(__file__).parent / "fixtures" / "keys"


@pytest.fixture
def key():
    return json.loads((KEYS / "s26-08-core.json").read_text())


@pytest.fixture
def wide_key():
    return json.loads((KEYS / "s26-09-wide.json").read_text())


def browse(k):
    return f'<a href="https://acme.atlassian.net/browse/{k}">{k}</a>'


GOOD = """
<h1>Customer Success stopped maintaining the retention sheet by hand</h1>
<section class="headline">
  <p>Cohort retention for the last 18 months is now a Metabase dashboard fed by a
  modelled event stream, and the Q3 renewal review on 2026-09-08 will run off it.</p>
</section>
<section class="increments">
  <article class="increment">
    <h2>Churn cohorts moved from a manual sheet to a modelled dashboard</h2>
    <p class="claim-meta">observed</p>
    <div class="evidence">{a412} {a418} {a421} — https://metabase.acme.io/dashboard/311-churn-cohorts</div>
    <p class="why-it-matters">The CS lead confirmed the Q3 renewal review uses it.</p>
  </article>
  <article class="increment">
    <h2>Campaign attribution is off the table until the CDN drops less data</h2>
    <p class="claim-meta">observed</p>
    <div class="evidence">{a430} — campaign_id absent for 94% of trial signups</div>
    <p class="why-it-matters">Growth deferred the attribution epic to Q4.</p>
  </article>
  <article class="increment">
    <h2>The nightly run now finishes before the working day starts</h2>
    <p class="claim-meta">synthesis</p>
    <div class="evidence">{a419} — 42 min down to 11 min</div>
  </article>
</section>
<section class="watch">
  <article class="increment">
    <h2>Rev-rec v2 has been waiting nine days on a Finance scope answer</h2>
    <p class="claim-meta">observed</p>
    <div class="evidence">{a425}</div>
  </article>
  <article class="increment">
    <h2>The funnel dataset shipped without a named owner</h2>
    <p class="claim-meta">unresolved</p>
    <div class="evidence">{a427}</div>
  </article>
</section>
<section class="appendix">
  <h2>Appendix</h2>
  <p>Scope: 14 issues — 11 Done, 1 In Progress, 1 Blocked, 1 To Do.</p>
  <table class="omissions">
    <tr><td>AE-405</td><td>omit</td><td>No downstream consumers.</td></tr>
    <tr><td>AE-401</td><td>omit</td><td>Routine alert tuning.</td></tr>
    <tr><td>AE-408</td><td>omit</td><td>Routine fix.</td></tr>
    <tr><td>AE-433</td><td>omit</td><td>Docs cleanup.</td></tr>
    <tr><td>AE-436</td><td>omit</td><td>Dependency bump.</td></tr>
    <tr><td>AE-444</td><td>omit</td><td>Not started.</td></tr>
  </table>
</section>
""".format(a412=browse("AE-412"), a418=browse("AE-418"), a421=browse("AE-421"),
           a419=browse("AE-419"), a425=browse("AE-425"), a427=browse("AE-427"),
           a430=browse("AE-430"))

GOOD_TRACE = (
    [{"tool": "jira_get_sprint_issues", "args": {"sprint_id": "991", "startAt": 0}}]
    + [{"tool": "jira_get_issue", "args": {"issue_key": k}}
       for k in ("AE-412", "AE-418", "AE-421", "AE-430", "AE-419", "AE-425", "AE-427")]
)


# --- the happy path ----------------------------------------------------------

def test_good_digest_scores_high(key):
    out = grade(GOOD, GOOD_TRACE, key)
    assert out["hard_fail"] == []
    assert out["score"] >= 0.9, json.dumps(out, indent=2)


# --- one mutant per grader ---------------------------------------------------

def test_invented_metrics_hard_fail(key):
    bad = GOOD.replace("<p>Cohort retention",
                       "<p>Velocity rose to 34 story points, saving $40k a year. Cohort retention")
    r = g_no_invention(bad, key)
    assert r.score == 0.0 and r.hard
    assert "story" in r.note  # note carries the pattern, not the literal
    assert "no_invention" in grade(bad, GOOD_TRACE, key)["hard_fail"]


def test_clean_digest_passes_invention_gate(key):
    assert g_no_invention(GOOD, key).score == 1.0


def test_counts_must_reconcile(key):
    bad = GOOD.replace("14 issues — 11 Done, 1 In Progress, 1 Blocked, 1 To Do",
                       "a busy sprint across the team")
    assert g_counts_reconcile(bad, key).score == 0.0
    assert g_counts_reconcile(GOOD, key).score == 1.0


def test_split_cluster_is_penalised(key):
    """The three churn keys in three separate increments is the failure this
    fixture exists to catch."""
    bad = GOOD.replace(
        '<div class="evidence">%s %s %s' % (browse("AE-412"), browse("AE-418"), browse("AE-421")),
        '<div class="evidence">%s' % browse("AE-412"))
    bad = bad.replace("</section>\n<section class=\"watch\">", """
  <article class="increment"><h2>A model landed</h2>
    <div class="evidence">%s</div></article>
  <article class="increment"><h2>A backfill ran</h2>
    <div class="evidence">%s</div></article>
</section>
<section class="watch">""" % (browse("AE-418"), browse("AE-421")), 1)
    assert g_cluster_unity(bad, key).score < g_cluster_unity(GOOD, key).score
    assert g_cluster_unity(GOOD, key).score == 1.0


def test_thin_spike_must_not_be_omitted(key):
    """AE-430 relegated to the omissions table is the 'looks small, decided a
    quarter' failure."""
    bad = GOOD.replace(
        '<article class="increment">\n    <h2>Campaign attribution is off the table '
        'until the CDN drops less data</h2>\n    <p class="claim-meta">observed</p>\n'
        '    <div class="evidence">%s — campaign_id absent for 94%% of trial signups</div>\n'
        '    <p class="why-it-matters">Growth deferred the attribution epic to Q4.</p>\n'
        '  </article>\n' % browse("AE-430"), "")
    bad = bad.replace("<tr><td>AE-405</td>",
                      "<tr><td>AE-430</td><td>omit</td><td>Just a spike.</td></tr>\n    <tr><td>AE-405</td>")
    assert g_bucket_placement(bad, key).score < g_bucket_placement(GOOD, key).score


def test_blocked_work_belongs_in_watch(key):
    blocks = segment(GOOD)
    assert bucket_of(blocks, "AE-425") == "watch"
    assert bucket_of(blocks, "AE-412") == "increment"
    assert bucket_of(blocks, "AE-405") == "omit"


def test_routine_work_promoted_is_penalised(key):
    bad = GOOD.replace('<div class="evidence">%s</div>' % browse("AE-425"),
                       '<div class="evidence">%s %s</div>' % (browse("AE-425"), browse("AE-405")))
    bad = bad.replace("<section class=\"watch\">", "<section class=\"increments\">", 1)
    assert g_omit_discipline(bad, key).score < 1.0
    assert g_omit_discipline(GOOD, key).score == 1.0


def test_unlabelled_open_claim_is_penalised(key):
    bad = GOOD.replace('<p class="claim-meta">unresolved</p>',
                       '<p class="claim-meta">observed</p>')
    bad = bad.replace("<section class=\"watch\">", "<section class=\"increments\">", 1)
    assert g_claim_labels(bad, key).score < g_claim_labels(GOOD, key).score


def test_missing_browse_links_penalised(key):
    bad = GOOD.replace('href="https://acme.atlassian.net/browse/', 'href="#')
    assert g_evidence_links(bad, key).score == 0.0
    assert g_evidence_links(GOOD, key).score == 1.0


def test_label_titles_penalised(key):
    bad = GOOD.replace(
        "<h1>Customer Success stopped maintaining the retention sheet by hand</h1>",
        "<h1>Sprint Digest</h1>")
    bad = bad.replace("<h2>Churn cohorts moved from a manual sheet to a modelled dashboard</h2>",
                      "<h2>Increment 1</h2>")
    assert g_conclusion_titles(bad, key).score < g_conclusion_titles(GOOD, key).score
    assert g_conclusion_titles(GOOD, key).score == 1.0


def test_status_dump_lead_is_caught(key):
    bad = GOOD.replace(
        "<p>Cohort retention for the last 18 months is now a Metabase dashboard fed by a",
        "<p>The team completed 11 issues this sprint. Cohort retention is now a dashboard fed by a")
    assert g_lead_is_not_a_dump(bad, key).score == 0.0
    assert g_lead_is_not_a_dump(GOOD, key).score == 1.0


def test_too_many_increments_penalised(key):
    extra = "".join('<article class="increment"><h2>Another thing happened %d</h2>'
                    '<div class="evidence">AE-%d</div></article>' % (i, 700 + i)
                    for i in range(6))
    bad = GOOD.replace("</section>\n<section class=\"watch\">", extra + "</section>\n<section class=\"watch\">", 1)
    assert g_increment_count(bad, key).score < g_increment_count(GOOD, key).score


def test_pagination_required_only_on_wide(key, wide_key):
    one_page = [{"tool": "jira_get_sprint_issues", "args": {"sprint_id": "992", "startAt": 0}}]
    two_page = one_page + [{"tool": "jira_get_sprint_issues",
                            "args": {"sprint_id": "992", "startAt": 50}}]
    assert g_pagination(one_page, wide_key).score == 0.0
    assert g_pagination(one_page, wide_key).hard
    assert g_pagination(two_page, wide_key).score == 1.0
    assert g_pagination(one_page, key).weight == 0.0  # not scored on the small sprint


def test_never_reading_comments_hard_fails(key):
    trace = [{"tool": "jira_get_sprint_issues", "args": {"sprint_id": "991", "startAt": 0}}]
    r = g_evidence_targeting(trace, key)
    assert r.score == 0.0 and r.hard


def test_fanning_out_to_every_ticket_scores_below_targeted(key):
    everything = GOOD_TRACE + [{"tool": "jira_get_issue", "args": {"issue_key": "AE-%d" % k}}
                               for k in (401, 405, 408, 433, 436, 440, 444)]
    assert g_evidence_targeting(everything, key).score < g_evidence_targeting(GOOD_TRACE, key).score


# --- helpers -----------------------------------------------------------------

def test_visible_text_drops_script_and_style():
    html = "<style>.x{color:red}</style><script>var burndown=1;</script><p>hello</p>"
    t = visible_text(html).lower()
    assert "hello" in t and "burndown" not in t and "color" not in t


def test_script_contents_do_not_trip_invention_gate(key):
    """Chart data in a <script> block is data, not a claim."""
    html = GOOD.replace("</section>", "<script>const capacity=[1,2];</script></section>", 1)
    assert g_no_invention(html, key).score == 1.0


# --- regressions: false positives caught by the first real run ---------------
# Both of these scored a real, well-behaved digest as a failure. Left unfixed they
# would have steered iteration backwards — the invention gate in particular was
# punishing the fail-closed disclaimer the contract asks for.

REAL_DISCLAIMER = (
    "<section class='appendix'><p>Total in sprint 14. Counts are status counts only. "
    "Story points, burndown, and team capacity were not fetched and are not claimed. "
    "No chart appears in this briefing because no fetched series supports one.</p></section>")


def test_disclaiming_absent_metrics_is_not_invention(key):
    r = g_no_invention(GOOD + REAL_DISCLAIMER, key)
    assert r.score == 1.0, r.note
    assert not r.hard or r.score == 1.0
    assert "disclaim" in r.note


def test_asserted_metric_still_fails_next_to_a_disclaimer(key):
    html = (GOOD + REAL_DISCLAIMER +
            "<p>Separately, the team burned 34 story points against a 40 point capacity.</p>")
    assert g_no_invention(html, key).score == 0.0


def test_sprint_end_date_is_not_a_ticket_count(key):
    html = GOOD.replace(
        '<section class="headline">',
        '<section class="headline"><p>Window 2026-08-10 to 2026-08-24 (closed 2026-08-24).</p>')
    assert g_lead_is_not_a_dump(html, key).score == 1.0


def test_lead_class_is_treated_as_headline(key):
    html = GOOD.replace('<section class="headline">', '<section class="lead">')
    assert g_lead_is_not_a_dump(html, key).score == 1.0
    bad = html.replace("<p>Cohort retention", "<p>We closed 11 issues this sprint. Cohort retention")
    assert g_lead_is_not_a_dump(bad, key).score == 0.0


def test_invention_patterns_are_word_anchored(key):
    """An unanchored 'fte' matches inside 'after'. That false positive hard-failed
    a clean digest on the first real run."""
    html = GOOD.replace("<p>Cohort retention",
                        "<p>After the shift we often refactored the softer parts. Cohort retention")
    assert g_no_invention(html, key).score == 1.0
