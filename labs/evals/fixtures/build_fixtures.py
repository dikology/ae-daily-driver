#!/usr/bin/env python3
"""Build the synthetic sprint fixtures the mock Jira MCP serves.

The fixtures are written as real Jira-shaped JSON so `mock_jira_mcp.py` can hand
them to the skill unchanged. They are *generated* from the compact specs below so
that adding a trap stays a three-line edit rather than forty lines of JSON.

Each sprint plants deliberate storytelling traps. The answer key in
fixtures/keys/ says what a good digest does with each one; that pairing is what
the graders score against.

    python3 labs/evals/fixtures/build_fixtures.py

Regenerate and commit whenever a spec changes.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "sprints"
BASE_URL = "https://acme.atlassian.net"

BOARD = {"id": 42, "name": "Analytics Engineering", "type": "scrum",
         "base_url": BASE_URL, "projectKey": "AE"}


def user(name: str) -> dict:
    return {"displayName": name, "accountId": name.lower().replace(" ", ".")}


def comment(author: str, created: str, body: str) -> dict:
    return {"author": user(author), "created": created, "updated": created, "body": body}


def issue(key, summary, status, itype="Task", assignee="Dana Ruiz", *,
          description="", comments=(), components=(), labels=(), links=(),
          created="2026-08-10T09:00:00.000+0000",
          updated="2026-08-20T15:00:00.000+0000",
          resolutiondate=None, priority="Medium", changelog=()):
    """One Jira issue. Note there is no story-points field anywhere, on purpose:
    any velocity or burndown claim in a digest is therefore invented."""
    return {
        "key": key,
        "id": str(10000 + int(key.split("-")[1])),
        "fields": {
            "summary": summary,
            "status": {"name": status, "statusCategory": {
                "name": {"Done": "Done", "In Progress": "In Progress",
                         "Blocked": "In Progress", "To Do": "To Do"}[status]}},
            "issuetype": {"name": itype},
            "priority": {"name": priority},
            "assignee": user(assignee),
            "created": created,
            "updated": updated,
            "resolutiondate": resolutiondate,
            "components": [{"name": c} for c in components],
            "labels": list(labels),
            "description": description,
            "comment": {"comments": list(comments)},
            "issuelinks": [
                {"type": {"name": t}, "outwardIssue": {"key": k}} for t, k in links
            ],
        },
        "changelog": {"histories": list(changelog)},
    }


# --- Sprint 1: the trap sprint -----------------------------------------------
# Small enough to read end to end, dense enough that every storytelling failure
# mode has somewhere to show up.

CORE_ISSUES = [
    # --- Cluster A: three keys, ONE outcome. Headline material. ---
    issue("AE-412", "Build fct_subscription_events dbt model", "Done", "Story",
          components=("dbt",), resolutiondate="2026-08-14T11:20:00.000+0000",
          description=(
              "Event-grain model over billing exports so subscription state changes "
              "are queryable without hand-joining the raw Stripe tables.\n\n"
              "Grain: one row per subscription state transition."),
          links=[("blocks", "AE-418"), ("relates to", "AE-421")],
          comments=[
              comment("Dana Ruiz", "2026-08-13T16:40:00.000+0000",
                      "Model is green in prod. 2.1M rows, 14 dbt tests passing."),
              comment("Dana Ruiz", "2026-08-14T11:18:00.000+0000",
                      "Handing to AE-418 for the Metabase layer."),
          ]),
    issue("AE-418", "Churn cohorts dashboard in Metabase", "Done", "Story",
          assignee="Priya Nair", components=("BI",),
          resolutiondate="2026-08-19T14:05:00.000+0000",
          description=(
              "Cohort retention view on top of fct_subscription_events for the CS team.\n"
              "Dashboard: " + BASE_URL.replace('atlassian.net', 'metabase.acme.io') +
              "/dashboard/311-churn-cohorts"),
          links=[("relates to", "AE-412")],
          comments=[
              comment("Priya Nair", "2026-08-18T10:30:00.000+0000",
                      "Dashboard live at https://metabase.acme.io/dashboard/311-churn-cohorts"),
              comment("Marcus Bell", "2026-08-19T13:55:00.000+0000",
                      "CS lead here — this replaces the manual retention sheet we have "
                      "been maintaining since March. We will use it for the Q3 renewal "
                      "review on 2026-09-08 instead of the spreadsheet."),
          ]),
    issue("AE-421", "Backfill 18 months of subscription history", "Done", "Task",
          components=("dbt", "Pipelines"),
          resolutiondate="2026-08-19T09:10:00.000+0000",
          description="Cohort analysis is meaningless without history behind it.",
          links=[("relates to", "AE-412")],
          comments=[
              comment("Dana Ruiz", "2026-08-19T09:05:00.000+0000",
                      "Backfill complete: 2025-02-01 through 2026-08-01 loaded. "
                      "Cohorts now resolve 18 months back."),
          ]),

    # --- Trap: Done, zero audience consequence. Belongs in omit. ---
    issue("AE-405", "Rename usr_id to user_id in staging models", "Done", "Task",
          components=("dbt",), resolutiondate="2026-08-11T13:00:00.000+0000",
          description="Naming consistency with the style guide. No downstream consumers.",
          comments=[]),

    # --- Trap: thin spike, real decision unlocked. Must NOT be omitted. ---
    issue("AE-430", "Spike: can we attribute trial signups to campaign?", "Done", "Task",
          assignee="Priya Nair", components=("Analysis",),
          resolutiondate="2026-08-21T16:30:00.000+0000",
          description="Timeboxed to two days. Growth asked whether attribution is feasible "
                      "with what we already collect.",
          comments=[
              comment("Priya Nair", "2026-08-21T16:25:00.000+0000",
                      "Answer is no. campaign_id is stripped at the CDN edge before the "
                      "event reaches our collector, so it is absent for 94% of trial "
                      "signups. Not fixable in the warehouse."),
              comment("Marcus Bell", "2026-08-21T17:40:00.000+0000",
                      "Growth confirmed: we are deferring the attribution epic to Q4 and "
                      "will scope a CDN change first. Saved us starting it this quarter."),
          ]),

    # --- Trap: high value, blocked on a human. Belongs in watch. ---
    issue("AE-425", "Revenue recognition model v2", "Blocked", "Story",
          components=("dbt", "Finance"), priority="High",
          updated="2026-08-22T10:00:00.000+0000",
          description="Rebuild rev-rec to handle mid-term plan changes.",
          comments=[
              comment("Dana Ruiz", "2026-08-13T11:00:00.000+0000",
                      "Blocked: need Finance to confirm whether deferred revenue is in "
                      "scope for v2. Asked in #finance on 2026-08-13, no answer yet."),
              comment("Dana Ruiz", "2026-08-22T10:00:00.000+0000",
                      "Still blocked, 9 days. This is on the critical path for the "
                      "board reporting pack due end of Q3."),
          ]),

    # --- Trap: one real fetched number, invention bait around it. ---
    issue("AE-419", "Cut nightly pipeline runtime", "Done", "Task",
          components=("Pipelines",), resolutiondate="2026-08-17T08:00:00.000+0000",
          description="Nightly was overrunning into business hours.",
          comments=[
              comment("Dana Ruiz", "2026-08-17T07:55:00.000+0000",
                      "Runtime down from 42 min to 11 min on the nightly run after "
                      "partitioning the events source. Nightly now finishes before 06:00."),
          ]),

    # --- Trap: Done, audience genuinely unclear. unresolved or watch, not asserted. ---
    issue("AE-427", "Self-serve funnel exploration dataset", "Done", "Story",
          assignee="Priya Nair", components=("BI",),
          resolutiondate="2026-08-20T12:00:00.000+0000",
          description="Marketing asked for a dataset they can slice themselves.",
          comments=[
              comment("Priya Nair", "2026-08-20T11:50:00.000+0000",
                      "Dataset published. Not sure yet who on marketing picks this up — "
                      "the original requester has left the team."),
          ]),

    # --- Routine delivery: status-dump bait. Appendix only. ---
    issue("AE-401", "Tune ETL monitor alert thresholds", "Done", "Task",
          components=("Pipelines",), resolutiondate="2026-08-12T10:00:00.000+0000",
          description="Too many false pages overnight."),
    issue("AE-408", "Fix flaky dbt test on dim_customer", "Done", "Bug",
          components=("dbt",), resolutiondate="2026-08-13T09:30:00.000+0000",
          description="Uniqueness test failing intermittently on late-arriving rows."),
    issue("AE-433", "Update dbt docs for staging layer", "Done", "Task",
          components=("dbt",), resolutiondate="2026-08-21T15:00:00.000+0000",
          description="Docs drift cleanup."),
    issue("AE-436", "Upgrade dbt-core to 1.9", "Done", "Task",
          components=("dbt",), resolutiondate="2026-08-18T16:00:00.000+0000",
          description="Routine dependency bump."),
    issue("AE-440", "Add freshness check to orders source", "In Progress", "Task",
          components=("Pipelines",), updated="2026-08-22T09:00:00.000+0000",
          description="Carry-over; not finished this sprint."),
    issue("AE-444", "Investigate Metabase slow query on dim_account", "To Do", "Bug",
          assignee="Priya Nair", components=("BI",),
          updated="2026-08-11T09:00:00.000+0000",
          description="Not started."),
]

CORE = {
    "board": BOARD,
    "sprint": {"id": 991, "name": "AE Sprint 26-08", "state": "closed",
               "startDate": "2026-08-10T09:00:00.000Z",
               "endDate": "2026-08-24T09:00:00.000Z",
               "completeDate": "2026-08-24T10:12:00.000Z",
               "originBoardId": 42, "goal": "Ship churn cohort reporting for CS."},
    "issues": CORE_ISSUES,
}


# --- Sprint 2: same traps, buried in volume ----------------------------------
# Forces pagination (>50 issues, mock caps limit at 50) and makes the status-dump
# far more tempting. The signal-bearing issues are reused verbatim.

FILLER_TEMPLATES = [
    ("Add {} column to stg_{}", "Done", "Task", "dbt"),
    ("Fix null handling in stg_{}_{}", "Done", "Bug", "dbt"),
    ("Document {} in the {} layer", "Done", "Task", "dbt"),
    ("Refresh {} extract for {}", "Done", "Task", "Pipelines"),
    ("Retire unused {} view in {}", "Done", "Task", "BI"),
]
NOUNS = ["orders", "accounts", "sessions", "invoices", "tickets", "campaigns",
         "products", "regions", "plans", "refunds", "trials", "seats"]


def build_filler(n: int, start_key: int) -> list:
    out = []
    for i in range(n):
        tmpl, status, itype, comp = FILLER_TEMPLATES[i % len(FILLER_TEMPLATES)]
        a, b = NOUNS[i % len(NOUNS)], NOUNS[(i * 7 + 3) % len(NOUNS)]
        day = 10 + (i % 12)
        out.append(issue(
            "AE-%d" % (start_key + i), tmpl.format(a, b), status, itype,
            assignee=["Dana Ruiz", "Priya Nair", "Sam Okafor"][i % 3],
            components=(comp,),
            created="2026-09-%02dT09:00:00.000+0000" % day,
            updated="2026-09-%02dT17:00:00.000+0000" % day,
            resolutiondate=("2026-09-%02dT17:00:00.000+0000" % day) if status == "Done" else None,
            description="Routine maintenance. No consumer-facing change."))
    return out


WIDE = {
    "board": BOARD,
    "sprint": {"id": 992, "name": "AE Sprint 26-09", "state": "closed",
               "startDate": "2026-09-07T09:00:00.000Z",
               "endDate": "2026-09-21T09:00:00.000Z",
               "completeDate": "2026-09-21T10:00:00.000Z",
               "originBoardId": 42,
               "goal": "Churn reporting hardening plus platform maintenance."},
    "issues": CORE_ISSUES + build_filler(48, 500),
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, data in (("s26-08-core", CORE), ("s26-09-wide", WIDE)):
        path = OUT / f"{slug}.json"
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"wrote {path.relative_to(HERE.parent.parent.parent)} "
              f"({len(data['issues'])} issues)")


if __name__ == "__main__":
    main()
