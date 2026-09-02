#!/usr/bin/env python3
"""Run the sprint-digest evals against one or both arms and report the delta.

An arm is a copy of the skill. `stable` is skills/sprint-digest (what other repos
copy); `candidate` is labs/sprint-digest (what you are editing). Running both in
the same invocation is the point: a candidate is only worth promoting when it
beats stable on the same fixtures, and a single arm's score in isolation tells
you almost nothing.

Each run gets a throwaway workspace that looks like a consuming repo — the skill
under .claude/skills/, a CONTEXT.md to consult, an empty analyses/ target — plus
a .mcp.json wired to mock_jira_mcp.py. The skill therefore executes its real
step 2 against fixture data and writes a real file, which is what gets graded.

    python3 labs/evals/run_evals.py                       # both arms, all cases
    python3 labs/evals/run_evals.py --arm candidate       # iterate fast
    python3 labs/evals/run_evals.py --case core-digest --runs 1 --no-judge
    python3 labs/evals/run_evals.py --promote             # copy candidate -> stable
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import graders  # noqa: E402

HERE = Path(__file__).parent
REPO = HERE.parent.parent
ARMS = {"stable": REPO / "skills" / "sprint-digest",
        "candidate": REPO / "labs" / "sprint-digest"}
FIXTURES = HERE / "fixtures" / "sprints"
KEYS = HERE / "fixtures" / "keys"
RESULTS = HERE / "results"
JUDGE_RUBRIC = HERE / "judge-rubric.md"

ALLOWED_TOOLS = ["Read", "Write", "Edit", "Glob", "Grep", "TodoWrite",
                 "mcp__jira__jira_get_agile_boards",
                 "mcp__jira__jira_get_sprints_from_board",
                 "mcp__jira__jira_get_sprint_issues",
                 "mcp__jira__jira_get_issue"]

CONSUMING_CONTEXT = """# Acme Analytics (consuming repo)

Stakeholder language is plain English; no internal jargon in briefings.

| Term | Meaning |
| --- | --- |
| cohort retention | share of a signup cohort still subscribed at month N |
| rev-rec | revenue recognition |
| nightly | the 02:00 warehouse build |

Analyses are published to `analyses/`. Jira is read-only from this repo.
"""


# --- workspace ---------------------------------------------------------------

def build_workspace(root: Path, arm: str, sprint: str) -> Path:
    ws = root / f"{arm}-{sprint}"
    (ws / ".claude" / "skills").mkdir(parents=True)
    shutil.copytree(ARMS[arm], ws / ".claude" / "skills" / "sprint-digest")
    (ws / "analyses").mkdir()
    (ws / "CONTEXT.md").write_text(CONSUMING_CONTEXT)

    trace = ws / "mcp-trace.jsonl"
    (ws / ".mcp.json").write_text(json.dumps({
        "mcpServers": {
            "jira": {
                "command": sys.executable,
                "args": [str(HERE / "mock_jira_mcp.py")],
                "env": {"MOCK_JIRA_FIXTURES": str(FIXTURES),
                        "MOCK_JIRA_TRACE": str(trace)},
            }
        }
    }, indent=2))
    return ws


def run_agent(ws: Path, prompt: str, model: str | None, timeout: int) -> dict:
    cmd = ["claude", "-p", prompt,
           "--output-format", "json",
           "--permission-mode", "bypassPermissions",
           "--mcp-config", str(ws / ".mcp.json"),
           "--allowedTools", *ALLOWED_TOOLS]
    if model:
        cmd += ["--model", model]
    started = time.time()
    try:
        proc = subprocess.run(cmd, cwd=ws, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"timed out after {timeout}s", "seconds": timeout}
    out = {"ok": proc.returncode == 0, "seconds": round(time.time() - started, 1),
           "stderr": proc.stderr[-2000:]}
    try:
        payload = json.loads(proc.stdout)
        out["text"] = payload.get("result", "")
        out["cost_usd"] = payload.get("total_cost_usd")
        out["turns"] = payload.get("num_turns")
    except json.JSONDecodeError:
        out["text"] = proc.stdout[-4000:]
    if not out["ok"]:
        out["error"] = out.get("stderr") or "non-zero exit"
    return out


def collect(ws: Path) -> tuple[str, Path | None, list]:
    html_files = sorted((ws / "analyses").glob("*.html"))
    html = html_files[0].read_text() if html_files else ""
    trace_path = ws / "mcp-trace.jsonl"
    trace = ([json.loads(l) for l in trace_path.read_text().splitlines() if l.strip()]
             if trace_path.exists() else [])
    return html, (html_files[0] if html_files else None), trace


# --- graders that are case-shaped rather than artefact-shaped ----------------

FILENAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_[a-z0-9-]+-digest\.html$")


def grade_digest(html: str, path: Path | None, trace: list, key: dict) -> dict:
    if path is None:
        return {"score": 0.0, "hard_fail": ["no_output"],
                "results": [{"name": "no_output", "score": 0.0, "weight": 1.0,
                             "hard": True, "note": "no HTML written to analyses/"}]}
    out = graders.grade(html, trace, key)
    ok = bool(FILENAME_RE.match(path.name))
    out["results"].insert(0, {"name": "contract_filename", "score": 1.0 if ok else 0.0,
                              "weight": 1.0, "hard": False,
                              "note": ("%s" % path.name) +
                                      ("" if ok else "  <-- want YYYY-MM-DD_<slug>-digest.html")})
    w = sum(r["weight"] for r in out["results"]) or 1.0
    out["score"] = round(sum(r["score"] * r["weight"] for r in out["results"]) / w, 3)
    return out


ASK_RE = re.compile(r"\?", re.S)


def grade_clarify(reply: str, path: Path | None, trace: list) -> dict:
    results = []
    results.append({"name": "no_premature_output", "score": 0.0 if path else 1.0,
                    "weight": 2.0, "hard": bool(path),
                    "note": "wrote %s before scope was agreed" % path.name if path
                            else "no file written"})
    asked = bool(ASK_RE.search(reply))
    results.append({"name": "asks_for_scope", "score": 1.0 if asked else 0.0,
                    "weight": 2.0, "hard": not asked,
                    "note": "reply asks a question" if asked else "no question asked"})
    wants = {"board": r"board", "sprint": r"sprint", "audience": r"audience|who .*for|stakeholder",
             "language": r"language|English|русск"}
    hit = [n for n, p in wants.items() if re.search(p, reply, re.I)]
    results.append({"name": "scope_dimensions", "score": len(hit) / len(wants), "weight": 1.0,
                    "hard": False, "note": "asked about: %s" % (", ".join(hit) or "nothing")})
    queried = [c for c in trace if c["tool"] in ("jira_get_sprint_issues", "jira_get_issue")]
    results.append({"name": "no_guessed_query", "score": 0.0 if queried else 1.0,
                    "weight": 1.0, "hard": False,
                    "note": "%d issue queries before scope was set" % len(queried)
                            if queried else "did not query before asking"})
    w = sum(r["weight"] for r in results)
    return {"score": round(sum(r["score"] * r["weight"] for r in results) / w, 3),
            "hard_fail": [r["name"] for r in results if r["hard"] and r["score"] == 0.0],
            "results": results}


# --- LLM judge ---------------------------------------------------------------

def judge(html: str, key: dict, model: str) -> dict | None:
    """Narrative quality — the half the deterministic graders cannot see. They can
    prove nothing was fabricated and everything landed in the right bucket; they
    cannot tell you whether the thing reads like a story worth someone's time."""
    if not html:
        return None
    rubric = JUDGE_RUBRIC.read_text()
    prompt = (
        f"{rubric}\n\n---\n\nWhat this sprint actually contained (the answer key):\n"
        f"```json\n{json.dumps(key, indent=2)}\n```\n\n"
        f"The digest under review:\n```html\n{html[:60000]}\n```\n\n"
        "Return ONLY a JSON object, no prose around it."
    )
    proc = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json", "--model", model,
         "--disallowedTools", "Bash", "Read", "Write", "Edit", "Glob", "Grep"],
        capture_output=True, text=True, timeout=300)
    try:
        text = json.loads(proc.stdout).get("result", "")
        m = re.search(r"\{.*\}", text, re.S)
        return json.loads(m.group(0)) if m else None
    except Exception:
        return None


# --- orchestration -----------------------------------------------------------

def run_case(arm: str, case: dict, args, tmp: Path, run_idx: int) -> dict:
    ws = build_workspace(tmp, arm, f"{case['id']}-{run_idx}")
    agent = run_agent(ws, case["prompt"], args.model, args.timeout)
    html, path, trace = collect(ws)
    key = json.loads((KEYS / f"{case['sprint']}.json").read_text())

    if case["kind"] == "clarify":
        scored = grade_clarify(agent.get("text", ""), path, trace)
    else:
        scored = grade_digest(html, path, trace, key)

    if args.judge and case["kind"] == "digest" and html:
        verdict = judge(html, key, args.judge_model)
        if verdict:
            scored["judge"] = verdict
            jscore = statistics.mean(
                [v["score"] for v in verdict.get("dimensions", {}).values()]) / 5.0 \
                if verdict.get("dimensions") else None
            if jscore is not None:
                scored["judge_score"] = round(jscore, 3)
                scored["combined"] = round(0.7 * scored["score"] + 0.3 * jscore, 3)

    if args.keep_temp and path:
        dest = RESULTS / "artifacts" / f"{arm}-{case['id']}-{run_idx}.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(path, dest)

    return {"arm": arm, "case": case["id"], "run": run_idx,
            "agent_ok": agent["ok"], "error": agent.get("error"),
            "seconds": agent.get("seconds"), "cost_usd": agent.get("cost_usd"),
            "output_file": path.name if path else None,
            "mcp_calls": len(trace), "reply": agent.get("text", "")[:1500],
            **scored}


def summarise(rows: list) -> dict:
    by = {}
    for r in rows:
        by.setdefault((r["arm"], r["case"]), []).append(r)
    out = {}
    for (arm, case), rs in by.items():
        scores = [r.get("combined", r["score"]) for r in rs]
        out.setdefault(arm, {})[case] = {
            "mean": round(statistics.mean(scores), 3),
            "min": round(min(scores), 3),
            "runs": len(rs),
            "hard_fails": sorted({h for r in rs for h in r["hard_fail"]}),
            "cost_usd": round(sum(r["cost_usd"] or 0 for r in rs), 4),
        }
    return out


def print_report(rows: list, summary: dict) -> None:
    cases = sorted({r["case"] for r in rows})
    arms = [a for a in ("stable", "candidate") if a in summary]

    print("\n" + "=" * 78)
    print("SPRINT-DIGEST EVALS")
    print("=" * 78)
    head = "%-22s" % "case" + "".join("%12s" % a for a in arms)
    print(head + ("%12s" % "delta" if len(arms) == 2 else ""))
    print("-" * 78)
    for c in cases:
        line = "%-22s" % c
        for a in arms:
            line += "%12.3f" % summary[a][c]["mean"]
        if len(arms) == 2:
            d = summary["candidate"][c]["mean"] - summary["stable"][c]["mean"]
            line += "%+12.3f" % d
        print(line)
    print("-" * 78)
    line = "%-22s" % "MEAN"
    means = {}
    for a in arms:
        means[a] = statistics.mean(summary[a][c]["mean"] for c in cases)
        line += "%12.3f" % means[a]
    if len(arms) == 2:
        line += "%+12.3f" % (means["candidate"] - means["stable"])
    print(line)

    for a in arms:
        hf = {c: summary[a][c]["hard_fails"] for c in cases if summary[a][c]["hard_fails"]}
        if hf:
            print(f"\n  {a} hard failures:")
            for c, names in hf.items():
                print(f"    {c}: {', '.join(names)}")

    print("\nweakest graders (mean score across all runs):")
    agg = {}
    for r in rows:
        for g in r["results"]:
            agg.setdefault((r["arm"], g["name"]), []).append(g["score"])
    worst = sorted(((statistics.mean(v), k) for k, v in agg.items()))[:8]
    for score, (a, name) in worst:
        if score >= 0.999:
            continue
        note = next((g["note"] for r in rows if r["arm"] == a
                     for g in r["results"] if g["name"] == name), "")
        print(f"  {score:5.2f}  {a:<10} {name:<22} {note[:60]}")

    total_cost = sum(r["cost_usd"] or 0 for r in rows)
    print(f"\ncost: ${total_cost:.3f} over {len(rows)} runs")
    if len(arms) == 2:
        d = means["candidate"] - means["stable"]
        verdict = ("candidate is ahead — promote with --promote" if d > 0.02 else
                   "no meaningful difference yet" if abs(d) <= 0.02 else
                   "candidate is BEHIND stable — do not promote")
        print(f"verdict: {verdict}")
    print("=" * 78 + "\n")


def promote() -> None:
    dst = ARMS["stable"]
    shutil.rmtree(dst)
    shutil.copytree(ARMS["candidate"], dst)
    print(f"promoted labs/sprint-digest -> skills/sprint-digest")
    print("review `git diff skills/sprint-digest` before committing.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arm", choices=["stable", "candidate", "both"], default="both")
    ap.add_argument("--case", help="substring or glob over case ids")
    ap.add_argument("--tag", action="append", help="filter cases by tag")
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--model", help="model for the agent under test")
    ap.add_argument("--judge-model", default="claude-sonnet-5")
    ap.add_argument("--no-judge", dest="judge", action="store_false", default=True)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--keep-temp", action="store_true",
                    help="copy each produced digest into results/artifacts/")
    ap.add_argument("--output-dir")
    ap.add_argument("--threshold", type=float,
                    help="exit 1 if any case mean falls below this")
    ap.add_argument("--promote", action="store_true",
                    help="copy candidate over stable, then exit")
    args = ap.parse_args()

    if args.promote:
        promote()
        return 0

    if not shutil.which("claude"):
        print("error: `claude` not on PATH", file=sys.stderr)
        return 2

    spec = json.loads((HERE / "cases.json").read_text())
    cases = spec["cases"]
    if args.case:
        cases = [c for c in cases if args.case in c["id"]]
    if args.tag:
        cases = [c for c in cases if set(args.tag) & set(c.get("tags", []))]
    if not cases:
        print("no cases matched", file=sys.stderr)
        return 2

    arms = ["stable", "candidate"] if args.arm == "both" else [args.arm]
    for a in arms:
        if not ARMS[a].exists():
            print(f"error: arm {a!r} missing at {ARMS[a]}", file=sys.stderr)
            return 2

    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    outdir = Path(args.output_dir) if args.output_dir else RESULTS / stamp
    outdir.mkdir(parents=True, exist_ok=True)

    rows = []
    total = len(arms) * len(cases) * args.runs
    n = 0
    with tempfile.TemporaryDirectory(prefix="sprint-digest-evals-") as tmpdir:
        tmp = Path(tmpdir)
        for arm in arms:
            for case in cases:
                for i in range(args.runs):
                    n += 1
                    print(f"[{n}/{total}] {arm:<10} {case['id']:<20} run {i + 1}",
                          flush=True)
                    row = run_case(arm, case, args, tmp, i)
                    flag = "" if row["agent_ok"] else "  AGENT ERROR: %s" % row.get("error")
                    print(f"          score {row.get('combined', row['score']):.3f}"
                          f"  {row['mcp_calls']} mcp calls  {row.get('seconds')}s{flag}",
                          flush=True)
                    rows.append(row)

    summary = summarise(rows)
    (outdir / "runs.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False))
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2))
    print_report(rows, summary)
    print(f"full results: {outdir}")

    if args.threshold:
        worst = min(s["mean"] for arm in summary.values() for s in arm.values())
        if worst < args.threshold:
            print(f"threshold {args.threshold} not met (worst case mean {worst})")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
