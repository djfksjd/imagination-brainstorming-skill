"""Deck integrity. A corrupt deck degrades every session silently - a frame in
the wrong category or a duplicated id would quietly weaken the guarantee that
three dealt approaches cannot be variants of each other."""

from __future__ import annotations

import json
import re

import pytest

MIN_SIZE = {"question-families": 10, "frames": 30}


def test_all_decks_present(decks):
    assert set(decks) == {"question-families", "frames", "cliches", "spec-schema", "approaches-schema"}


def test_question_families_are_usable(decks):
    families = decks["question-families"]["families"]
    ids = [f["id"] for f in families]
    assert len(ids) == len(set(ids))
    assert len(families) >= MIN_SIZE["question-families"]
    for f in families:
        assert f["prompts"], f"{f['id']} has no example phrasing"
        assert all(p.strip().endswith("?") for p in f["prompts"]), f"{f['id']} has a prompt that is not a question"
        assert len(f["purpose"]) > 20
        assert len(f["listens_for"]) > 20, f"{f['id']} does not say what to listen for"
        assert len(f["anti_pattern"]) > 20, f"{f['id']} does not name the premise-preserving version to avoid"


def test_frames_cover_declared_categories(decks):
    deck = decks["frames"]
    declared = {c["id"] for c in deck["categories"]}
    used = {f["category"] for f in deck["frames"]}
    assert used <= declared, f"undeclared categories: {used - declared}"
    assert declared == used, f"empty categories: {declared - used}"
    assert len(declared) >= 8, "fewer than 8 categories weakens the divergence guarantee"
    ids = [f["id"] for f in deck["frames"]]
    assert len(ids) == len(set(ids))
    assert len(ids) >= MIN_SIZE["frames"]


def test_every_frame_demands_something(decks):
    for f in decks["frames"]["frames"]:
        assert len(f["move"]) > 30, f"{f['id']} does not say what to do"
        assert len(f["must_contain"]) > 10, f"{f['id']} requires nothing of the approach"
        assert len(f["characteristic_failure"]) > 10, f"{f['id']} has no failure hint"


def test_cliche_tiers_and_regexes(decks):
    cliches = decks["cliches"]
    for p in cliches["phrases"]:
        assert p["tier"] in {"ban", "warn"}
        assert p["phrase"].strip()
    for pattern in cliches["structural_patterns"]:
        re.compile(pattern["regex"])  # raises on a malformed deck
        assert pattern["tier"] in {"ban", "warn"}
        assert pattern["why"]
    overlap = set(cliches["hollow_adjectives"]["ban"]) & set(cliches["hollow_adjectives"]["warn"])
    assert not overlap, f"adjective in both tiers: {overlap}"
    assert len(cliches["moves"]) >= 8


def test_spec_schema_is_self_consistent(decks):
    schema = decks["spec-schema"]
    assert schema["counts"]["approaches"] == 3
    assert schema["counts"]["min_open_questions"] >= 2, "a spec with fewer than two open questions has hidden its unknowns"
    assert schema["counts"]["min_premises_broken"] <= schema["counts"]["min_premises"]
    section_ids = [s["id"] for s in schema["required_markdown_sections"]]
    assert len(section_ids) == len(set(section_ids))
    for required in ("brief", "premises", "banlist", "approaches", "concept", "open-questions", "handoff"):
        assert required in section_ids
    assert "stop" in schema["handoff_targets"]
    assert schema["placeholder_markers"]


def test_template_declares_every_required_section(references, decks):
    template = (references / "concept-template.md").read_text(encoding="utf-8")
    for section in decks["spec-schema"]["required_markdown_sections"]:
        assert f"<!-- section: {section['id']} -->" in template, f"template is missing {section['id']}"


def test_template_shows_every_bound_field_inline(references):
    """spec_gate.py fails once per missing <!-- bind: field --> block
    (chosen.forbids, chosen.impossible_now, first_use_scene, every
    open_questions[i] - see spec-schema.json's bindings_note). A user
    following the template should not need to open example-concept.md just to
    discover three of the four exist: a spec built from a template that shows
    only one gets rejected three times over for a value the template itself
    never told them to write. This pins all four inline in the fenced
    template, inside the concept/first-use/open-questions blocks the schema
    requires them in."""
    template = (references / "concept-template.md").read_text(encoding="utf-8")
    fence_start = template.index("```markdown")
    fence_end = template.index("```", fence_start + len("```markdown"))
    body = template[fence_start:fence_end]
    for field in ("chosen.forbids", "chosen.impossible_now", "first_use_scene", "open_questions[0]"):
        assert f"<!-- bind: {field} -->" in body, f"template's fenced example never shows <!-- bind: {field} -->"
    # concept and impossible_now must sit in the concept section, not deferred
    # to trailing prose outside the fenced spec a user would actually copy.
    concept_start = body.index("<!-- section: concept -->")
    first_use_start = body.index("<!-- section: first-use -->")
    open_q_start = body.index("<!-- section: open-questions -->")
    decisions_start = body.index("<!-- section: decisions -->")
    concept_body = body[concept_start:first_use_start]
    first_use_body = body[first_use_start:open_q_start]
    open_q_body = body[open_q_start:decisions_start]
    assert "<!-- bind: chosen.forbids -->" in concept_body
    assert "<!-- bind: chosen.impossible_now -->" in concept_body
    assert "<!-- bind: first_use_scene -->" in first_use_body
    assert "<!-- bind: open_questions[0] -->" in open_q_body
    assert "<!-- bind: open_questions[1] -->" in open_q_body
