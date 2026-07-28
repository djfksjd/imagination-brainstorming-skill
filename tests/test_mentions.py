"""A banned word can be denied, and denying it is not using it.

`magical` and `delightful` are hard bans, and they fired inside a negation: a
fantasy spec saying "the region is not magical" was rejected for saying so, with
no per-session release anywhere at the gate. That is the same blindness a
similarity score had when it could not tell an assertion from a quotation, which
is why bind markers replaced it one layer up. The fix has the same shape: the
author marks the span and names the id, and the mark is visible in the source
and reported in the verdict. It cannot verify that the word really is mentioned
rather than used - nothing in the standard library can - so these tests pin what
it does do: the release is per span, per id, and nowhere else.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

NEGATION = "The region is not magical; nothing in it is enchanted."
MARKED = "<!-- mention: hollow-magical -->The region is not magical<!-- /mention -->; nothing in it is enchanted."


@pytest.fixture
def draft(tmp_path: Path):
    def _write(text: str) -> str:
        path = tmp_path / "draft.md"
        path.write_text(text + "\n", encoding="utf-8")
        return str(path)

    return _write


def test_a_negated_ban_is_flagged_when_it_is_not_marked(run, draft, banlist):
    res = run("cliche_lint.py", "--draft", draft(NEGATION), "--banlist", str(banlist))
    assert res.code == 3, res
    assert "hollow-magical" in res.out


def test_a_marked_mention_is_not_a_use(run, draft, banlist):
    res = run("cliche_lint.py", "--draft", draft(MARKED), "--banlist", str(banlist))
    assert res.code == 0, res.out
    assert "hollow-magical" not in res.out


def test_the_release_stops_at_the_end_of_the_span(run, draft, banlist):
    """The whole point of marking a span rather than releasing a rule."""
    text = MARKED + "\n\nThe hand-off ritual itself is magical in the ordinary sense."
    res = run("cliche_lint.py", "--draft", draft(text), "--banlist", str(banlist))
    assert res.code == 3, res.out
    assert "line 3" in res.out


def test_a_mention_releases_only_the_id_it_names(run, draft, banlist):
    text = "<!-- mention: hollow-magical -->It is not magical and not delightful<!-- /mention -->"
    res = run("cliche_lint.py", "--draft", draft(text), "--banlist", str(banlist))
    assert res.code == 3, res.out
    assert "hollow-delightful" in res.out
    assert "hollow-magical" not in res.out


def test_an_unknown_id_is_refused(run, draft, banlist):
    text = "<!-- mention: hollow-nosuchrule -->not magical<!-- /mention -->"
    res = run("cliche_lint.py", "--draft", draft(text), "--banlist", str(banlist))
    assert res.code == 1
    assert "unknown rule id" in res.err


def test_a_mention_naming_nothing_is_refused(run, draft, banlist):
    text = "<!-- mention: -->not magical<!-- /mention -->"
    res = run("cliche_lint.py", "--draft", draft(text), "--banlist", str(banlist))
    assert res.code == 1
    assert "names no rule id" in res.err


def test_the_marker_itself_is_never_linted(run, draft, banlist):
    """`hollow-magical` contains the word it releases: the comment used to trip
    the rule it was declaring."""
    res = run("cliche_lint.py", "--draft", draft(MARKED), "--banlist", str(banlist), "--json")
    assert res.code == 0
    assert res.json()["findings"] == []


# --- the same, at the real gate -------------------------------------------


@pytest.fixture
def spec_with(tmp_path: Path, references: Path):
    def _write(extra: str) -> str:
        text = (references / "example-concept.md").read_text(encoding="utf-8")
        path = tmp_path / "spec.md"
        path.write_text(text.rstrip() + "\n\n" + extra + "\n", encoding="utf-8")
        return str(path)

    return _write


def test_the_gate_flags_an_unmarked_negation(run, references, banlist, spec_with):
    res = run("spec_gate.py", "--concept", str(references / "example-concept.json"),
              "--markdown", spec_with(NEGATION), "--banlist", str(banlist), "--json")
    assert res.code == 2
    assert any("magical" in f for f in res.json()["failures"])


def test_the_gate_accepts_a_marked_mention_and_reports_it(run, references, banlist, spec_with):
    res = run("spec_gate.py", "--concept", str(references / "example-concept.json"),
              "--markdown", spec_with(MARKED), "--banlist", str(banlist), "--json")
    assert res.code == 0, res.out
    verdict = res.json()
    assert any("mentioning rather than using hollow-magical" in w for w in verdict["warnings"]), verdict
    assert any("cannot verify that" in w for w in verdict["warnings"])


def test_the_gate_refuses_an_unknown_id(run, references, banlist, spec_with):
    marked = "<!-- mention: not-a-rule -->The region is not magical<!-- /mention -->"
    res = run("spec_gate.py", "--concept", str(references / "example-concept.json"),
              "--markdown", spec_with(marked), "--banlist", str(banlist), "--json")
    assert res.code == 2
    assert any("unknown rule id" in f for f in res.json()["failures"])


def test_a_mention_does_not_release_the_sidecar_elsewhere(run, references, banlist, spec_with, concept_path, example):
    """The markdown's spans apply to concept.json only where the same words
    appear - a marked denial in the spec cannot license a claim in the sidecar."""
    concept = deepcopy(example)
    concept["chosen"]["why"] = concept["chosen"]["why"] + " The result is magical."
    res = run("spec_gate.py", "--concept", concept_path(concept),
              "--markdown", spec_with(MARKED), "--banlist", str(banlist), "--json")
    assert res.code == 2
    assert any("magical" in f for f in res.json()["failures"])
