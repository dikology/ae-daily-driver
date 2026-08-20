"""Discover and summarize Cursor agent transcripts for /retrospective."""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

USER_QUERY_RE = re.compile(r"<user_query>\s*(.*?)\s*</user_query>", re.DOTALL)
SKILL_NAME_RE = re.compile(r"Skill Name:\s*(\S+)")
MIN_USER_MESSAGES = 3
QUERY_PREVIEW_CHARS = 80


def projects_root() -> Path:
    override = os.environ.get("CURSOR_PROJECTS_ROOT")
    if override:
        return Path(override)
    return Path.home() / ".cursor" / "projects"


@dataclass
class SessionSummary:
    uuid: str
    slug: str
    project_name: str
    project_path: Path | None
    path: Path
    user_queries: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    mtime: datetime | None = None

    @property
    def short_id(self) -> str:
        return self.uuid[:8]


def decode_project_slug(slug: str, home: Path | None = None) -> tuple[str, Path | None]:
    """Turn a Cursor project slug into (short_name, resolved_path)."""
    if slug == "empty-window":
        return "(empty window)", None
    home = home or Path.home()
    home_slug = str(home).lstrip("/").replace("/", "-")
    if slug == home_slug:
        return home.name, home
    if not slug.startswith(home_slug + "-"):
        return slug, None

    remaining = slug[len(home_slug) + 1 :]
    current = home
    while remaining:
        if not current.exists():
            return remaining, None
        children = {p.name: p for p in current.iterdir() if p.is_dir()}
        matches = [
            name
            for name in children
            if remaining == name or remaining.startswith(name + "-")
        ]
        if not matches:
            return current.name if current != home else remaining, None
        name = max(matches, key=len)
        current = children[name]
        remaining = remaining[len(name) :].lstrip("-")
    return current.name, current


def _text_blocks(content: object) -> list[str]:
    if isinstance(content, str):
        return [content]
    if not isinstance(content, list):
        return []
    texts: list[str] = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            texts.append(block.get("text") or "")
    return texts


def extract_user_query(text: str) -> str:
    match = USER_QUERY_RE.search(text)
    if match:
        return match.group(1).strip()
    return text.strip()


def _tool_names(content: object) -> list[str]:
    if not isinstance(content, list):
        return []
    names: list[str] = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "tool_use":
            name = block.get("name")
            if name:
                names.append(name)
            inp = block.get("input") or {}
            if name == "Read" and isinstance(inp, dict):
                path = str(inp.get("path") or "")
                if "/skills/" in path and path.endswith("SKILL.md"):
                    skill = Path(path).parent.name
                    names.append(f"skill:{skill}")
    return names


def _skills_from_text(text: str) -> list[str]:
    return SKILL_NAME_RE.findall(text)


def parse_transcript(path: Path, home: Path | None = None) -> SessionSummary:
    slug = path.parts[-4] if len(path.parts) >= 4 else path.parent.parent.name
    uuid = path.stem
    project_name, project_path = decode_project_slug(slug, home=home)
    summary = SessionSummary(
        uuid=uuid,
        slug=slug,
        project_name=project_name,
        project_path=project_path,
        path=path,
        mtime=datetime.fromtimestamp(path.stat().st_mtime),
    )

    tools: list[str] = []
    skills: list[str] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") == "turn_ended":
                continue
            role = obj.get("role")
            content = (obj.get("message") or {}).get("content")
            if role == "user":
                for text in _text_blocks(content):
                    query = extract_user_query(text)
                    if query:
                        summary.user_queries.append(query)
                    skills.extend(_skills_from_text(text))
            elif role == "assistant":
                for name in _tool_names(content):
                    if name.startswith("skill:"):
                        skills.append(name.split(":", 1)[1])
                    else:
                        tools.append(name)

    # unique, stable order
    seen_tools: list[str] = []
    for t in tools:
        if t not in seen_tools:
            seen_tools.append(t)
    seen_skills: list[str] = []
    for s in skills:
        if s not in seen_skills:
            seen_skills.append(s)
    summary.tools = seen_tools
    summary.skills = seen_skills
    return summary


def iter_transcript_paths(root: Path | None = None) -> list[Path]:
    root = root or projects_root()
    if not root.exists():
        return []
    paths: list[Path] = []
    for jsonl in root.glob("*/agent-transcripts/*/*.jsonl"):
        if "subagents" in jsonl.parts:
            continue
        paths.append(jsonl)
    return paths


def _on_date(mtime: datetime | None, target: date) -> bool:
    if mtime is None:
        return False
    return mtime.date() == target


def discover_sessions(
    target: date | None = None,
    min_user_messages: int = MIN_USER_MESSAGES,
    root: Path | None = None,
    home: Path | None = None,
) -> list[SessionSummary]:
    target = target or date.today()
    sessions: list[SessionSummary] = []
    for path in iter_transcript_paths(root):
        mtime = datetime.fromtimestamp(path.stat().st_mtime)
        if not _on_date(mtime, target):
            continue
        summary = parse_transcript(path, home=home)
        if len(summary.user_queries) < min_user_messages:
            continue
        sessions.append(summary)
    sessions.sort(key=lambda s: s.mtime or datetime.min, reverse=True)
    return sessions


def _preview(text: str) -> str:
    first = text.splitlines()[0].strip()
    if len(first) <= QUERY_PREVIEW_CHARS:
        return first
    return first[: QUERY_PREVIEW_CHARS - 1] + "…"


def format_sessions(sessions: list[SessionSummary], target: date) -> str:
    if not sessions:
        return f"Found 0 sessions on {target.isoformat()}."
    lines = [f"Found {len(sessions)} sessions on {target.isoformat()}:"]
    for s in sessions:
        q = _preview(s.user_queries[0]) if s.user_queries else "(no user query)"
        lines.append(f"- {s.project_name} ({s.short_id}) — \"{q}\"")
        extra: list[str] = [f"  uuid: {s.uuid}", f"  path: {s.path}"]
        if s.project_path:
            extra.append(f"  project: {s.project_path}")
        extra.append(f"  user_messages: {len(s.user_queries)}")
        if s.tools:
            extra.append(f"  tools: {', '.join(s.tools[:12])}")
        if s.skills:
            extra.append(f"  skills: {', '.join(s.skills)}")
        queries = s.user_queries[:10]
        if len(s.user_queries) > 10:
            tail = s.user_queries[-5:]
            # avoid duplicating if overlap
            seen = set(queries)
            queries = queries + [q for q in tail if q not in seen]
        extra.append("  queries:")
        for q in queries:
            extra.append(f"    - {_preview(q)}")
        lines.extend(extra)
    return "\n".join(lines) + "\n"


def _parse_date(value: str) -> date:
    today = date.today()
    if value == "today":
        return today
    if value == "yesterday":
        return today - timedelta(days=1)
    return date.fromisoformat(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize Cursor agent transcripts.")
    parser.add_argument("--date", default="today", help="today | yesterday | YYYY-MM-DD")
    parser.add_argument(
        "--min-user-messages",
        type=int,
        default=MIN_USER_MESSAGES,
        help="Skip sessions with fewer user messages (default: 3)",
    )
    args = parser.parse_args(argv)
    target = _parse_date(args.date)
    sessions = discover_sessions(target=target, min_user_messages=args.min_user_messages)
    print(format_sessions(sessions, target), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
