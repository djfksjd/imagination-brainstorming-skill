"""Nothing the judged artefact says releases a burnt instinct or a user exclusion.

Two different mechanisms have now produced the same defect. The ban list's
`allowed` field released whatever it named until it was closed; mention markers
were added afterwards and released whatever they named, including all twelve
first instincts and the user's own exclusions, until this file was written. A
test naming those two routes would not catch the third, so these tests assert
the property instead of the mechanism:

* the invariant, at the one function every release has to pass through;
* a pin on that function's release surface, so a *new* route cannot be added
  without this file failing and the invariant being extended to cover it;
* a sweep over the shapes an artefact can take - every field of the ban list
  emptied, retiered, and stuffed with every id in the contract, plus fields the
  gate does not read today - each asserting the burnt phrase still fails.
"""

from __future__ import annotations

import inspect
import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "skills" / "imagination-brainstorming" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from engine import deck_lint_entries, lint_text, load_deck, releasable_ids  # noqa: E402

INSTINCT = "handover app with structured form"
EXCLUSION = "no scoring or ranking of nurses"


def protected_entries() -> list[dict]:
    """A burnt instinct and a user exclusion, each claiming to be deck-sourced.

    The claim is part of the fixture: `source` is written by the artefact, so a
    protection that trusted it would be a fourth route.
    """
    return [
        {"id": "instinct-01", "phrase": INSTINCT, "tier": "ban", "group": "first-instinct", "source": "deck"},
        {"id": "user-02", "phrase": EXCLUSION, "tier": "ban", "group": "user-exclusion", "source": "deck"},
    ]


def test_no_release_of_any_shape_reaches_a_protected_entry():
    """The invariant, stated once: hand `lint_text` every release it accepts,
    naming every id, over the whole text, and the protected phrases are still
    reported."""
    deck = load_deck("cliches")
    entries = deck_lint_entries(deck) + protected_entries()
    patterns = deck["structural_patterns"]
    text = f"{INSTINCT}\n{EXCLUSION}\n"
    every_id = {str(e["id"]) for e in entries} | {str(p["id"]) for p in patterns}

    findings = lint_text(text, entries, patterns, every_id, [(text, every_id)])
    reported = {f["id"] for f in findings if f["tier"] == "ban"}
    assert {"instinct-01", "user-02"} <= reported, findings


def test_the_release_surface_is_pinned_so_a_third_route_fails_here():
    """`lint_text` is where every release lands. If a parameter is added to it,
    this fails on purpose: extend the invariant above to drive the new route
    before shipping it."""
    params = list(inspect.signature(lint_text).parameters)
    assert params == ["text", "entries", "patterns", "allow", "mentions"], (
        "a new parameter of lint_text is a new release route; add it to "
        "test_no_release_of_any_shape_reaches_a_protected_entry, then update this list"
    )
    assert not inspect.signature(releasable_ids).parameters, (
        "releasable_ids() takes no argument on purpose - a caller that can widen the releasable set "
        "is the hole this file exists to prevent"
    )


def test_the_releasable_set_is_the_bundled_deck_and_nothing_else():
    deck = load_deck("cliches")
    expected = {e["id"] for e in deck_lint_entries(deck)} | {str(p["id"]) for p in deck["structural_patterns"]}
    assert releasable_ids() == expected
    assert not any(i.startswith(("instinct-", "user-")) for i in releasable_ids())


# --- the same property, through the gate, over artefact shapes --------------


@pytest.fixture
def burnt_spec(tmp_path: Path, references: Path) -> str:
    """The shipped spec with a burnt instinct and a user exclusion added to it."""
    text = (references / "example-concept.md").read_text(encoding="utf-8")
    path = tmp_path / "burnt.md"
    path.write_text(f"{text.rstrip()}\n\n{INSTINCT} and {EXCLUSION}\n", encoding="utf-8")
    return str(path)


def all_ids(payload: dict) -> list[str]:
    return [str(e["id"]) for e in payload["entries"]] + [
        str(p["id"]) for p in payload.get("structural_patterns", [])
    ]


def mutate(payload: dict, how: str) -> dict:
    out = deepcopy(payload)
    if how == "allowed-everything":
        out["allowed"] = all_ids(out)
    elif how == "retier-to-warn":
        for e in out["entries"]:
            if e["phrase"] in (INSTINCT, EXCLUSION):
                e["tier"] = "warn"
    elif how == "retier-to-manual":
        for e in out["entries"]:
            if e["phrase"] in (INSTINCT, EXCLUSION):
                e["tier"] = "manual"
    elif how == "drop-the-entries":
        out["entries"] = [e for e in out["entries"] if e["phrase"] not in (INSTINCT, EXCLUSION)]
    elif how == "empty-structural-patterns":
        out["structural_patterns"] = []
    elif how == "empty-manual-checks":
        out["manual_checks"] = []
    elif how == "unread-field-named-release":
        # A field this gate does not read today. If a later wave starts reading
        # one, this case is already here.
        out["release"] = all_ids(out)
        out["exempt"] = all_ids(out)
        out["skip_lint"] = True
    return out


@pytest.mark.parametrize("how", [
    "allowed-everything", "retier-to-warn", "retier-to-manual", "drop-the-entries",
    "empty-structural-patterns", "empty-manual-checks", "unread-field-named-release",
])
def test_no_ban_list_shape_lets_the_burnt_phrases_pass(how, run, references, banlist, burnt_spec, tmp_path):
    payload = json.loads(Path(banlist).read_text(encoding="utf-8"))
    path = tmp_path / f"{how}.json"
    path.write_text(json.dumps(mutate(payload, how), ensure_ascii=False), encoding="utf-8")
    res = run("spec_gate.py", "--concept", str(references / "example-concept.json"),
              "--markdown", burnt_spec, "--banlist", str(path))
    assert res.code != 0, f"{how} was accepted:\n{res.out}"


@pytest.mark.parametrize("how", ["emptied", "nulled"])
def test_emptying_any_ban_list_field_does_not_buy_a_pass(how, run, references, banlist, burnt_spec, tmp_path):
    """Field-by-field rather than by name, so a field added later is swept too."""
    payload = json.loads(Path(banlist).read_text(encoding="utf-8"))
    for key in list(payload):
        mutated = deepcopy(payload)
        mutated[key] = None if how == "nulled" else type(payload[key])() if payload[key] is not None else None
        path = tmp_path / f"{key}-{how}.json"
        path.write_text(json.dumps(mutated, ensure_ascii=False), encoding="utf-8")
        res = run("spec_gate.py", "--concept", str(references / "example-concept.json"),
                  "--markdown", burnt_spec, "--banlist", str(path))
        assert res.code != 0, f"{key} {how} was accepted:\n{res.out}"


def test_relabelling_a_user_exclusion_as_the_models_does_not_discharge_it(
        run, references, banlist, tmp_path, example):
    """`manual_checks[].source` is written by the same caller as everything else.
    Flipping it to 'model' turned the user's long exclusions from a required
    answer into a warning; whose exclusion it is now comes from the sidecar's
    instinct list, and an unmatched statement counts as the user's."""
    payload = json.loads(Path(banlist).read_text(encoding="utf-8"))
    for m in payload["manual_checks"]:
        m["source"] = "model"
    flipped = tmp_path / "flipped.json"
    flipped.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    concept = deepcopy(example)
    concept["banlist_contract"]["manual_checks_cleared"] = []
    path = tmp_path / "unanswered.json"
    path.write_text(json.dumps(concept, ensure_ascii=False), encoding="utf-8")

    res = run("spec_gate.py", "--concept", str(path),
              "--markdown", str(references / "example-concept.md"), "--banlist", str(flipped), "--json")
    assert res.code == 2, res.out
    assert any("has no note saying how the concept avoids it" in f for f in res.json()["failures"])


def test_no_markdown_marking_lets_the_burnt_phrases_pass(run, references, banlist, tmp_path):
    """Every marker shape at once: one wrapping everything, and one per id."""
    text = (references / "example-concept.md").read_text(encoding="utf-8").rstrip()
    payload = json.loads(Path(banlist).read_text(encoding="utf-8"))
    ids = ", ".join(all_ids(payload))
    shapes = {
        "whole-document": f"<!-- mention: {ids} -->{text}\n\n{INSTINCT} and {EXCLUSION}<!-- /mention -->\n",
        "one-id-per-span": (
            f"{text}\n\n<!-- mention: instinct-01 -->not {INSTINCT}<!-- /mention -->\n\n"
            f"<!-- mention: user-02 -->not {EXCLUSION}<!-- /mention -->\n"
        ),
    }
    for name, body in shapes.items():
        path = tmp_path / f"{name}.md"
        path.write_text(body, encoding="utf-8")
        res = run("spec_gate.py", "--concept", str(references / "example-concept.json"),
                  "--markdown", str(path), "--banlist", str(banlist))
        assert res.code == 2, f"{name} was accepted:\n{res.out}"
