#!/usr/bin/env python3
"""
run_skill_evals.py — executes each skill's rung-2 cases file and reports a verdict per case.

A cases file lives at <skill-dir>/evals/cases.json; its shape is defined once, in
cases_schema.py, which the validator's R7.1 check reads too.

The run has two halves.

  Deterministic (default, no model, free): the file parses against the schema, trigger
  cases appear only on auto-triggerable skills, and every negative case's `owner` is
  another auto-triggerable skill that exists in the repo. Cases that only a model can
  decide are reported as `skip`, never as a pass.

  Model-in-the-loop (--with-model, opt-in, costs money): positive trigger cases pass
  when the skill ranks within `top_k` for the prompt, negative ones when the declared
  owner outranks it, and execution cases when a judge finds every expectation met.

Usage:
    python3 run_skill_evals.py <repo-root> [--skill NAME ...] [--json]
                                           [--with-model] [--model-cmd "claude -p"]

Skills are discovered under skills/, .claude/skills/ and .cursor/skills/ of the repo.
Without --skill, every discovered skill that has a cases file is run.

Exit codes: 0 = no case failed, 1 = at least one case failed, 2 = bad usage.
"""

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import audit_context as ac  # noqa: E402
import cases_schema  # noqa: E402

# Where a repo keeps skills: the Library's canonical surface plus the per-agent
# install folders a consuming repo copies skills into.
SKILL_ROOTS = ("skills", ".claude/skills", ".cursor/skills")

# One model call covers an agent reading a skill and acting on a prompt — the same unit
# of work the rung-3 harness gives 900 seconds by default.
MODEL_TIMEOUT_SECONDS = 900

RANK_PROMPT_HEAD = "Rank the skills below"
JUDGE_PROMPT_HEAD = "Grade the response below"


# ── Discovery ────────────────────────────────────────────────────────────────

def discover_skills(repo_root):
    """Every skill under the repo's skill roots, in path order."""
    found = []
    for root in SKILL_ROOTS:
        base = os.path.join(repo_root, root)
        # Skills are often installed as symlinks into an agent folder.
        for dirpath, dirnames, filenames in os.walk(base, followlinks=True):
            dirnames[:] = sorted(d for d in dirnames if d not in ac.SKIP_DIRS)
            if "SKILL.md" not in filenames:
                continue
            fm, _ = ac.parse_frontmatter(ac.read_text(os.path.join(dirpath, "SKILL.md")))
            rel = os.path.relpath(dirpath, repo_root).replace(os.sep, "/")
            found.append({
                "name": fm.get("name") or os.path.basename(dirpath),
                "dir": rel,
                "description": fm.get("description", ""),
                "command_only": cases_schema.is_command_only(fm),
            })
    return found


# ── Model-in-the-loop helpers ────────────────────────────────────────────────

def command_model(command, cwd):
    """A model callable that appends the prompt to `command` and returns its stdout."""
    argv = shlex.split(command)

    def model(prompt):
        proc = subprocess.run(argv + [prompt], cwd=cwd, capture_output=True, text=True,
                              timeout=MODEL_TIMEOUT_SECONDS)
        if proc.returncode != 0:
            raise RuntimeError(f"model command exited {proc.returncode}: {proc.stderr.strip()[-300:]}")
        return proc.stdout
    return model


def ask(model, prompt):
    """Call the model, returning (reply, error). A model failure is a case failure, not a crash."""
    try:
        return model(prompt), None
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as err:
        return "", f"model call failed: {err}"


def json_array(reply):
    """The last flat JSON array in a model reply, or None if there is not one.

    The last, because a reply that reasons before answering puts its answer at the end
    and may use square brackets in the prose before it.
    """
    for candidate in reversed(re.findall(r"\[[^\[\]]*\]", reply)):
        try:
            return json.loads(candidate)
        except ValueError:
            continue
    return None


def rank(model, prompt, skills):
    """Ask which skills should handle a prompt. Returns (names best-first, error)."""
    # Only auto-triggerable skills compete for a prompt, de-duplicated by name: the
    # same skill installed under two roots is one candidate.
    candidates = {s["name"]: s["description"] for s in skills if not s["command_only"]}
    listing = "\n".join(f"{name}: {desc}" for name, desc in sorted(candidates.items()))
    reply, err = ask(model, (
        f"{RANK_PROMPT_HEAD} by how well each one's description matches the user request. "
        "Judge from the descriptions only. Reply with a JSON array of skill names, best match "
        "first, listing only skills that plausibly apply.\n\n"
        f"Skills:\n{listing}\n\nUser request: {prompt}"
    ))
    if err:
        return None, err
    ranking = json_array(reply)
    if ranking is None:
        return None, "model reply held no JSON array of skill names"
    return ranking, None


def judge(model, skill, case):
    """Run one execution case and grade it. Returns (verdict, detail)."""
    response, err = ask(model, (
        f"Read the skill at {skill['dir']}/SKILL.md and follow it to handle this request.\n\n"
        f"Request: {case['prompt']}"
    ))
    if err:
        return "fail", err
    expectations = case["expectations"]
    reply, err = ask(model, (
        f"{JUDGE_PROMPT_HEAD} against each numbered expectation. Reply with a JSON array of "
        f"{len(expectations)} booleans, in order: true only where the response clearly meets "
        "the expectation.\n\n"
        f"Expected output: {case['expected_output']}\n\nExpectations:\n"
        + "\n".join(f"- {e}" for e in expectations)
        + f"\n\nResponse:\n{response}"
    ))
    if err:
        return "fail", err
    grades = json_array(reply)
    if grades is None or len(grades) != len(expectations):
        return "fail", "judge reply did not grade every expectation"
    unmet = [e for e, met in zip(expectations, grades) if met is not True]
    if unmet:
        return "fail", "unmet: " + "; ".join(unmet)
    return "pass", f"all {len(expectations)} expectations met"


# ── The run ──────────────────────────────────────────────────────────────────

NEEDS_MODEL = "needs --with-model"


def run_skill(repo_root, skill, skills, model, rows):
    def row(case, kind, verdict, detail):
        rows.append({"skill": skill["name"], "dir": skill["dir"], "case": case, "kind": kind,
                     "verdict": verdict, "detail": detail})

    cases_rel = f"{skill['dir']}/{cases_schema.CASES_RELPATH}"
    cases_abs = os.path.join(repo_root, cases_rel)
    if not os.path.isfile(cases_abs):
        row(cases_rel, "schema", "fail", "no cases file")
        return
    cases, problems = cases_schema.validate(ac.read_text(cases_abs), skill["command_only"], skill["name"])
    if problems:
        # Case rows from a file that fails the schema would be verdicts on a guess.
        row(cases_rel, "schema", "fail", "; ".join(problems))
        return
    row(cases_rel, "schema", "pass", "parses against the rung-2 schema")

    # An owner is a skill that could win the prompt instead: another skill, and one
    # that auto-triggers. A command-only owner can never be ranked.
    owners = {s["name"]: s["dir"] for s in skills
              if not s["command_only"] and s["name"] != skill["name"]}
    known = {s["name"] for s in skills}
    trigger = cases.get("trigger") or {}

    for i, case in enumerate(trigger.get("positive") or [], 1):
        label = f"trigger+{i}"
        if model is None:
            row(label, "trigger-positive", "skip", NEEDS_MODEL)
            continue
        ranking, err = rank(model, case["prompt"], skills)
        if err:
            row(label, "trigger-positive", "fail", err)
        elif skill["name"] in ranking[:case["top_k"]]:
            row(label, "trigger-positive", "pass", f"ranked {ranking.index(skill['name']) + 1} (top_k {case['top_k']})")
        else:
            row(label, "trigger-positive", "fail", f"not within top {case['top_k']}: {ranking}")

    for i, case in enumerate(trigger.get("negative") or [], 1):
        label, owner = f"trigger-{i}", case["owner"]
        if owner == skill["name"]:
            row(label, "trigger-negative", "fail", "owner is this skill itself")
        elif owner in known and owner not in owners:
            row(label, "trigger-negative", "fail",
                f"owner '{owner}' has disable-model-invocation: true, so it can never win a prompt")
        elif owner not in owners:
            row(label, "trigger-negative", "fail",
                f"owner '{owner}' is not a skill under {', '.join(SKILL_ROOTS)}")
        elif model is None:
            row(label, "trigger-negative", "skip", f"owner resolves to {owners[owner]}; {NEEDS_MODEL} to rank")
        else:
            ranking, err = rank(model, case["prompt"], skills)
            if err:
                row(label, "trigger-negative", "fail", err)
            elif owner in ranking and (skill["name"] not in ranking
                                       or ranking.index(owner) < ranking.index(skill["name"])):
                row(label, "trigger-negative", "pass", f"'{owner}' outranks this skill")
            else:
                row(label, "trigger-negative", "fail", f"'{owner}' does not outrank this skill: {ranking}")

    for i, case in enumerate(cases["evals"], 1):
        label = f"eval {case.get('id', i)}"
        if model is None:
            row(label, "execution", "skip", NEEDS_MODEL)
        else:
            row(label, "execution", *judge(model, skill, case))


def run(repo_root, only=None, model=None):
    """Run rung-2 cases over a repo and return the verdict rows.

    `model` is a callable (prompt) -> reply. None runs the deterministic half alone.
    `only` restricts the run to the named skills; a named skill that is missing, or
    has no cases file under any root, is a failed row rather than a silent omission.
    """
    skills = discover_skills(repo_root)
    rows = []

    def has_cases(skill):
        return os.path.isfile(os.path.join(repo_root, skill["dir"], cases_schema.CASES_RELPATH))

    if only:
        for name in only:
            matches = [s for s in skills if s["name"] == name]
            if not matches:
                rows.append({"skill": name, "dir": "-", "case": "-", "kind": "schema", "verdict": "fail",
                             "detail": f"no skill named '{name}' under {', '.join(SKILL_ROOTS)}"})
            # A copy without cases is not a failure while another copy of the same
            # skill carries them; when none does, every copy reports the missing file.
            with_cases = [s for s in matches if has_cases(s)]
            for skill in with_cases or matches:
                run_skill(repo_root, skill, skills, model, rows)
        return rows
    for skill in skills:
        if has_cases(skill):
            run_skill(repo_root, skill, skills, model, rows)
    return rows


def failed(rows):
    return any(r["verdict"] == "fail" for r in rows)


# ── Reporting ────────────────────────────────────────────────────────────────

def render_markdown(rows, with_model):
    counts = {v: sum(1 for r in rows if r["verdict"] == v) for v in ("pass", "fail", "skip")}
    half = "deterministic + model-in-the-loop" if with_model else "deterministic half only"
    o = [f"# Rung-2 evals — {half}\n",
         f"{counts['pass']} passed, {counts['fail']} failed, {counts['skip']} skipped\n",
         "| Skill | Case | Kind | Verdict | Detail |",
         "|---|---|---|---|---|"]
    for r in rows:
        detail = r["detail"].replace("|", "\\|").replace("\n", " ")
        o.append(f"| {r['dir']} | {r['case']} | {r['kind']} | {r['verdict']} | {detail} |")
    if counts["skip"]:
        o.append("\nSkipped cases need a model and were not run; a skip is not a pass. "
                 "Re-run with --with-model to decide them.")
    if not rows:
        o.append("\nNo skill with a cases file was found.")
    return "\n".join(o)


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo_root", nargs="?", default=".", help="repository whose skills to run (default: cwd)")
    ap.add_argument("--skill", action="append", metavar="NAME",
                    help="run only this skill (repeatable); default is every skill with a cases file")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    ap.add_argument("--with-model", action="store_true",
                    help="also run the model-in-the-loop half (opt-in: one or more model calls per case)")
    ap.add_argument("--model-cmd", default="claude -p",
                    help="command the prompt is appended to; its stdout is the reply (default: 'claude -p')")
    args = ap.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    if not os.path.isdir(repo_root):
        print(f"ERROR: not a directory: {repo_root}", file=sys.stderr)
        return 2

    model = None
    if args.with_model:
        argv = shlex.split(args.model_cmd)
        if not argv or not shutil.which(argv[0]):
            print(f"ERROR: --with-model needs a model command on PATH and '{args.model_cmd}' is not. "
                  "Pass --model-cmd, or drop --with-model to run the deterministic half alone.",
                  file=sys.stderr)
            return 2
        model = command_model(args.model_cmd, repo_root)

    rows = run(repo_root, only=args.skill, model=model)

    if args.json:
        print(json.dumps({"repo": repo_root, "with_model": args.with_model, "rows": rows}, indent=2))
    else:
        print(render_markdown(rows, args.with_model))
    return 1 if failed(rows) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
