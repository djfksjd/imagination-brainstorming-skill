"""The gate is fail-closed: anything it cannot verify is a failure. These tests
pin each way the work can be skipped and the spec still look finished."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path

import pytest


@pytest.fixture
def concept(example):
    return deepcopy(example)


def test_the_shipped_example_passes(gate, references):
    res = gate(str(references / "example-concept.json"))
    assert res.code == 0, res.out
    assert "PASSED" in res.out


def test_the_sidecar_alone_is_not_a_gate(run, references):
    """Gating concept.json by itself would pass a session that never wrote the
    document the gate is supposed to be about."""
    res = run("spec_gate.py", "--concept", str(references / "example-concept.json"))
    assert res.code != 0
    assert "--markdown" in res.err and "--banlist" in res.err


def test_untested_premises_fail(gate, concept_path, concept):
    for p in concept["premises"]:
        p["verdict"] = "kept"
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("refined the brief instead of testing it" in f for f in res.json()["failures"])


def test_too_few_premises_fail(gate, concept_path, concept):
    concept["premises"] = concept["premises"][:2]
    res = gate(concept_path(concept), "--json")
    assert res.code == 2


def test_unconfirmed_contract_fails(gate, concept_path, concept):
    concept["banlist_contract"]["user_confirmed"] = False
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("user_confirmed" in f for f in res.json()["failures"])


def test_missing_skeleton_fails(gate, concept_path, concept):
    concept["banlist_contract"]["skeleton"] = "a form"
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("skeleton" in f for f in res.json()["failures"])


def test_too_few_instincts_fail(gate, concept_path, concept):
    concept["banlist_contract"]["model_instincts"] = ["a form", "a board"]
    res = gate(concept_path(concept), "--json")
    assert res.code == 2


def test_no_unsafe_seat_fails(gate, concept_path, concept):
    concept["approaches"][0]["unsafe_seat"] = False
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("unsafe seat" in f for f in res.json()["failures"])


def test_two_chosen_approaches_fail(gate, concept_path, concept):
    concept["approaches"][0]["chosen"] = True
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("marked chosen" in f for f in res.json()["failures"])


def test_chosen_id_must_match(gate, concept_path, concept):
    concept["chosen"]["approach_id"] = "ward-ledger"
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("does not match" in f for f in res.json()["failures"])


def test_wish_list_without_a_refusal_fails(gate, concept_path, concept):
    concept["chosen"]["forbids"] = "it will not be a burden"
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("wish list" in f for f in res.json()["failures"])


def test_thin_first_use_scene_fails(gate, concept_path, concept):
    concept["first_use_scene"] = "A nurse uses it at the end of the shift and it works well."
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("first_use_scene" in f for f in res.json()["failures"])


def test_missing_neighbours_fail(gate, concept_path, concept):
    concept["nearest_existing"] = []
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("nearest_existing" in f for f in res.json()["failures"])


def test_hidden_unknowns_fail(gate, concept_path, concept):
    concept["open_questions"] = ["will it work?"]
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("hidden" in f for f in res.json()["failures"])


def test_missing_decision_log_fails(gate, concept_path, concept):
    concept["decisions"] = concept["decisions"][:1]
    res = gate(concept_path(concept), "--json")
    assert res.code == 2


def test_bad_handoff_target_fails(gate, concept_path, concept):
    concept["handoff"]["next"] = "start-implementing"
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("handoff.next" in f for f in res.json()["failures"])


def test_placeholders_anywhere_fail(gate, concept_path, concept):
    concept["chosen"]["why"] = "TBD - we will work this out with the ward later on in the process."
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("placeholder" in f for f in res.json()["failures"])


def test_no_user_exclusions_warns_but_passes(gate, concept_path, concept):
    concept["banlist_contract"]["user_exclusions"] = []
    res = gate(concept_path(concept), "--json")
    assert res.code == 0
    assert any("no exclusions of their own" in w for w in res.json()["warnings"])


def test_markdown_section_markers_are_required(gate, concept_path, concept, tmp_path):
    md = tmp_path / "spec.md"
    md.write_text("# Concept\n\n<!-- section: brief -->\nSome text.\n", encoding="utf-8")
    res = gate(concept_path(concept), "--markdown", str(md), "--json")
    assert res.code == 2
    assert any("section: premises" in f for f in res.json()["failures"])


MARKER = re.compile(r"<!--\s*section:\s*([\w-]+)\s*-->", re.IGNORECASE)


def replace_section(spec: str, section: str, body: str) -> str:
    """Swap one section body of the shipped spec, leaving the rest - and so the
    binding between the document and the sidecar - intact."""
    marks = list(MARKER.finditer(spec))
    for i, m in enumerate(marks):
        if m.group(1).lower() != section:
            continue
        end = marks[i + 1].start() if i + 1 < len(marks) else len(spec)
        return spec[:m.end()] + "\n" + body + "\n\n" + spec[end:]
    raise AssertionError(f"section {section} not found")


def test_banlist_section_is_exempt_from_the_lint(gate, concept_path, concept, tmp_path, spec_md):
    """The ban contract quotes the banned material by design, so that one
    section - and only that one - is dropped before linting."""
    spec = Path(spec_md).read_text(encoding="utf-8")
    md = tmp_path / "spec.md"
    md.write_text(replace_section(
        spec, "banlist",
        "Off the table: a digitised SBAR template, a handover quality score, gamification, "
        "and anything that turns this into a form to fill in at the end of the shift.",
    ), encoding="utf-8")
    res = gate(concept_path(concept), "--markdown", str(md), "--json")
    assert res.code == 0, res.out


def test_content_after_the_banlist_section_is_still_linted(gate, concept_path, concept, tmp_path, spec_md):
    """Putting the contract last used to blank the rest of the document."""
    spec = Path(spec_md).read_text(encoding="utf-8")
    md = tmp_path / "spec.md"
    md.write_text(replace_section(spec, "handoff",
                                  "Next: writing-plans. This is a frictionless one-stop shop for the ward, "
                                  "and nothing else is left to decide before planning starts."),
                  encoding="utf-8")
    res = gate(concept_path(concept), "--markdown", str(md), "--json")
    assert res.code == 2
    assert any("banned phrase" in f for f in res.json()["failures"])


def test_the_preamble_is_linted_too(gate, concept_path, concept, tmp_path, spec_md):
    """Rebuilding the text from section bodies dropped everything above the
    first marker, so a banned phrase in the title went unseen."""
    spec = Path(spec_md).read_text(encoding="utf-8")
    md = tmp_path / "spec.md"
    md.write_text("# A frictionless concept\n\n" + spec, encoding="utf-8")
    res = gate(concept_path(concept), "--markdown", str(md), "--json")
    assert res.code == 2
    assert any("banned phrase" in f for f in res.json()["failures"])


def test_invisible_bodies_do_not_count(gate, concept_path, concept, tmp_path, decks):
    """Ten markers each followed by a long HTML comment rendered as a title and
    nothing else, and passed."""
    md = tmp_path / "spec.md"
    md.write_text("# Empty shell\n\n" + "".join(
        f"<!-- section: {s['id']} -->\n<!-- {'z' * 120} -->\n"
        for s in decks["spec-schema"]["required_markdown_sections"]
    ), encoding="utf-8")
    res = gate(concept_path(concept), "--markdown", str(md), "--json")
    assert res.code == 2
    assert any("a reader can see" in f for f in res.json()["failures"])


def test_markdown_must_contain_the_concept(gate, concept_path, concept, tmp_path, decks):
    """A document with the right markers and unrelated prose is not this spec."""
    filler = ("The unit reviewed several operational considerations across the whole department "
              "before settling on an approach that suits the existing rota and its constraints. ")
    md = tmp_path / "spec.md"
    md.write_text("# Something else\n\n" + "".join(
        f"<!-- section: {s['id']} -->\n{filler}\n"
        for s in decks["spec-schema"]["required_markdown_sections"]
    ), encoding="utf-8")
    res = gate(concept_path(concept), "--markdown", str(md), "--json")
    assert res.code == 2
    assert any("must be the same piece of work" in f for f in res.json()["failures"])


def test_empty_sections_fail(gate, concept_path, concept, tmp_path, decks):
    md = tmp_path / "spec.md"
    md.write_text("# Concept\n\n" + "".join(
        f"<!-- section: {s['id']} -->\nx\n" for s in decks["spec-schema"]["required_markdown_sections"]
    ), encoding="utf-8")
    res = gate(concept_path(concept), "--markdown", str(md), "--json")
    assert res.code == 2
    assert any("a reader can see" in f for f in res.json()["failures"])


def test_sections_out_of_order_fail(gate, concept_path, concept, tmp_path, decks, spec_md):
    spec = Path(spec_md).read_text(encoding="utf-8")
    marks = list(MARKER.finditer(spec))
    blocks = [spec[m.start():(marks[i + 1].start() if i + 1 < len(marks) else len(spec))]
              for i, m in enumerate(marks)]
    blocks.append(blocks.pop(2))  # move the ban contract to the end
    md = tmp_path / "spec.md"
    md.write_text(spec[:marks[0].start()] + "".join(blocks), encoding="utf-8")
    res = gate(concept_path(concept), "--markdown", str(md), "--json")
    assert res.code == 2
    assert any("out of order" in f for f in res.json()["failures"])


def test_banned_phrase_outside_the_contract_still_fails(gate, concept_path, concept, tmp_path):
    concept["chosen"]["why"] += " It is a frictionless experience for the whole ward."
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("banned phrase" in f for f in res.json()["failures"])


def test_unreadable_concept_is_a_usage_error(gate, tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")
    assert gate(str(path)).code == 1
