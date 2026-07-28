"""One proposal plus two decoys is the standard failure of "here are three
options". These tests pin every way that set gets built."""

from __future__ import annotations

import json
from copy import deepcopy

import pytest


@pytest.fixture
def approaches(example):
    return deepcopy(example["approaches"])


def write(tmp_path, payload):
    path = tmp_path / "approaches.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return str(path)


def test_the_shipped_example_passes(run, references):
    res = run("divergence_check.py", "--approaches", str(references / "example-concept.json"))
    assert res.code == 0, res.out
    assert "alternatives, not variants" in res.out


def test_accepts_a_bare_list(run, tmp_path, approaches):
    assert run("divergence_check.py", "--approaches", write(tmp_path, approaches)).code == 0


def test_restated_summaries_fail(run, tmp_path, approaches):
    approaches[1]["summary"] = approaches[0]["summary"]
    res = run("divergence_check.py", "--approaches", write(tmp_path, approaches), "--json")
    assert res.code == 3
    assert any("restate each other" in f for f in res.json()["failures"])


def test_shared_failure_mode_fails(run, tmp_path, approaches):
    approaches[2]["failure_mode"] = approaches[1]["failure_mode"]
    res = run("divergence_check.py", "--approaches", write(tmp_path, approaches), "--json")
    assert res.code == 3
    assert any("fail the same way" in f for f in res.json()["failures"])


def test_same_category_fails(run, tmp_path, approaches):
    approaches[1]["frame_id"] = "one-percent"  # scale-shift, same as hundred-times
    approaches[2]["frame_id"] = "single-instance"
    res = run("divergence_check.py", "--approaches", write(tmp_path, approaches), "--json")
    assert res.code == 3
    assert any("frame category" in f for f in res.json()["failures"])


def test_missing_unsafe_seat_fails(run, tmp_path, approaches):
    for a in approaches:
        a["unsafe_seat"] = False
    res = run("divergence_check.py", "--approaches", write(tmp_path, approaches), "--json")
    assert res.code == 3
    assert any("unsafe seat" in f for f in res.json()["failures"])


def test_two_unsafe_seats_fail(run, tmp_path, approaches):
    approaches[1]["unsafe_seat"] = True
    res = run("divergence_check.py", "--approaches", write(tmp_path, approaches), "--json")
    assert res.code == 3


def test_thin_decoy_fails_on_detail(run, tmp_path, approaches):
    approaches[0]["summary"] = "A spoken handover at the bedside with the patient present, no artefact produced at all."
    res = run("divergence_check.py", "--approaches", write(tmp_path, approaches), "--json")
    assert res.code == 3
    failures = " ".join(res.json()["failures"])
    assert "far less detail" in failures or "summary" in failures


def test_missing_failure_mode_fails(run, tmp_path, approaches):
    approaches[2]["failure_mode"] = "it might not work"
    res = run("divergence_check.py", "--approaches", write(tmp_path, approaches), "--json")
    assert res.code == 3
    assert any("failure_mode" in f for f in res.json()["failures"])


def test_unknown_frame_fails(run, tmp_path, approaches):
    approaches[0]["frame_id"] = "not-a-frame"
    res = run("divergence_check.py", "--approaches", write(tmp_path, approaches), "--json")
    assert res.code == 3
    assert any("unknown frame_id" in f for f in res.json()["failures"])


def test_category_used_as_frame_id_is_refused_by_name(run, tmp_path, approaches):
    """Reproduces the live-use defect: deal.py's printed output shows each
    approach as '[category] label', and a user who reads only that output
    writes the category into approaches[].frame_id. The category is never a
    valid frame_id (every category holds several frames), so this must be
    refused with a message naming the real candidates - not a bare 'unknown
    frame_id', and never a silent guess at which frame was meant."""
    approaches[0]["frame_id"] = "subtraction"  # a category, not a frame id
    res = run("divergence_check.py", "--approaches", write(tmp_path, approaches), "--json")
    assert res.code == 3
    failures = res.json()["failures"]
    match = [f for f in failures if "frame category, not a frame_id" in f]
    assert match, failures
    # Every frame in the 'subtraction' category must be named as a candidate.
    for candidate in ("delete-the-core", "one-thing-only", "no-interface", "no-storage"):
        assert candidate in match[0]


def test_every_frame_category_is_ambiguous_as_a_frame_id(run, tmp_path, approaches, decks):
    """Guards the fix against a future deck where some category happens to
    contain only one frame - in that case a category token would resolve
    unambiguously and this refusal would need to say so instead of listing
    exactly one candidate as though it were still a choice."""
    frames = decks["frames"]
    by_cat: dict[str, list[str]] = {}
    for f in frames["frames"]:
        by_cat.setdefault(f["category"], []).append(f["id"])
    assert all(len(ids) > 1 for ids in by_cat.values()), (
        "a category with exactly one frame would make this refusal message "
        "misleading; update it to resolve unambiguous categories instead of listing them"
    )


def test_wrong_count_fails(run, tmp_path, approaches):
    res = run("divergence_check.py", "--approaches", write(tmp_path, approaches[:2]), "--json")
    assert res.code == 3
    assert any("2 approaches supplied" in f for f in res.json()["failures"])


def test_banned_phrase_in_an_approach_fails(run, tmp_path, approaches, banlist):
    approaches[1]["summary"] += " In short it is the Uber for ward duties, a frictionless experience."
    res = run("divergence_check.py", "--approaches", write(tmp_path, approaches),
              "--banlist", str(banlist), "--json")
    assert res.code == 3
    assert any("banned phrase" in f for f in res.json()["failures"])


def test_malformed_input_is_a_usage_error(run, tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")
    assert run("divergence_check.py", "--approaches", str(path)).code == 1
