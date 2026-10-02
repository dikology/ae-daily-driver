#!/usr/bin/env python3
"""
Tests for run_skill_evals.py. Each test builds a throwaway skills tree on disk, runs
the runner over it, and asserts on the verdict rows it emits — so the tests survive a
refactor that leaves the runner's behaviour unchanged.

No test here spawns a model: the model-in-the-loop half is exercised through an
injected fake.

Run: python3 scripts/test_run_skill_evals.py
"""

import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import run_skill_evals as rse  # noqa: E402


def skill(name, command_only=False, desc="Does a thing. Use when the user asks for a thing."):
    flag = "disable-model-invocation: true\n" if command_only else ""
    return f"---\nname: {name}\ndescription: {desc}\n{flag}---\n\n# {name}\n"


def execution(n=1):
    return [{"id": i, "prompt": f"do thing {i}", "expected_output": "a thing",
             "expectations": ["the thing is done", "nothing else is touched"]}
            for i in range(1, n + 1)]


def cases(positive=(), negative=(), evals=None):
    doc = {"evals": execution() if evals is None else evals}
    if positive or negative:
        doc["trigger"] = {"positive": list(positive), "negative": list(negative)}
    return json.dumps(doc)


POS = {"prompt": "do the thing", "top_k": 1}


def build(root, files):
    for rel, content in files.items():
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)


def run(files, model=None, only=None):
    with tempfile.TemporaryDirectory() as root:
        build(root, files)
        return rse.run(root, only=only, model=model)


def cli(files, *args):
    """Run the runner as a command over a temporary repo, returning (exit code, stdout, stderr)."""
    with tempfile.TemporaryDirectory() as root:
        build(root, files)
        proc = subprocess.run([sys.executable, rse.__file__, root, *args], capture_output=True, text=True)
        return proc.returncode, proc.stdout, proc.stderr


def verdicts(rows, kind=None):
    return [r["verdict"] for r in rows if kind is None or r["kind"] == kind]


def tree(cases_text, command_only=False, extra=None):
    files = {
        "skills/demo/SKILL.md": skill("demo", command_only=command_only),
        "skills/demo/evals/cases.json": cases_text,
        "skills/sibling/SKILL.md": skill("sibling", desc="Does another thing. Use when asked for it."),
    }
    files.update(extra or {})
    return files


TESTS = []


def test(fn):
    TESTS.append(fn)
    return fn


@test
def a_valid_cases_file_yields_one_row_per_case():
    rows = run(tree(cases(positive=[POS], negative=[{"prompt": "other thing", "owner": "sibling"}],
                          evals=execution(2))))
    assert verdicts(rows, "schema") == ["pass"], rows
    assert len(verdicts(rows, "trigger-positive")) == 1
    assert len(verdicts(rows, "trigger-negative")) == 1
    assert len(verdicts(rows, "execution")) == 2
    assert all(r["skill"] == "demo" for r in rows), "a skill without a cases file emits no rows"
    assert not rse.failed(rows), rows


@test
def a_file_that_does_not_parse_fails_and_emits_no_case_rows():
    rows = run(tree("{ not json"))
    assert verdicts(rows) == ["fail"], rows
    assert rows[0]["kind"] == "schema"
    assert rse.failed(rows)


@test
def a_cases_file_missing_execution_expectations_fails_schema():
    rows = run(tree(cases(positive=[POS], negative=[{"prompt": "x", "owner": "sibling"}], evals=[])))
    assert verdicts(rows, "schema") == ["fail"], rows
    no_expectations = [{"prompt": "p", "expected_output": "o", "expectations": []}]
    rows = run(tree(cases(evals=no_expectations), command_only=True))
    assert verdicts(rows, "schema") == ["fail"], rows


@test
def trigger_cases_on_a_command_only_skill_fail():
    rows = run(tree(cases(positive=[POS]), command_only=True))
    assert verdicts(rows, "schema") == ["fail"], rows
    assert "disable-model-invocation" in rows[0]["detail"]


@test
def a_command_only_skill_needs_no_trigger_cases():
    rows = run(tree(cases(), command_only=True))
    assert verdicts(rows, "schema") == ["pass"], rows
    assert not rse.failed(rows)


@test
def an_auto_triggerable_skill_without_trigger_cases_fails():
    rows = run(tree(cases()))
    assert verdicts(rows, "schema") == ["fail"], rows


@test
def a_negative_case_naming_an_owner_that_does_not_exist_fails():
    rows = run(tree(cases(positive=[POS], negative=[
        {"prompt": "other thing", "owner": "sibling"},
        {"prompt": "third thing", "owner": "nobody-home"},
    ])))
    assert verdicts(rows, "schema") == ["pass"], "an unknown owner is a case failure, not a parse failure"
    assert verdicts(rows, "trigger-negative") == ["skip", "fail"], rows
    assert "nobody-home" in [r for r in rows if r["verdict"] == "fail"][0]["detail"]
    assert rse.failed(rows)


@test
def an_owner_resolves_in_any_skill_root_of_the_repo():
    rows = run(tree(
        cases(positive=[POS], negative=[{"prompt": "other thing", "owner": "installed"}]),
        extra={".claude/skills/installed/SKILL.md": skill("installed")},
    ))
    assert verdicts(rows, "trigger-negative") == ["skip"], rows


@test
def an_owner_must_be_another_skill_that_can_auto_trigger():
    itself = run(tree(cases(positive=[POS], negative=[{"prompt": "x", "owner": "demo"}])))
    assert verdicts(itself, "trigger-negative") == ["fail"], itself
    command_only = run(tree(
        cases(positive=[POS], negative=[{"prompt": "x", "owner": "manual"}]),
        extra={"skills/manual/SKILL.md": skill("manual", command_only=True)},
    ))
    assert verdicts(command_only, "trigger-negative") == ["fail"], command_only


@test
def an_eval_id_of_an_unexpected_type_is_reported_not_raised():
    odd = [{"id": [1], "prompt": "p", "expected_output": "o", "expectations": ["e"]}] * 2
    rows = run(tree(cases(evals=odd), command_only=True))
    assert verdicts(rows, "schema") == ["fail"], rows


@test
def without_a_model_the_model_dependent_cases_are_skipped_not_failed():
    rows = run(tree(cases(positive=[POS], negative=[{"prompt": "x", "owner": "sibling"}])))
    assert verdicts(rows, "trigger-positive") == ["skip"], rows
    assert verdicts(rows, "trigger-negative") == ["skip"], "an unranked case is not a passed one"
    assert verdicts(rows, "execution") == ["skip"], rows
    assert not rse.failed(rows), "the free suite must pass with no model"


@test
def only_restricts_the_run_and_a_named_skill_without_cases_fails():
    files = tree(cases(positive=[POS], negative=[{"prompt": "x", "owner": "sibling"}]))
    assert {r["skill"] for r in run(files, only=["demo"])} == {"demo"}
    rows = run(files, only=["sibling"])
    assert verdicts(rows) == ["fail"] and rows[0]["skill"] == "sibling", rows
    rows = run(files, only=["no-such-skill"])
    assert verdicts(rows) == ["fail"], rows


def fake_model(ranking, met=True):
    """A model that ranks skills as told, replies to tasks, and grades every expectation `met`."""
    def model(prompt):
        if prompt.startswith(rse.RANK_PROMPT_HEAD):
            return "Ranking: " + json.dumps(ranking)
        if prompt.startswith(rse.JUDGE_PROMPT_HEAD):
            return json.dumps([met] * prompt.count("\n- "))
        return "did the thing"
    return model


BOTH = cases(positive=[POS], negative=[{"prompt": "other thing", "owner": "sibling"}])


@test
def with_a_model_a_positive_passes_only_when_the_skill_ranks_within_top_k():
    assert verdicts(run(tree(BOTH), model=fake_model(["demo", "sibling"])), "trigger-positive") == ["pass"]
    assert verdicts(run(tree(BOTH), model=fake_model(["sibling", "demo"])), "trigger-positive") == ["fail"]


@test
def with_a_model_a_negative_passes_only_when_the_owner_outranks_the_skill():
    assert verdicts(run(tree(BOTH), model=fake_model(["sibling", "demo"])), "trigger-negative") == ["pass"]
    assert verdicts(run(tree(BOTH), model=fake_model(["demo", "sibling"])), "trigger-negative") == ["fail"]
    assert verdicts(run(tree(BOTH), model=fake_model(["demo"])), "trigger-negative") == ["fail"]


@test
def with_a_model_an_execution_case_fails_when_an_expectation_is_unmet():
    ok = run(tree(BOTH), model=fake_model(["demo"], met=True))
    assert verdicts(ok, "execution") == ["pass"], ok
    bad = run(tree(BOTH), model=fake_model(["demo"], met=False))
    assert verdicts(bad, "execution") == ["fail"], bad
    assert "the thing is done" in [r for r in bad if r["kind"] == "execution"][0]["detail"]


@test
def an_unreadable_model_reply_is_a_failed_case_not_a_crash():
    rows = run(tree(BOTH), model=lambda prompt: "I would rather not say")
    assert verdicts(rows, "trigger-positive") == ["fail"], rows
    assert verdicts(rows, "execution") == ["fail"], rows


@test
def a_ranking_is_read_from_a_reply_that_reasons_first():
    chatty = lambda prompt: 'I think [maybe] the answer is: ["demo", "sibling"]'
    assert verdicts(run(tree(BOTH), model=chatty), "trigger-positive") == ["pass"]


@test
def the_command_exits_0_when_clean_1_on_a_failed_case_and_2_on_bad_usage():
    code, out, _ = cli(tree(BOTH))
    assert code == 0 and "skip" in out, (code, out)
    code, out, _ = cli(tree("{ not json"))
    assert code == 1 and "fail" in out, (code, out)
    code, _, err = cli(tree(BOTH), "--with-model", "--model-cmd", "no-such-model-command-xyz")
    assert code == 2 and "no-such-model-command-xyz" in err, (code, err)


@test
def the_command_emits_rows_as_json_and_honours_skill():
    code, out, _ = cli(tree(BOTH), "--json", "--skill", "demo")
    rows = json.loads(out)["rows"]
    assert code == 0 and rows and {r["skill"] for r in rows} == {"demo"}, (code, rows)
    code, out, _ = cli(tree(BOTH), "--json", "--skill", "sibling")
    assert code == 1, "a named skill without a cases file is a failure"


def main():
    failed = 0
    for fn in TESTS:
        try:
            fn()
            print(f"  ok   {fn.__name__}")
        except AssertionError as err:
            failed += 1
            print(f"  FAIL {fn.__name__}: {err}")
    print(f"\n{len(TESTS)} tests, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
