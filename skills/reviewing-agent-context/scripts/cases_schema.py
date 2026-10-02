#!/usr/bin/env python3
"""
cases_schema.py — the one definition of a skill's rung-2 cases file.

Imported by both audit_context.py (rubric line R7.1) and run_skill_evals.py (the
runner), so the check that demands a cases file and the runner that executes it cannot
disagree about its shape. This module is imported, not executed.

The file lives at <skill-dir>/evals/cases.json:

    {
      "skill_name": "<name>",                  optional; must match the skill if present
      "trigger": {                             auto-triggerable skills only
        "positive": [{"prompt": "...", "top_k": 1}],
        "negative": [{"prompt": "...", "owner": "<skill that should win instead>"}]
      },
      "evals": [                               every skill
        {"id": 1, "prompt": "...", "expected_output": "...", "expectations": ["..."]}
      ]
    }

Trigger cases test which skill claims a prompt. A skill with
`disable-model-invocation: true` never competes for one, so trigger cases there test
nothing and are rejected; an auto-triggerable skill owes at least one positive and one
negative. Execution expectations are owed by every skill.
"""

import json

# Relative to the skill's own directory.
CASES_RELPATH = "evals/cases.json"


def is_command_only(frontmatter):
    """True when the skill's frontmatter opts it out of auto-triggering."""
    return str(frontmatter.get("disable-model-invocation", "")).strip().lower() == "true"


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _case_list(value, where, problems):
    """Return value as a list of objects, recording a problem for anything else."""
    if value is None:
        return []
    if not isinstance(value, list):
        problems.append(f"{where} must be an array")
        return []
    for i, case in enumerate(value, 1):
        if not isinstance(case, dict):
            problems.append(f"{where}[{i}] must be an object")
    return [c for c in value if isinstance(c, dict)]


def validate(text, command_only, skill_name=None):
    """Parse a cases file. Returns (cases, problems).

    `cases` is None when the text is not a JSON object; `problems` is empty exactly
    when the file satisfies the schema for a skill of this kind.
    """
    try:
        cases = json.loads(text)
    except ValueError as err:
        return None, [f"not valid JSON: {err}"]
    if not isinstance(cases, dict):
        return None, ["top level must be a JSON object"]

    problems = []

    declared = cases.get("skill_name")
    if declared is not None and skill_name is not None and declared != skill_name:
        problems.append(f"skill_name is '{declared}' but the file belongs to '{skill_name}'")

    trigger = cases.get("trigger")
    if trigger is not None and not isinstance(trigger, dict):
        problems.append("trigger must be an object")
        trigger = None
    positive = _case_list((trigger or {}).get("positive"), "trigger.positive", problems)
    negative = _case_list((trigger or {}).get("negative"), "trigger.negative", problems)

    for i, case in enumerate(positive, 1):
        if not _text(case.get("prompt")):
            problems.append(f"trigger.positive[{i}] has no prompt")
        top_k = case.get("top_k")
        if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
            problems.append(f"trigger.positive[{i}] needs top_k as an integer of 1 or more")
    for i, case in enumerate(negative, 1):
        if not _text(case.get("prompt")):
            problems.append(f"trigger.negative[{i}] has no prompt")
        if not _text(case.get("owner")):
            problems.append(f"trigger.negative[{i}] names no owner")

    if command_only and (positive or negative):
        problems.append("trigger cases on a skill with disable-model-invocation: true — "
                        "it never auto-triggers, so they test nothing")
    if not command_only and not (positive and negative):
        problems.append("an auto-triggerable skill needs at least one positive and one "
                        "negative trigger case")

    evals = _case_list(cases.get("evals"), "evals", problems)
    if not evals:
        problems.append("no execution expectations: evals must hold at least one case")
    seen_ids = set()
    for i, case in enumerate(evals, 1):
        for field in ("prompt", "expected_output"):
            if not _text(case.get(field)):
                problems.append(f"evals[{i}] has no {field}")
        expectations = case.get("expectations")
        if (not isinstance(expectations, list) or not expectations
                or not all(_text(e) for e in expectations)):
            problems.append(f"evals[{i}] needs expectations as a non-empty array of strings")
        if "id" in case:
            # Compared by repr so an id of any JSON type is a problem, never a crash.
            case_id = repr(case["id"])
            if case_id in seen_ids:
                problems.append(f"evals[{i}] repeats id {case_id}")
            seen_ids.add(case_id)

    return cases, problems
