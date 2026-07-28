"""The deal is the part of the session the model does not control. These tests
pin the properties the rest of the skill leans on: it is reproducible, the
dealt frames cannot produce variants, exactly one unsafe seat exists, and a
later round deals fresh material instead of the same favourites."""

from __future__ import annotations

import json

BRIEF = "a way for a hospital ward to hand over shifts"


def deal(run_fixture, *args):
    res = run_fixture("deal.py", "--brief", BRIEF, "--json", *args)
    assert res.code == 0, res
    return res.json()


def test_same_inputs_give_the_same_deal(run):
    assert deal(run) == deal(run)


def test_salt_changes_the_deal(run):
    assert deal(run)["approaches"] != deal(run, "--salt", "second attempt")["approaches"]


def test_different_brief_changes_the_deal(run):
    other = run("deal.py", "--brief", "a way to retire an old internal tool", "--json")
    assert other.code == 0
    assert other.json()["approaches"] != deal(run)["approaches"]


def test_frames_come_from_disjoint_categories(run):
    for round_index in ("1", "2", "3", "4"):
        payload = deal(run, "--run", round_index)
        cats = [a["category"] for a in payload["approaches"]]
        assert len(cats) == len(set(cats)), f"round {round_index} dealt two frames from one category"


def test_exactly_one_unsafe_seat(run):
    for round_index in ("1", "2", "3"):
        payload = deal(run, "--run", round_index)
        assert sum(1 for a in payload["approaches"] if a["unsafe_seat"]) == 1


def test_unsafe_seat_rotates_between_rounds(run):
    seats = []
    for round_index in ("1", "2", "3"):
        payload = deal(run, "--run", round_index)
        seats.append(next(a["slot"] for a in payload["approaches"] if a["unsafe_seat"]))
    assert len(set(seats)) > 1, "the same slot always carries the uncomfortable option"


def test_later_rounds_deal_fresh_frames(run):
    first = {a["frame_id"] for a in deal(run, "--run", "1")["approaches"]}
    second = {a["frame_id"] for a in deal(run, "--run", "2")["approaches"]}
    third = {a["frame_id"] for a in deal(run, "--run", "3")["approaches"]}
    assert not (first & second)
    assert not (second & third)
    assert not (first & third)


def test_question_families_carry_their_guidance(run):
    payload = deal(run, "--questions", "4")
    assert len(payload["question_families"]) == 4
    for f in payload["question_families"]:
        assert f["listens_for"] and f["anti_pattern"] and f["prompts"]


def test_too_many_approaches_fails_rather_than_repeating_a_category(run):
    res = run("deal.py", "--brief", BRIEF, "--approaches", "99")
    assert res.code == 1
    assert "variants" in res.err


def test_single_approach_is_refused(run):
    res = run("deal.py", "--brief", BRIEF, "--approaches", "1")
    assert res.code == 1


def test_too_many_questions_fails(run):
    res = run("deal.py", "--brief", BRIEF, "--questions", "99")
    assert res.code == 1


def test_missing_brief_fails(run):
    assert run("deal.py", "--run", "1").code == 1


def test_bad_run_fails(run):
    assert run("deal.py", "--brief", BRIEF, "--run", "0").code == 1


def test_out_writes_deal_json(run, tmp_path):
    res = run("deal.py", "--brief", BRIEF, "--out", str(tmp_path))
    assert res.code == 0
    payload = json.loads((tmp_path / "deal.json").read_text(encoding="utf-8"))
    assert payload["brief"] == BRIEF
    assert len(payload["approaches"]) == 3


def test_list_frames(run):
    res = run("deal.py", "--list-frames")
    assert res.code == 0
    assert "subtraction" in res.out and "failure-first" in res.out


def test_human_output_carries_the_rules(run):
    res = run("deal.py", "--brief", BRIEF)
    assert res.code == 0
    assert "unsafe seat" in res.out
    assert "One question per message" in res.out or "one question per message" in res.out.lower()
