#!/usr/bin/env python3
"""Fixture-backed stand-in for the Jira MCP server.

Speaks enough MCP over stdio for `sprint-digest` step 2 to run verbatim:
board lookup -> sprint lookup -> paginated sprint issues -> per-issue detail.

Fixtures live in fixtures/sprints/<sprint-slug>.json. One file holds one board,
one sprint, and its issues. Nothing is invented here: whatever the digest cites
has to come out of a fixture, which is what makes the invention graders possible.

Every tool call is appended to $MOCK_JIRA_TRACE as JSONL so graders can check
evidence-gathering behaviour (did it paginate? did it pull comments only for
candidates?) and not just the final HTML.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

FIXTURES = Path(os.environ.get("MOCK_JIRA_FIXTURES") or Path(__file__).parent / "fixtures" / "sprints")
TRACE = os.environ.get("MOCK_JIRA_TRACE")
PROTOCOL_VERSION = "2024-11-05"

# Fields jira_get_sprint_issues is allowed to return. Comments and changelog are
# deliberately absent — the skill is supposed to fetch those per candidate.
LIST_FIELDS = {
    "summary", "status", "priority", "assignee", "updated", "created",
    "issuetype", "components", "labels", "resolutiondate", "parent",
}


def load_sprints() -> list[dict]:
    out = []
    for path in sorted(FIXTURES.glob("*.json")):
        data = json.loads(path.read_text())
        data["_slug"] = path.stem
        out.append(data)
    return out


def trace(tool: str, args: dict, note: str = "") -> None:
    if not TRACE:
        return
    with open(TRACE, "a") as fh:
        fh.write(json.dumps({"tool": tool, "args": args, "note": note}) + "\n")


def strip_fields(issue: dict, allowed: set) -> dict:
    fields = {k: v for k, v in issue.get("fields", {}).items() if k in allowed}
    return {"key": issue["key"], "id": issue.get("id", issue["key"]), "fields": fields}


# --- tools -------------------------------------------------------------------

def t_get_agile_boards(args: dict) -> dict:
    name = (args.get("board_name") or "").lower()
    boards = []
    for s in load_sprints():
        b = s["board"]
        if name and name not in b["name"].lower():
            continue
        if b not in boards:
            boards.append(b)
    return {"values": boards, "total": len(boards)}


def t_get_sprints_from_board(args: dict) -> dict:
    board_id = str(args.get("board_id", ""))
    state = args.get("state")
    sprints = []
    for s in load_sprints():
        if str(s["board"]["id"]) != board_id:
            continue
        sp = dict(s["sprint"])
        if state and sp.get("state") != state:
            continue
        sprints.append(sp)
    return {"values": sprints, "total": len(sprints)}


def _find_sprint(sprint_id: str) -> dict | None:
    for s in load_sprints():
        if str(s["sprint"]["id"]) == str(sprint_id):
            return s
    return None


def t_get_sprint_issues(args: dict) -> dict:
    sprint = _find_sprint(args.get("sprint_id", ""))
    if sprint is None:
        return {"error": f"sprint {args.get('sprint_id')!r} not found"}

    issues = sprint["issues"]
    start = int(args.get("startAt", args.get("start_at", 0)) or 0)
    limit = int(args.get("limit", 50) or 50)
    limit = min(limit, 50)
    page = issues[start:start + limit]

    requested = args.get("fields")
    if isinstance(requested, str):
        requested = [f.strip() for f in requested.split(",") if f.strip()]
    allowed = LIST_FIELDS if not requested else (set(requested) & LIST_FIELDS)

    note = "page %d-%d of %d" % (start, start + len(page), len(issues))
    if requested and set(requested) - LIST_FIELDS:
        note += "; dropped non-list fields: %s" % sorted(set(requested) - LIST_FIELDS)
    trace("jira_get_sprint_issues", args, note)

    return {
        "startAt": start,
        "maxResults": limit,
        "total": len(issues),
        "issues": [strip_fields(i, allowed) for i in page],
    }


def t_get_issue(args: dict) -> dict:
    key = args.get("issue_key") or args.get("issue_id_or_key") or ""
    for s in load_sprints():
        for issue in s["issues"]:
            if issue["key"] != key:
                continue
            out = json.loads(json.dumps(issue))  # deep copy
            limit = int(args.get("comment_limit", 10) or 10)
            comments = out.get("fields", {}).get("comment", {}).get("comments", [])
            out["fields"].setdefault("comment", {})["comments"] = comments[:limit]
            out["fields"]["comment"]["total"] = len(comments)
            expand = args.get("expand") or ""
            if "changelog" not in expand:
                out.pop("changelog", None)
            out["self"] = "%s/rest/api/2/issue/%s" % (s["board"]["base_url"], key)
            return out
    return {"error": f"issue {key!r} not found"}


TOOLS = [
    {
        "name": "jira_get_agile_boards",
        "description": "List Jira agile boards, optionally filtered by name.",
        "inputSchema": {
            "type": "object",
            "properties": {"board_name": {"type": "string"}},
        },
    },
    {
        "name": "jira_get_sprints_from_board",
        "description": "List sprints on a board. state: active | closed | future.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "board_id": {"type": "string"},
                "state": {"type": "string"},
            },
            "required": ["board_id"],
        },
    },
    {
        "name": "jira_get_sprint_issues",
        "description": (
            "Issues in a sprint. Paginated (limit max 50). Returns list-level "
            "fields only — comments and changelog need jira_get_issue."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "sprint_id": {"type": "string"},
                "fields": {"type": "string"},
                "limit": {"type": "integer"},
                "startAt": {"type": "integer"},
            },
            "required": ["sprint_id"],
        },
    },
    {
        "name": "jira_get_issue",
        "description": "One issue in full: description, comments, links, changelog via expand.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "issue_key": {"type": "string"},
                "fields": {"type": "string"},
                "comment_limit": {"type": "integer"},
                "expand": {"type": "string"},
            },
            "required": ["issue_key"],
        },
    },
]

HANDLERS = {
    "jira_get_agile_boards": t_get_agile_boards,
    "jira_get_sprints_from_board": t_get_sprints_from_board,
    "jira_get_sprint_issues": t_get_sprint_issues,
    "jira_get_issue": t_get_issue,
}


# --- MCP stdio loop ----------------------------------------------------------

def send(msg: dict) -> None:
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def handle(req: dict) -> dict | None:
    method = req.get("method")
    rid = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": rid,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "mock-jira", "version": "1.0.0"},
            },
        }
    if method in ("notifications/initialized", "notifications/cancelled"):
        return None
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = req.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {}) or {}
        fn = HANDLERS.get(name)
        if fn is None:
            return {"jsonrpc": "2.0", "id": rid,
                    "error": {"code": -32601, "message": f"unknown tool {name}"}}
        if name not in ("jira_get_sprint_issues",):  # that one traces itself, with a note
            trace(name, args)
        try:
            payload = fn(args)
        except Exception as exc:  # surface as a tool error, not a transport crash
            return {"jsonrpc": "2.0", "id": rid,
                    "result": {"content": [{"type": "text", "text": f"error: {exc}"}],
                               "isError": True}}
        return {"jsonrpc": "2.0", "id": rid,
                "result": {"content": [{"type": "text",
                                        "text": json.dumps(payload, ensure_ascii=False)}]}}

    if rid is None:
        return None
    return {"jsonrpc": "2.0", "id": rid,
            "error": {"code": -32601, "message": f"unknown method {method}"}}


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(req)
        if resp is not None:
            send(resp)


if __name__ == "__main__":
    main()
