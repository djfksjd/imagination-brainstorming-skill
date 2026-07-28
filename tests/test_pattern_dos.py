"""A `structural_patterns[].regex` in the ban list is an artefact the judged
party supplies - a hand-written ban list, or one built by banlist.py from the
deck plus the user's own instincts. This repo's rule is that such an artefact
must never own the verdict. `(a+)+b$` against forty `a` characters is the
textbook example: Python's backtracking matcher explores an exponential
number of ways to split the run of `a`s between the inner and outer `+`
before it can report there is no `b` to find, and every script that lints
text against a ban list (spec_gate.py, divergence_check.py, cliche_lint.py -
all of them through `engine.lint_text`) used to simply never return. A
verdict that never arrives is functionally "did not fail", which is exactly
the substitution this branch's other fixes closed for the mention markers and
the allow-list.

`engine.catastrophic_shape` refuses the nested-quantifier shape at compile
time instead, so the failure mode is a named, immediate refusal, not a hang -
and not a silent skip either, since a silently dropped pattern is worse than
the hang: the user would believe a ban was active that never fires again.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "skills" / "imagination-brainstorming" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from engine import catastrophic_shape  # noqa: E402

# Generous relative to the fix (which answers in well under a tenth of a
# second): this is a ceiling on "did it hang", not a performance assertion,
# so it is not sensitive to how fast the machine running the suite is.
HANG_GUARD_SECONDS = 10.0

EVIL_PATTERN = {"id": "evil", "regex": "(a+)+b$", "tier": "ban", "why": "reproduction of the pattern-DoS defect"}


def _banlist_with_evil_pattern(references: Path, tmp_path: Path) -> Path:
    payload = json.loads((references / "example-banlist.json").read_text(encoding="utf-8"))
    payload["structural_patterns"] = [*payload["structural_patterns"], EVIL_PATTERN]
    out = tmp_path / "evil-banlist.json"
    out.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return out


def _banlist_with_benign_custom_pattern(references: Path, tmp_path: Path) -> Path:
    payload = json.loads((references / "example-banlist.json").read_text(encoding="utf-8"))
    payload["structural_patterns"] = [*payload["structural_patterns"], {
        "id": "moonshot-claim",
        "regex": r"\bthis will change everything\b",
        "tier": "ban",
        "why": "a legitimate custom structural ban a user might add",
    }]
    out = tmp_path / "benign-banlist.json"
    out.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return out


# --- the reproduction: every caller of engine.lint_text must refuse, not hang --

def test_spec_gate_refuses_the_evil_pattern_instead_of_hanging(run, references, tmp_path):
    banlist = _banlist_with_evil_pattern(references, tmp_path)
    markdown = tmp_path / "spec.md"
    original = (references / "example-concept.md").read_text(encoding="utf-8")
    markdown.write_text(original + "\n\n" + "a" * 40 + "\n", encoding="utf-8")

    res = run(
        "spec_gate.py",
        "--concept", str(references / "example-concept.json"),
        "--markdown", str(markdown),
        "--banlist", str(banlist),
        timeout=HANG_GUARD_SECONDS,
    )
    assert res.code != 0
    assert "evil" in res.err
    assert "nested" in res.err or "repetition" in res.err


def test_divergence_check_refuses_the_evil_pattern_instead_of_hanging(run, references, tmp_path):
    banlist = _banlist_with_evil_pattern(references, tmp_path)
    approaches = copy.deepcopy(json.loads((references / "example-approaches.json").read_text(encoding="utf-8")))
    approaches["approaches"][0]["summary"] += " " + "a" * 40
    approaches_path = tmp_path / "approaches.json"
    approaches_path.write_text(json.dumps(approaches, ensure_ascii=False), encoding="utf-8")

    res = run(
        "divergence_check.py",
        "--approaches", str(approaches_path),
        "--banlist", str(banlist),
        timeout=HANG_GUARD_SECONDS,
    )
    assert res.code != 0
    assert "evil" in res.err


def test_cliche_lint_refuses_the_evil_pattern_instead_of_hanging(run, references, tmp_path):
    banlist = _banlist_with_evil_pattern(references, tmp_path)
    draft = tmp_path / "draft.txt"
    draft.write_text("a" * 40 + "\n", encoding="utf-8")

    res = run(
        "cliche_lint.py",
        "--draft", str(draft),
        "--banlist", str(banlist),
        timeout=HANG_GUARD_SECONDS,
    )
    assert res.code != 0
    assert "evil" in res.err


# --- a legitimate custom pattern must still work -----------------------------

def test_a_legitimate_custom_structural_pattern_still_catches_its_target(run, references, tmp_path):
    banlist = _banlist_with_benign_custom_pattern(references, tmp_path)
    draft = tmp_path / "draft.txt"
    draft.write_text("Honestly, this will change everything for the industry.\n", encoding="utf-8")

    res = run(
        "cliche_lint.py",
        "--draft", str(draft),
        "--banlist", str(banlist),
        "--json",
        timeout=HANG_GUARD_SECONDS,
    )
    assert res.code != 0, res
    findings = res.json()
    ids = {f["id"] for f in findings["findings"]} if isinstance(findings, dict) else {f["id"] for f in findings}
    assert "moonshot-claim" in ids


def test_a_legitimate_custom_pattern_gates_the_shipped_spec_normally(run, references, tmp_path):
    """The benign addition must not change the shipped example's PASSED verdict
    when its target phrase is absent - proof the new check doesn't over-refuse."""
    banlist = _banlist_with_benign_custom_pattern(references, tmp_path)
    res = run(
        "spec_gate.py",
        "--concept", str(references / "example-concept.json"),
        "--markdown", str(references / "example-concept.md"),
        "--banlist", str(banlist),
        timeout=HANG_GUARD_SECONDS,
    )
    assert res.code == 0, res
    assert "PASSED" in res.out


# --- catastrophic_shape itself, and a pin against the shipped deck ----------

@pytest.mark.parametrize("regex_src", [
    "(a+)+b$",
    "(a*)*b",
    "(a+)*b",
    "((a)+)+",
    "(a{2,}){2,}b",
])
def test_catastrophic_shape_flags_the_classic_nested_quantifier_family(regex_src):
    assert catastrophic_shape(regex_src) is not None


@pytest.mark.parametrize("regex_src", [
    r"\bcross between\b",
    r"\b(?:a )?(?:mix|blend|fusion|mashup|combination) of\b",
    r"\busers? will (?:love|enjoy|appreciate)\b",
    r"(abc)+d",
    r"a{1,5}b",
])
def test_catastrophic_shape_does_not_flag_ordinary_patterns(regex_src):
    assert catastrophic_shape(regex_src) is None


def test_every_shipped_deck_structural_pattern_clears_the_check(decks):
    """Pinned against the shipped deck: if a future cliches.json entry trips
    this check, that must fail here, at test time, and name the pattern - not
    surface as a hang in a user's terminal."""
    for pattern in decks["cliches"]["structural_patterns"]:
        reason = catastrophic_shape(pattern["regex"])
        assert reason is None, f"deck pattern {pattern['id']!r} was refused: {reason}"


def test_every_shipped_example_banlist_structural_pattern_clears_the_check(references):
    for name in ("example-banlist.json", "example-ritual-banlist.json"):
        payload = json.loads((references / name).read_text(encoding="utf-8"))
        for pattern in payload.get("structural_patterns", []):
            reason = catastrophic_shape(pattern["regex"])
            assert reason is None, f"{name} pattern {pattern['id']!r} was refused: {reason}"
