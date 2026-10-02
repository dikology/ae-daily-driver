#!/usr/bin/env python3
"""
Tests for audit_context.py. Each test builds a throwaway repo on disk, runs one
check, and asserts on the rules that fire — so a regression in a check surfaces here
rather than in an audit report.

Run: python3 scripts/test_audit_context.py
"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import audit_context as ac  # noqa: E402


def build(root, files):
    for rel, content in files.items():
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)


def audit(files, scope="repo"):
    """Run every check over a temporary repo, returning (findings, items, always_tokens)."""
    with tempfile.TemporaryDirectory() as root:
        build(root, files)
        items = ac.build_inventory(root, scope=scope)
        out = ac.Findings()
        scoped = [e for e in items if e["in_scope"]]
        for entry in scoped:
            if entry["kind"] == "skill":
                ac.check_frontmatter(entry, out)
                ac.check_body_size(entry, out)
        links = ac.check_links(root, scoped, out)
        ac.check_reference_tocs(root, scoped, links, out)
        ac.check_time_sensitive(root, scoped, out)
        ac.check_path_claims(root, scoped, out)
        ac.check_evals(root, scoped, out)
        ac.check_duplicates(root, scoped, out)
        _, always = ac.tier_totals(items)
        return out, items, always


def rules(out):
    return sorted({r["rule"] for r in out.rows})


def skill(name="demo", desc="Does a thing. Use when the user asks for a thing.", body="# Demo\n",
          command_only=False):
    flag = "disable-model-invocation: true\n" if command_only else ""
    return f"---\nname: {name}\ndescription: {desc}\n{flag}---\n\n{body}"


EXECUTION = [{"prompt": "do the thing", "expected_output": "a thing", "expectations": ["the thing is done"]}]
TRIGGER = {
    "positive": [{"prompt": "do the thing", "top_k": 1}],
    "negative": [{"prompt": "do another thing", "owner": "sibling"}],
}
# Rung-2 cases files: what an auto-triggerable skill and a command-only skill each owe.
CASES = json.dumps({"trigger": TRIGGER, "evals": EXECUTION})
CASES_COMMAND_ONLY = json.dumps({"evals": EXECUTION})


TESTS = []


def test(fn):
    TESTS.append(fn)
    return fn


@test
def frontmatter_violations_are_errors():
    out, _, _ = audit({"skills/bad/SKILL.md": skill(name="Bad_Claude", desc="I can help you with things")})
    assert "R2.1" in rules(out), "invalid name characters must be flagged"
    assert "R2.4" in rules(out), "first-person description must be flagged"
    assert any("reserved word" in r["message"] for r in out.rows), "reserved word must be named"


@test
def clean_skill_produces_no_frontmatter_findings():
    out, _, _ = audit({
        "skills/good/SKILL.md": skill(),
        "skills/good/evals/cases.json": CASES,
    })
    assert not [r for r in out.rows if r["rule"].startswith(("R2", "R7"))], \
        f"clean skill should be quiet, got {out.rows}"


@test
def oversize_body_is_an_error_and_near_limit_is_a_warning():
    over = audit({"skills/big/SKILL.md": skill(body="x\n" * (ac.SKILL_BODY_MAX_LINES + 10))})[0]
    assert [r for r in over.rows if r["rule"] == "R1.1" and r["severity"] == "error"]
    near = audit({"skills/mid/SKILL.md": skill(body="x\n" * (ac.SKILL_BODY_WARN_LINES + 10))})[0]
    assert [r for r in near.rows if r["rule"] == "R1.1" and r["severity"] == "warn"]


@test
def unresolvable_link_is_flagged_with_its_line():
    out, _, _ = audit({"skills/s/SKILL.md": skill(body="See [gate](../../../docs/gate.md)\n")})
    hits = [r for r in out.rows if r["rule"] == "R4.3"]
    assert hits and hits[0]["line"] == 6, f"expected line 6, got {hits}"


@test
def placeholder_link_target_is_not_a_broken_link():
    out, _, _ = audit({"skills/s/SKILL.md": skill(body="Cite as [short title](uuid) using the folder id.\n")})
    assert "R4.3" not in rules(out), "bare placeholder targets must not be treated as file links"


@test
def two_level_reference_chain_is_an_error():
    out, _, _ = audit({
        "skills/s/SKILL.md": skill(body="See [a](a.md)\n"),
        "skills/s/a.md": "Then see [b](b.md)\n",
        "skills/s/b.md": "content\n",
    })
    assert "R4.2" in rules(out), "SKILL.md -> a.md -> b.md must be flagged"


@test
def one_level_references_are_accepted():
    out, _, _ = audit({
        "skills/s/SKILL.md": skill(body="See [a](a.md) and [b](b.md)\n"),
        "skills/s/a.md": "content\n",
        "skills/s/b.md": "content\n",
    })
    assert "R4.2" not in rules(out) and "R3.4" not in rules(out)


@test
def bundled_file_never_linked_is_flagged_as_orphan():
    out, _, _ = audit({"skills/s/SKILL.md": skill(), "skills/s/orphan.md": "unreachable\n"})
    assert "R3.4" in rules(out)


@test
def long_reference_without_toc_is_flagged():
    out, _, _ = audit({
        "skills/s/SKILL.md": skill(body="See [a](a.md)\n"),
        "skills/s/a.md": "# A\n" + "line\n" * (ac.REFERENCE_TOC_THRESHOLD_LINES + 5),
    })
    assert "R4.4" in rules(out)
    with_toc = audit({
        "skills/s/SKILL.md": skill(body="See [a](a.md)\n"),
        "skills/s/a.md": "# A\n\n## Contents\n- one\n" + "line\n" * (ac.REFERENCE_TOC_THRESHOLD_LINES + 5),
    })[0]
    assert "R4.4" not in rules(with_toc)


@test
def quoted_time_sensitive_phrase_is_not_flagged():
    asserted = audit({"AGENTS.md": "The mcp/ directory is coming soon.\n"})[0]
    assert "R8.1" in rules(asserted), "an asserted promise must be flagged"
    quoted = audit({"AGENTS.md": 'Avoid phrases like "coming soon" in instructions.\n'})[0]
    assert "R8.1" not in rules(quoted), "a phrase named as an example must not be flagged"


@test
def path_claim_resolves_against_the_skill_root():
    out, _, _ = audit({
        "skills/s/SKILL.md": skill(body="Run `scripts/go.py`\n"),
        "skills/s/scripts/go.py": "print(1)\n",
    })
    assert "R8.6" not in rules(out), "a skill may name its own script from the skill root"
    missing = audit({"skills/s/SKILL.md": skill(body="Run `scripts/gone.py`\n")})[0]
    assert "R8.6" in rules(missing)


@test
def duplicate_passage_across_two_loaded_files_is_flagged():
    shared = "the gate is failed closed and a blocked ticket never reaches execute under any circumstance"
    out, _, _ = audit({
        "docs/gate.md": shared + "\n",
        "skills/s/SKILL.md": skill(body=shared + "\n"),
    })
    assert "R8.2" in rules(out)


@test
def always_tier_counts_skill_descriptions_not_only_root_files():
    description = "Does a specific thing. Use when the user asks for that specific thing."
    _, _, always = audit({
        "AGENTS.md": "# Repo\n",
        "skills/s/SKILL.md": skill(desc=description, body="body\n"),
    })
    assert always >= ac.est_tokens(description), \
        "frontmatter descriptions ship in the system prompt and must be in the always tier"


@test
def load_tiers_are_assigned_by_artifact_kind():
    _, items, _ = audit({
        "AGENTS.md": "# Repo\n",
        ".cursor/rules/scoped.mdc": "---\ndescription: x\nglobs:\n  - \"**/*.sql\"\nalwaysApply: false\n---\n# R\n",
        ".cursor/rules/global.mdc": "---\ndescription: x\nalwaysApply: true\n---\n# R\n",
        "skills/s/SKILL.md": skill(),
        "diagrams/d.excalidraw": "{}\n",
    })
    tiers = {i["path"]: i["tier"] for i in items}
    assert tiers["AGENTS.md"] == "always"
    assert tiers[".cursor/rules/scoped.mdc"] == "path"
    assert tiers[".cursor/rules/global.mdc"] == "always"
    assert tiers["skills/s/SKILL.md"] == "task"
    assert tiers["diagrams/d.excalidraw"] == "none"


@test
def skill_test_fixtures_are_on_exec_not_task_context():
    _, items, _ = audit({
        "skills/s/SKILL.md": skill(),
        "skills/s/config.yaml": "a: 1\n",
        "skills/s/scenarios/01_case.yaml": "a: 1\n",
    })
    tiers = {i["path"]: i["tier"] for i in items}
    assert tiers["skills/s/config.yaml"] == "task", "skill config is read into context"
    assert tiers["skills/s/scenarios/01_case.yaml"] == "on-exec", \
        "test fixtures are read by the skill's scripts, not loaded into context"


def r71(files):
    return [r for r in audit(files)[0].rows if r["rule"] == "R7.1"]


@test
def a_skill_with_no_cases_file_is_flagged():
    assert r71({"skills/s/SKILL.md": skill()})


@test
def an_empty_evals_directory_does_not_satisfy_the_check():
    assert r71({"skills/s/SKILL.md": skill(), "skills/s/evals/.gitkeep": ""}), \
        "R7.1 must not be satisfiable by mkdir"
    assert r71({"skills/s/SKILL.md": skill(), "skills/s/scenarios/01.yaml": "a: 1\n"}), \
        "a directory of some other shape is not a rung-2 cases file"


@test
def a_malformed_cases_file_is_an_error():
    not_json = r71({"skills/s/SKILL.md": skill(), "skills/s/evals/cases.json": "{ nope"})
    assert [r for r in not_json if r["severity"] == "error"], not_json
    wrong_shape = r71({"skills/s/SKILL.md": skill(), "skills/s/evals/cases.json": "{}"})
    assert [r for r in wrong_shape if r["severity"] == "error"], wrong_shape


@test
def an_auto_triggerable_skill_owes_trigger_cases_and_execution_expectations():
    assert not r71({"skills/s/SKILL.md": skill(), "skills/s/evals/cases.json": CASES})
    assert r71({"skills/s/SKILL.md": skill(), "skills/s/evals/cases.json": CASES_COMMAND_ONLY}), \
        "an auto-triggerable skill without trigger cases must be flagged"
    assert r71({"skills/s/SKILL.md": skill(),
                "skills/s/evals/cases.json": json.dumps({"trigger": TRIGGER, "evals": []})}), \
        "trigger cases alone do not stand in for execution expectations"


@test
def a_command_only_skill_owes_execution_expectations_and_no_trigger_cases():
    command_only = skill(command_only=True)
    assert not r71({"skills/s/SKILL.md": command_only, "skills/s/evals/cases.json": CASES_COMMAND_ONLY})
    assert r71({"skills/s/SKILL.md": command_only, "skills/s/evals/cases.json": CASES}), \
        "trigger cases on a skill that never auto-triggers test nothing"
    assert r71({"skills/s/SKILL.md": command_only,
                "skills/s/evals/cases.json": json.dumps({"evals": []})})


@test
def canonical_scope_excludes_the_sandbox_but_keeps_the_canonical_surface():
    files = {
        "skills/real/SKILL.md": skill(name="real", body="See [x](../../../docs/x.md)\n"),
        "skills/real/evals/cases.json": CASES,
        ".cursor/skills/sand/SKILL.md": skill(name="sand", desc="Does sandbox things."),
        ".cursor/skills/sand/notes.md": "an orphan reference\n",
    }
    repo = audit(files, scope="repo")[0]
    canon = audit(files, scope="canonical")[0]

    # Unscoped, the sandbox skill generates findings of its own.
    assert any(r["path"].startswith(".cursor/") for r in repo.rows), \
        "sandbox should produce findings when the audit is not scoped"
    # Scoped to the canonical surface, nothing under the sandbox is reported.
    assert not any(r["path"].startswith(".cursor/") for r in canon.rows), \
        f"sandbox must be out of scope, got {[r['path'] for r in canon.rows]}"
    # The canonical skill's own finding is untouched by the scoping.
    assert "R4.3" in rules(canon), "scoping removes noise, it must not weaken a check"


@test
def scoping_does_not_change_findings_on_the_canonical_surface():
    files = {
        "skills/s/SKILL.md": skill(name="s", body="Run `scripts/gone.py`\n"),
        ".cursor/skills/junk/SKILL.md": skill(name="junk", desc="Does things."),
    }
    on_surface = lambda out: {
        (r["rule"], r["path"], r["line"]) for r in out.rows if r["path"].startswith("skills/")
    }
    repo_rows = on_surface(audit(files, scope="repo")[0])
    canon_rows = on_surface(audit(files, scope="canonical")[0])
    assert repo_rows and repo_rows == canon_rows, (repo_rows, canon_rows)


@test
def a_passage_shared_only_with_the_sandbox_is_not_flagged_under_canonical_scope():
    shared = "the gate is failed closed and a blocked ticket never reaches execute under any circumstance"
    files = {
        ".claude/skills/tg/SKILL.md": skill(name="tg", body=shared + "\n"),
        ".cursor/skills/tg/SKILL.md": skill(name="tg", body=shared + "\n"),
    }
    assert "R8.2" in rules(audit(files, scope="repo")[0])
    assert "R8.2" not in rules(audit(files, scope="canonical")[0]), \
        "the only duplicate was the sandbox copy; canonical scope must be quiet"


@test
def excluded_files_are_grouped_and_counted_for_the_declaration():
    _, items, _ = audit({
        "skills/s/SKILL.md": skill(),
        "skills/s/evals/cases.json": CASES,
        ".cursor/skills/a/SKILL.md": skill(name="a"),
        ".cursor/skills/a/ref.md": "x\n",
        "docs/x.md": "x\n",
        "README.md": "# Repo\n",
    }, scope="canonical")
    groups = ac.group_excluded(items)
    assert groups[".cursor"] == 2, groups
    assert groups["docs"] == 1, groups
    assert groups[""] == 1, "a repo-root file groups under the empty key"
    assert "skills" not in groups, "the canonical surface is in scope, not excluded"


@test
def repo_scope_is_the_default_and_excludes_nothing():
    _, items, _ = audit({
        "skills/s/SKILL.md": skill(),
        ".cursor/skills/a/SKILL.md": skill(name="a"),
    })
    assert all(e["in_scope"] for e in items)
    assert ac.group_excluded(items) == {}


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
