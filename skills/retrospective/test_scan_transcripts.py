"""Tests for Cursor transcript scanning."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from scan_transcripts import (
    decode_project_slug,
    discover_sessions,
    extract_user_query,
    format_sessions,
    parse_transcript,
)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def _user(text: str) -> dict:
    return {"role": "user", "message": {"content": [{"type": "text", "text": text}]}}


def _assistant(text: str = "", tools: list[tuple[str, dict]] | None = None) -> dict:
    content: list[dict] = []
    if text:
        content.append({"type": "text", "text": text})
    for name, inp in tools or []:
        content.append({"type": "tool_use", "name": name, "input": inp})
    return {"role": "assistant", "message": {"content": content}}


def test_extract_user_query_strips_wrapper():
    raw = "<timestamp>Thu</timestamp>\n<user_query>\nadapt this skill\n</user_query>"
    assert extract_user_query(raw) == "adapt this skill"


def test_extract_user_query_plain_text():
    assert extract_user_query("just a question") == "just a question"


def test_decode_project_slug_walks_real_dirs(tmp_path: Path):
    home = tmp_path / "Users" / "dikology"
    project = home / "dikology" / "ae-daily-driver"
    project.mkdir(parents=True)
    slug = str(project).lstrip("/").replace("/", "-")
    name, resolved = decode_project_slug(slug, home=home)
    assert name == "ae-daily-driver"
    assert resolved == project


def test_decode_empty_window():
    name, resolved = decode_project_slug("empty-window")
    assert name == "(empty window)"
    assert resolved is None


def test_parse_transcript_counts_queries_tools_skills(tmp_path: Path):
    jsonl = tmp_path / "Users-me-proj" / "agent-transcripts" / "abc-def" / "abc-def.jsonl"
    _write_jsonl(
        jsonl,
        [
            _user("<user_query>first</user_query>"),
            _assistant(
                "working",
                tools=[
                    (
                        "Read",
                        {"path": "/Users/me/proj/.cursor/skills/telegram/SKILL.md"},
                    ),
                    ("Shell", {"command": "ls"}),
                ],
            ),
            {"type": "turn_ended", "status": "success"},
            _user(
                "<manually_attached_skills>\nSkill Name: triage-analytics\n</manually_attached_skills>\n"
                "<user_query>second</user_query>"
            ),
            _user("<user_query>third</user_query>"),
        ],
    )
    summary = parse_transcript(jsonl, home=tmp_path / "Users" / "me")
    assert summary.uuid == "abc-def"
    assert summary.user_queries == ["first", "second", "third"]
    assert "Shell" in summary.tools
    assert "telegram" in summary.skills
    assert "triage-analytics" in summary.skills


def test_discover_filters_by_date_and_min_messages(tmp_path: Path):
    root = tmp_path / "projects"
    keep = (
        root
        / "Users-me-keep"
        / "agent-transcripts"
        / "11111111-1111-1111-1111-111111111111"
        / "11111111-1111-1111-1111-111111111111.jsonl"
    )
    skip_short = (
        root
        / "Users-me-short"
        / "agent-transcripts"
        / "22222222-2222-2222-2222-222222222222"
        / "22222222-2222-2222-2222-222222222222.jsonl"
    )
    skip_sub = (
        root
        / "Users-me-keep"
        / "agent-transcripts"
        / "11111111-1111-1111-1111-111111111111"
        / "subagents"
        / "sub.jsonl"
    )
    _write_jsonl(
        keep,
        [
            _user("<user_query>one</user_query>"),
            _user("<user_query>two</user_query>"),
            _user("<user_query>three</user_query>"),
        ],
    )
    _write_jsonl(skip_short, [_user("<user_query>only one</user_query>")])
    _write_jsonl(skip_sub, [_user("<user_query>sub</user_query>")] * 5)

    today = date.today()
    sessions = discover_sessions(
        target=today,
        min_user_messages=3,
        root=root,
        home=tmp_path / "Users" / "me",
    )
    assert len(sessions) == 1
    assert sessions[0].short_id == "11111111"
    listing = format_sessions(sessions, today)
    assert "Found 1 sessions" in listing
    assert "one" in listing


def test_discover_empty_root(tmp_path: Path):
    sessions = discover_sessions(target=date.today(), root=tmp_path / "missing")
    assert sessions == []
    assert format_sessions(sessions, date.today()).startswith("Found 0 sessions")
