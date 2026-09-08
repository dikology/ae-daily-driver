#!/usr/bin/env python3
"""
audit_context.py — the deterministic half of a `reviewing-agent-context` audit.

Walks a repository's agent-facing context, classifies every artifact into a load
tier, measures its token cost, and checks it against the machine-decidable lines of
references/rubric.md (R1.1, R2.1, R2.3, R2.4, R3.4, R4.1-R4.5, R7.1, R8.1, R8.6, and
near-duplicate detection for R8.2).

Everything it reports is a measurement or a resolved path. Judgment findings are the
agent's job, not this script's.

Usage:
    python3 audit_context.py <repo-root> [--json] [--fail-on {error,warn,never}]
                                         [--scope {repo,canonical}]
    python3 audit_context.py --locate-context-engineering

--scope canonical restricts findings to skills/ and .claude/skills/, declaring
everything outside it in the report rather than dropping it silently.

Exit codes: 0 = clean at the chosen threshold, 1 = findings at or above it, 2 = bad usage.
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict

# ── Constants ────────────────────────────────────────────────────────────────
#
# Every threshold here is either quoted from Anthropic's authoring guide or derived
# from a stated measurement rule. None are tuned by taste.

# Anthropic: "Keep SKILL.md body under 500 lines for optimal performance."
SKILL_BODY_MAX_LINES = 500
# Warn one fifth below the hard limit, so a skill is flagged while a split is still
# cheap rather than on the commit that breaks it.
SKILL_BODY_WARN_LINES = 400

# Anthropic frontmatter validation rules.
NAME_MAX_CHARS = 64
DESCRIPTION_MAX_CHARS = 1024
NAME_PATTERN = re.compile(r"^[a-z0-9-]+$")
RESERVED_NAME_WORDS = ("anthropic", "claude")

# Anthropic: "For reference files longer than 100 lines, include a table of contents."
REFERENCE_TOC_THRESHOLD_LINES = 100

# English text averages close to four characters per BPE token. Used for relative
# comparison between artifacts, not for billing.
CHARS_PER_TOKEN = 4

# A duplicated run of this many words is long enough that two files are stating the
# same rule, and short enough to catch a paraphrased sentence. Shorter runs match
# ordinary shared phrasing ("see the table below") and produce noise.
DUPLICATE_SHINGLE_WORDS = 12

# Root instruction files, by the convention of each agent tool. Loaded on every request.
ALWAYS_LOADED_FILENAMES = {
    "CLAUDE.md", "AGENTS.md", "GEMINI.md", ".cursorrules", ".windsurfrules",
}
ALWAYS_LOADED_PATHS = {
    ".github/copilot-instructions.md",
}

MCP_CONFIG_NAMES = {"mcp.json", ".mcp.json", "mcp_servers.json", "claude_desktop_config.json"}

GENERATED_SUFFIXES = (".excalidraw", ".png", ".svg", ".jpg", ".jpeg", ".pdf", ".lock")
SCRIPT_SUFFIXES = (".py", ".js", ".ts", ".sh", ".rb")
DATA_SUFFIXES = (".json", ".yaml", ".yml", ".toml")

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".pytest_cache"}

# Path prefixes `--scope canonical` restricts findings to: the skills a Library owns
# and distributes. Files outside are still walked and counted (render_markdown
# declares them), just not checked. The default `repo` scope checks everything — a
# consuming repo whose skills live in `.cursor/skills/` wants that, not this.
CANONICAL_SURFACE = ("skills/", ".claude/skills/")

# Data under these directory names is read by a skill's own scripts, not loaded into
# an agent's context, so it belongs in the on-exec tier rather than the task tier.
TEST_DATA_DIRS = {"scenarios", "fixtures", "testdata", "test-files", "__fixtures__"}

# Statements that date the content. R8.1.
TIME_SENSITIVE_PATTERNS = [
    (re.compile(r"\bcoming soon\b", re.I), "coming soon"),
    (re.compile(r"\bas of (january|february|march|april|may|june|july|august|september|october|november|december|q[1-4]|20\d\d)", re.I), "as-of date"),
    (re.compile(r"\b(currently|for now|at the moment),", re.I), "temporal hedge"),
    (re.compile(r"\b(will be|to be) (added|shipped|imported|populated|built)\b", re.I), "future-tense promise"),
    (re.compile(r"\b(deprecated|removed) in 20\d\d\b", re.I), "bare version date"),
]

# Descriptions must be third person. R2.4.
POV_PATTERNS = [
    (re.compile(r"\b(I|I'll|I can|I will)\b"), "first person"),
    (re.compile(r"\byou can use this\b", re.I), "second person"),
    (re.compile(r"^\s*(use me|helps you)\b", re.I), "second person"),
]

MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
BACKTICK_PATH = re.compile(r"`([A-Za-z0-9_./-]+)`")
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n{2,}")


# ── Small helpers ────────────────────────────────────────────────────────────

def est_tokens(text):
    return len(text) // CHARS_PER_TOKEN


def read_text(path):
    """Read a file as text, returning '' for anything undecodable rather than raising."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except (UnicodeDecodeError, OSError):
        return ""


def parse_frontmatter(text):
    """Return (frontmatter_dict, body_text). Missing frontmatter yields ({}, text).

    Deliberately a flat scalar parser: SKILL.md frontmatter is name/description plus a
    few booleans, and depending on PyYAML would make this script unrunnable where it is
    not installed.
    """
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end]
    body = text[end + 4:].lstrip("\n")

    fields, key, buf = {}, None, []
    for line in raw.splitlines():
        m = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if m:
            if key:
                fields[key] = " ".join(buf).strip()
            key, rest = m.group(1), m.group(2).strip()
            buf = [] if rest in (">-", ">", "|", "|-", "") else [rest]
        elif key is not None and line.strip():
            buf.append(line.strip().lstrip("- "))
    if key:
        fields[key] = " ".join(buf).strip()
    return fields, body


def normalize_words(text):
    """Lowercase word stream with markdown punctuation and links stripped."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[`*_#|>\-]", " ", text)
    return re.findall(r"[a-z0-9']+", text.lower())


# ── Locating the context-engineering skill ───────────────────────────────────

def locate_context_engineering(repo_root):
    """Search the usual skill roots for the context-engineering SKILL.md."""
    home = os.path.expanduser("~")
    roots = [
        os.path.join(repo_root, "skills"),
        os.path.join(repo_root, ".claude", "skills"),
        os.path.join(repo_root, ".cursor", "skills"),
        os.path.join(home, ".claude", "skills"),
        os.path.join(home, ".claude", "plugins"),
        os.path.join(home, ".cursor", "skills"),
    ]
    hits = []
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            if os.path.basename(dirpath) == "context-engineering" and "SKILL.md" in filenames:
                hits.append(os.path.join(dirpath, "SKILL.md"))
    return hits


# ── Inventory ────────────────────────────────────────────────────────────────

def classify(rel_path, repo_root):
    """Return (kind, load_tier) for one file.

    Tiers: always | task | path | query | on-exec | none.
    'none' means nothing loads the file into an agent's context.
    """
    name = os.path.basename(rel_path)
    parts = rel_path.split("/")

    if name in ALWAYS_LOADED_FILENAMES or rel_path in ALWAYS_LOADED_PATHS:
        return "instruction file", "always"

    if name.endswith(".mdc") and "rules" in parts:
        fm, _ = parse_frontmatter(read_text(os.path.join(repo_root, rel_path)))
        always = str(fm.get("alwaysApply", "")).lower() == "true"
        return "scoped rule", "always" if always else "path"

    if name == "SKILL.md":
        return "skill", "task"

    in_skill_dir = any(p in ("skills", ".claude", ".cursor") for p in parts[:-1])

    if name in MCP_CONFIG_NAMES or parts[0] == "mcp":
        return "tool/MCP config", "query"

    if name.endswith(SCRIPT_SUFFIXES):
        return "script", "on-exec" if in_skill_dir else "none"

    if name.endswith(GENERATED_SUFFIXES):
        return "generated artifact", "none"

    if name.endswith(DATA_SUFFIXES):
        if not in_skill_dir:
            return "data", "none"
        if TEST_DATA_DIRS & set(parts[:-1]):
            return "skill test data", "on-exec"
        return "skill data", "task"

    if name.endswith(".md"):
        if in_skill_dir:
            return "reference", "task"
        if parts[0] == "docs":
            return "doc", "task"
        return "doc", "none"

    return "other", "none"


def on_canonical_surface(rel_path):
    return any(rel_path == p.rstrip("/") or rel_path.startswith(p) for p in CANONICAL_SURFACE)


def group_excluded(items):
    """{top-level dir: count} for every out-of-scope file. Repo-root files key on ''."""
    groups = defaultdict(int)
    for e in items:
        if e["in_scope"]:
            continue
        groups[e["path"].split("/")[0] if "/" in e["path"] else ""] += 1
    return dict(groups)


def build_inventory(repo_root, scope="repo"):
    items = []
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            abs_path = os.path.join(dirpath, fn)
            rel = os.path.relpath(abs_path, repo_root).replace(os.sep, "/")
            if rel.startswith(".git/"):
                continue
            text = read_text(abs_path)
            kind, tier = classify(rel, repo_root)
            entry = {
                "path": rel,
                "kind": kind,
                "tier": tier,
                "in_scope": scope != "canonical" or on_canonical_surface(rel),
                "lines": text.count("\n") + 1 if text else 0,
                "tokens": est_tokens(text),
            }
            if kind == "skill":
                fm, body = parse_frontmatter(text)
                entry["name"] = fm.get("name", "")
                entry["description"] = fm.get("description", "")
                # The description ships in the system prompt whether or not the body
                # is ever read, so it is an always-tier cost.
                entry["always_tokens"] = est_tokens(entry["description"])
                entry["body_lines"] = body.count("\n") + 1 if body else 0
            elif tier == "always":
                entry["always_tokens"] = entry["tokens"]
            items.append(entry)
    return items


# ── Checks ───────────────────────────────────────────────────────────────────

class Findings:
    def __init__(self):
        self.rows = []

    def add(self, severity, rule, path, message, line=None):
        self.rows.append({
            "severity": severity, "rule": rule, "path": path,
            "line": line, "message": message,
        })

    def by_severity(self, severity):
        return [r for r in self.rows if r["severity"] == severity]


def check_frontmatter(entry, out):
    path, name, desc = entry["path"], entry.get("name", ""), entry.get("description", "")

    if not name:
        out.add("error", "R2.1", path, "SKILL.md has no `name` in frontmatter")
    else:
        if len(name) > NAME_MAX_CHARS:
            out.add("error", "R2.1", path, f"name is {len(name)} chars (max {NAME_MAX_CHARS})")
        if not NAME_PATTERN.match(name):
            out.add("error", "R2.1", path, f"name '{name}' must be lowercase letters, numbers, hyphens only")
        for word in RESERVED_NAME_WORDS:
            if word in name.lower():
                out.add("error", "R2.1", path, f"name contains reserved word '{word}'")

    if not desc:
        out.add("error", "R2.3", path, "SKILL.md has no `description` in frontmatter")
        return
    if len(desc) > DESCRIPTION_MAX_CHARS:
        out.add("error", "R2.3", path, f"description is {len(desc)} chars (max {DESCRIPTION_MAX_CHARS})")
    for pattern, label in POV_PATTERNS:
        if pattern.search(desc):
            out.add("error", "R2.4", path, f"description is not third person ({label})")
            break
    if not re.search(r"\buse (when|this|it)\b|\btrigger(s|ing)? on\b", desc, re.I):
        out.add("warn", "R2.5", path, "description states what the skill does but no explicit trigger condition")


def check_body_size(entry, out):
    lines = entry.get("body_lines", 0)
    if lines > SKILL_BODY_MAX_LINES:
        out.add("error", "R1.1", entry["path"], f"body is {lines} lines (limit {SKILL_BODY_MAX_LINES})")
    elif lines > SKILL_BODY_WARN_LINES:
        out.add("warn", "R1.1", entry["path"], f"body is {lines} lines, approaching the {SKILL_BODY_MAX_LINES}-line limit")


def check_links(repo_root, items, out):
    """R4.1-R4.3, R4.5 and R3.4: link resolution, reference depth, orphaned bundles."""
    md_paths = [e["path"] for e in items if e["path"].endswith((".md", ".mdc"))]
    links = defaultdict(list)   # source rel path -> [(target rel path or None, raw, line)]

    for rel in md_paths:
        text = read_text(os.path.join(repo_root, rel))
        for lineno, line in enumerate(text.splitlines(), 1):
            for raw in MD_LINK.findall(line):
                if raw.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                # A single bare word with no separator and no extension is a
                # placeholder in a citation-format example, not a file link.
                if "/" not in raw and "." not in raw:
                    continue
                if re.search(r"[{}<>*]", raw):
                    continue
                if "\\" in raw:
                    out.add("error", "R4.5", rel, f"link uses backslashes: {raw}", lineno)
                target = raw.split("#")[0]
                if not target:
                    continue
                resolved = os.path.normpath(os.path.join(os.path.dirname(rel), target))
                exists = os.path.exists(os.path.join(repo_root, resolved))
                if not exists:
                    out.add("error", "R4.3", rel, f"link does not resolve: {raw} -> {resolved}", lineno)
                links[rel].append((resolved if exists else None, raw, lineno))

    # R4.2 — a reference that is itself linked from a SKILL.md must not link onward
    # to another local markdown file.
    for skill_rel in [e["path"] for e in items if e["kind"] == "skill"]:
        first_level = {t for t, _, _ in links.get(skill_rel, []) if t and t.endswith(".md")}
        for ref in sorted(first_level):
            for target, raw, lineno in links.get(ref, []):
                if target and target.endswith(".md") and target != skill_rel:
                    out.add("error", "R4.2", ref, f"reference chains one level deeper: {raw} (link it from {skill_rel} instead)", lineno)

    # R3.4 — bundled markdown a skill never links to.
    for entry in items:
        if entry["kind"] != "skill":
            continue
        skill_dir = os.path.dirname(entry["path"])
        reachable = {t for t, _, _ in links.get(entry["path"], []) if t}
        for other in items:
            p = other["path"]
            if not p.startswith(skill_dir + "/") or not p.endswith(".md") or p == entry["path"]:
                continue
            if p not in reachable:
                out.add("warn", "R3.4", p, f"bundled file is never linked from {entry['path']}")

    return links


def check_reference_tocs(repo_root, items, links, out):
    """R4.4 — reference files over the threshold open with a table of contents."""
    referenced = set()
    for entry in items:
        if entry["kind"] == "skill":
            referenced |= {t for t, _, _ in links.get(entry["path"], []) if t and t.endswith(".md")}
    for rel in sorted(referenced):
        text = read_text(os.path.join(repo_root, rel))
        nlines = text.count("\n") + 1
        if nlines <= REFERENCE_TOC_THRESHOLD_LINES:
            continue
        head = "\n".join(text.splitlines()[:30]).lower()
        if not re.search(r"^#{1,3}\s+(contents|table of contents)", head, re.M):
            out.add("warn", "R4.4", rel, f"reference is {nlines} lines but has no table of contents")


def check_time_sensitive(repo_root, items, out):
    for entry in items:
        if entry["tier"] in ("none", "on-exec") or not entry["path"].endswith((".md", ".mdc")):
            continue
        for lineno, line in enumerate(read_text(os.path.join(repo_root, entry["path"])).splitlines(), 1):
            # A phrase inside quotes or backticks is being named as an example
            # (as this repo's own rubric does), not asserted as fact.
            probe = re.sub(r"`[^`]*`|\"[^\"]*\"|\u201c[^\u201d]*\u201d", " ", line)
            for pattern, label in TIME_SENSITIVE_PATTERNS:
                if pattern.search(probe):
                    out.add("warn", "R8.1", entry["path"], f"time-sensitive statement ({label}): {line.strip()[:90]}", lineno)
                    break


def check_path_claims(repo_root, items, out):
    """R8.6 — backticked repo-shaped paths that do not resolve.

    Reported as warnings, not errors: a skill meant to run in a consuming repo will
    legitimately name paths that exist only there. The agent decides which is which.
    """
    for entry in items:
        if not entry["path"].endswith((".md", ".mdc")) or entry["tier"] == "none":
            continue
        text = read_text(os.path.join(repo_root, entry["path"]))
        seen = set()
        for lineno, line in enumerate(text.splitlines(), 1):
            for claim in BACKTICK_PATH.findall(line):
                if "/" not in claim or claim.startswith(("http", "-")) or claim in seen:
                    continue
                if not (re.search(r"\.[a-z]{2,5}$", claim) or claim.endswith("/")):
                    continue
                seen.add(claim)
                candidates = [claim, claim.rstrip("/")]
                if any(os.path.exists(os.path.join(repo_root, c)) for c in candidates):
                    continue
                # Also accept a path relative to the file's own directory, or to
                # the root of the skill that bundles it (skills document their
                # own scripts and references from the skill root).
                bases = [os.path.dirname(entry["path"])]
                skill_root = nearest_skill_root(repo_root, entry["path"])
                if skill_root is not None:
                    bases.append(skill_root)
                if any(os.path.exists(os.path.join(repo_root, os.path.normpath(os.path.join(b, claim))))
                       for b in bases):
                    continue
                out.add("warn", "R8.6", entry["path"], f"path claim does not resolve in this repo: {claim}", lineno)


def nearest_skill_root(repo_root, rel_path):
    """Directory of the SKILL.md that bundles rel_path, or None if it is not in a skill."""
    d = os.path.dirname(rel_path)
    while d:
        if os.path.exists(os.path.join(repo_root, d, "SKILL.md")):
            return d
        d = os.path.dirname(d)
    return None


def check_evals(repo_root, items, out):
    """R7.1 — every skill has evaluations somewhere its own directory can reach."""
    for entry in items:
        if entry["kind"] != "skill":
            continue
        skill_dir = os.path.join(repo_root, os.path.dirname(entry["path"]))
        skill_name = os.path.basename(os.path.dirname(entry["path"]))
        local = any(
            os.path.exists(os.path.join(skill_dir, c))
            for c in ("evals", "evals.json", "evals/cases.json", "scenarios")
        )
        shared = os.path.exists(os.path.join(repo_root, "evals", "cases", skill_name + ".json"))
        if not (local or shared):
            out.add("warn", "R7.1", entry["path"], "no evaluations found for this skill")


def check_duplicates(repo_root, items, out):
    """R8.2 — the same long run of words appearing in two agent-loaded files."""
    index = defaultdict(set)
    for entry in items:
        if entry["tier"] in ("none", "on-exec") or not entry["path"].endswith((".md", ".mdc")):
            continue
        for sentence in SENTENCE_SPLIT.split(read_text(os.path.join(repo_root, entry["path"]))):
            words = normalize_words(sentence)
            for i in range(len(words) - DUPLICATE_SHINGLE_WORDS + 1):
                shingle = " ".join(words[i:i + DUPLICATE_SHINGLE_WORDS])
                index[shingle].add(entry["path"])

    reported = set()
    for shingle, paths in sorted(index.items()):
        if len(paths) < 2:
            continue
        key = tuple(sorted(paths))
        if key in reported:
            continue
        reported.add(key)
        out.add("warn", "R8.2", key[0],
                f"shared passage with {', '.join(key[1:])}: \"{shingle[:70]}…\"")


# ── Reporting ────────────────────────────────────────────────────────────────

def tier_totals(items):
    totals = defaultdict(lambda: {"tokens": 0, "files": 0})
    always = 0
    for e in items:
        if e["tier"] == "none" or not e["in_scope"]:
            continue
        totals[e["tier"]]["tokens"] += e["tokens"]
        totals[e["tier"]]["files"] += 1
        always += e.get("always_tokens", 0)
    return dict(totals), always


def render_markdown(repo_root, items, findings, always_tokens, totals, ce_paths):
    o = []
    o.append(f"# Context audit — {os.path.basename(os.path.abspath(repo_root))}\n")
    o.append(f"context-engineering skill: {ce_paths[0] if ce_paths else 'NOT FOUND — rubric-only audit'}\n")

    excluded = group_excluded(items)
    if excluded:
        skipped = sum(excluded.values())
        o.append("\n## Scope\n")
        o.append("Audited: the canonical surface — `" + "`, `".join(CANONICAL_SURFACE) + "`.\n")
        o.append(f"\n**Declared exclusions** — {skipped} file(s) outside the canonical surface "
                 "were not audited (checked-and-clean is not claimed for them):\n")
        o.append("| Directory | Files skipped |")
        o.append("|---|---:|")
        for key in sorted(excluded):
            label = f"`{key}/`" if key else "repo root"
            o.append(f"| {label} | {excluded[key]} |")

    o.append("\n## Load map\n")
    o.append("| Tier | Files | Est. tokens |")
    o.append("|---|---:|---:|")
    for tier in ("always", "task", "path", "query", "on-exec"):
        if tier in totals:
            o.append(f"| {tier} | {totals[tier]['files']} | {totals[tier]['tokens']:,} |")
    o.append(f"\n**Always-tier budget: ~{always_tokens:,} tokens** "
             "(root instruction files + always-apply rules + every skill's frontmatter description).\n")

    unloaded = [e for e in items if e["tier"] == "none" and e["tokens"] > 0 and e["in_scope"]]
    if unloaded:
        o.append(f"\n{len(unloaded)} file(s) in no load tier — nothing puts them in an agent's context.\n")

    o.append("\n## Inventory (agent-loaded)\n")
    o.append("| Path | Kind | Tier | Lines | Est. tokens |")
    o.append("|---|---|---|---:|---:|")
    for e in sorted((e for e in items if e["tier"] != "none" and e["in_scope"]), key=lambda x: -x["tokens"]):
        o.append(f"| `{e['path']}` | {e['kind']} | {e['tier']} | {e['lines']} | {e['tokens']:,} |")

    errors, warns = findings.by_severity("error"), findings.by_severity("warn")
    o.append(f"\n## Rubric findings — {len(errors)} error(s), {len(warns)} warning(s)\n")
    for label, rows in (("Errors", errors), ("Warnings", warns)):
        if not rows:
            continue
        o.append(f"\n### {label}\n")
        o.append("| Rule | Location | Finding |")
        o.append("|---|---|---|")
        for r in sorted(rows, key=lambda x: (x["rule"], x["path"], x["line"] or 0)):
            loc = f"`{r['path']}`" + (f":{r['line']}" if r["line"] else "")
            o.append(f"| {r['rule']} | {loc} | {r['message']} |")

    o.append("\n---\nJudgment findings (R1.2-R1.4, R2.2, R2.5-R2.6, R3.1-R3.3, R5, R6.2-R6.5, "
             "R7.2-R7.4, R8.3-R8.5) are not checked here — see references/rubric.md.\n")
    return "\n".join(o)


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo_root", nargs="?", default=".", help="repository to audit (default: cwd)")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    ap.add_argument("--fail-on", choices=("error", "warn", "never"), default="error",
                    help="exit 1 at this severity or above (default: error)")
    ap.add_argument("--scope", choices=("repo", "canonical"), default="repo",
                    help="'canonical' restricts findings to the canonical surface (%s); files "
                         "outside it are still counted and named in the report as a declared "
                         "exclusion. Default 'repo' audits the whole tree."
                         % ", ".join(CANONICAL_SURFACE))
    ap.add_argument("--locate-context-engineering", action="store_true",
                    help="print where the context-engineering skill is installed, then exit")
    args = ap.parse_args()

    repo_root = os.path.abspath(args.repo_root)

    if args.locate_context_engineering:
        hits = locate_context_engineering(repo_root)
        if hits:
            for h in hits:
                print(h)
            return 0
        print("context-engineering skill not found. Install it, or note its absence in the "
              "report header and continue with the rubric half of the audit:\n"
              "  git clone --depth 1 https://github.com/addyosmani/agent-skills", file=sys.stderr)
        return 1

    if not os.path.isdir(repo_root):
        print(f"ERROR: not a directory: {repo_root}", file=sys.stderr)
        return 2

    items = build_inventory(repo_root, scope=args.scope)
    findings = Findings()

    # Checks run over the in-scope items only; `items` keeps the excluded files so
    # the report can declare them (see group_excluded / render_markdown).
    scoped = [e for e in items if e["in_scope"]]

    for entry in scoped:
        if entry["kind"] == "skill":
            check_frontmatter(entry, findings)
            check_body_size(entry, findings)

    links = check_links(repo_root, scoped, findings)
    check_reference_tocs(repo_root, scoped, links, findings)
    check_time_sensitive(repo_root, scoped, findings)
    check_path_claims(repo_root, scoped, findings)
    check_evals(repo_root, scoped, findings)
    check_duplicates(repo_root, scoped, findings)

    totals, always_tokens = tier_totals(items)
    ce_paths = locate_context_engineering(repo_root)

    if args.json:
        print(json.dumps({
            "repo": repo_root,
            "scope": args.scope,
            "context_engineering_skill": ce_paths,
            "always_tier_tokens": always_tokens,
            "tier_totals": totals,
            "declared_exclusions": group_excluded(items),
            "inventory": items,
            "findings": findings.rows,
        }, indent=2))
    else:
        print(render_markdown(repo_root, items, findings, always_tokens, totals, ce_paths))

    if args.fail_on == "never":
        return 0
    if args.fail_on == "warn":
        return 1 if findings.rows else 0
    return 1 if findings.by_severity("error") else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
