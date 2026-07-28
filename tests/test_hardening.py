"""Regressions from the adversarial review of the first build.

Every test here corresponds to a way the gates could be satisfied without doing
the work they claim to prove. They are grouped by the finding they close.
"""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "imagination-brainstorming" / "scripts"))

from engine import content_tokens, distinct_ratio, jaccard, phrase_regex  # noqa: E402


# --- non-Latin scripts were invisible to every comparison ------------------

def test_identical_korean_text_scores_as_identical():
    ko = "이 접근은 병동의 모든 미완료 의무를 하나의 원장으로 옮기고 교대는 일괄 재배정 사건이 된다."
    assert jaccard(ko, ko) == 1.0


def test_different_korean_texts_score_below_the_threshold():
    a = "병동의 모든 미완료 의무를 하나의 원장으로 옮기고 교대는 일괄 재배정이 된다."
    b = "간호사는 환자 곁에서 한 문장을 소리 내어 말하고 아무것도 기록하지 않는다."
    assert jaccard(a, b) < 0.5


@pytest.mark.parametrize("text", ["병동 인계", "病棟の引き継ぎ", "交接班"])
def test_cjk_text_produces_comparable_tokens(text):
    assert content_tokens(text), f"{text} tokenized to nothing"


def test_identical_cjk_approaches_fail_divergence(run, tmp_path, example):
    concept = deepcopy(example)
    ko_summary = ("이 접근은 병동의 미완료 의무 전부를 하나의 원장으로 옮겨 각 항목에 소유자와 만료 시각을 "
                  "붙이고 교대는 일괄 재배정 사건으로 바꾼다. 개별 짝짓기는 사라진다.")
    ko_failure = "소유자 없는 풀은 매립지가 되어 오래된 항목이 무시되고 책임이 흩어지는 방식으로 실패한다."
    for a in concept["approaches"]:
        a["summary"], a["failure_mode"] = ko_summary, ko_failure
    path = tmp_path / "ko.json"
    path.write_text(json.dumps(concept, ensure_ascii=False), encoding="utf-8")
    res = run("divergence_check.py", "--approaches", str(path), "--json")
    assert res.code == 3
    assert any("identical" in f for f in res.json()["failures"])


def test_korean_ban_matches_through_a_particle():
    """대시보드 must fire on 대시보드는; requiring a trailing word boundary made
    the ban list decorative for agglutinative languages."""
    assert phrase_regex("대시보드").search("대시보드는 모든 정보를 한곳에 모읍니다.")


# --- padding met the character minimums ------------------------------------

def test_repeated_filler_scores_low():
    assert distinct_ratio("x" * 300) < 0.3
    assert distinct_ratio("duty owner deadline " * 20) < 0.3


def test_ordinary_prose_scores_high():
    prose = ("The handover assembles itself all shift from orders placed and medication given, "
             "so the nurse only corrects what is wrong in the last ten minutes.")
    assert distinct_ratio(prose) > 0.5


def test_padded_fields_fail_the_gate(gate, concept_path, example):
    concept = deepcopy(example)
    concept["first_use_scene"] = "x" * 300
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("repeated filler" in f for f in res.json()["failures"])


def test_duplicate_premises_fail(gate, concept_path, example):
    concept = deepcopy(example)
    concept["premises"] = [concept["premises"][0]] * 3
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("repeats premises[0]" in f for f in res.json()["failures"])


def test_null_instincts_fail(gate, concept_path, example):
    concept = deepcopy(example)
    concept["banlist_contract"]["model_instincts"] = [None] * 12
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("empty or not text" in f for f in res.json()["failures"])


def test_string_booleans_are_rejected(gate, concept_path, example):
    """'false' is a truthy string; it used to satisfy the unsafe-seat check."""
    concept = deepcopy(example)
    for a in concept["approaches"]:
        a["unsafe_seat"] = "false"
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("must be true or false" in f for f in res.json()["failures"])


def test_invented_frame_ids_fail_the_spec_gate(gate, concept_path, example):
    concept = deepcopy(example)
    for i, a in enumerate(concept["approaches"]):
        a["frame_id"] = f"fake-{i}"
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("unknown frame_id" in f for f in res.json()["failures"])


def test_statements_that_are_not_questions_fail(gate, concept_path, example):
    concept = deepcopy(example)
    concept["open_questions"] = [
        "We should probably look into the legal record situation at some point.",
        "The silent error rate is something the ward would need to think about.",
    ]
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("not phrased as a question" in f for f in res.json()["failures"])


# --- the skeleton was stored and never enforced ----------------------------

def test_a_concept_that_restates_the_skeleton_fails(gate, concept_path, example):
    concept = deepcopy(example)
    skeleton = concept["banlist_contract"]["skeleton"]
    concept["chosen"]["why"] = skeleton + " That is exactly what this design does, and it works."
    concept["chosen"]["forbids"] = skeleton + " Nothing else is ruled out by this design at all."
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("restates the banned skeleton" in f for f in res.json()["failures"])


# --- the user's long exclusions were collected and then ignored ------------

def test_unanswered_user_exclusions_fail(gate, concept_path, example):
    concept = deepcopy(example)
    del concept["banlist_contract"]["manual_checks_cleared"]
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("manual_checks_cleared" in f for f in res.json()["failures"])


def test_a_thin_answer_to_an_exclusion_fails(gate, concept_path, example):
    concept = deepcopy(example)
    concept["banlist_contract"]["manual_checks_cleared"] = [
        {"id": "user-01", "note": "fine"}, {"id": "user-03", "note": "ok"},
    ]
    res = gate(concept_path(concept), "--json")
    assert res.code == 2


# --- counts were caller-controlled ----------------------------------------

def test_divergence_count_cannot_be_lowered(run, references):
    res = run("divergence_check.py", "--approaches", str(references / "example-concept.json"), "--count", "1")
    assert res.code == 1
    assert "cannot be lower than 3" in res.err


def test_deal_cannot_deal_fewer_than_three(run):
    res = run("deal.py", "--brief", "a way to retire an old tool", "--approaches", "2")
    assert res.code == 1
    assert "cannot be lower than 3" in res.err


def test_instinct_minimum_cannot_be_lowered(run, tmp_path, skeleton):
    thin = tmp_path / "thin.txt"
    thin.write_text("a form\na board\n", encoding="utf-8")
    res = run("banlist.py", "--brief", "x", "--instincts", str(thin), "--skeleton", skeleton,
              "--min-instincts", "0")
    assert res.code == 2


# --- malformed ban lists silently disabled the lint ------------------------

@pytest.mark.parametrize("payload", ["{}", "[]", '{"entries": []}', '{"entries": [{"phrase": ""}]}'])
def test_malformed_banlists_are_refused(run, tmp_path, references, payload):
    bad = tmp_path / "bad.json"
    bad.write_text(payload, encoding="utf-8")
    for script, args in (
        ("cliche_lint.py", ["--draft", str(references / "example-concept.md")]),
        ("divergence_check.py", ["--approaches", str(references / "example-concept.json")]),
        ("spec_gate.py", ["--concept", str(references / "example-concept.json"),
                          "--markdown", str(references / "example-concept.md")]),
    ):
        res = run(script, *args, "--banlist", str(bad))
        assert res.code == 1, f"{script} accepted a malformed ban list: {payload}"
        assert "ban list" in res.err


def test_the_schema_cannot_be_swapped(run, tmp_path, references, banlist):
    """A caller-supplied schema could set every floor to zero, leaving a gate
    that reports success without checking anything. The flag is gone."""
    bad = tmp_path / "schema.json"
    bad.write_text(json.dumps({"counts": {}, "min_chars": {}}), encoding="utf-8")
    res = run("spec_gate.py", "--concept", str(references / "example-concept.json"),
              "--markdown", str(references / "example-concept.md"),
              "--banlist", str(banlist), "--schema", str(bad))
    assert res.code == 1, "a mistyped or removed flag is a usage error, not a failed gate"
    assert "unrecognized arguments" in res.err or "--schema" in res.err


# --- the pitch regex flagged ordinary story prose --------------------------

def test_a_scene_is_not_a_pitch(run, tmp_path):
    draft = tmp_path / "story.md"
    draft.write_text("Alice meets Bob at the station, and they argue about the map.\n", encoding="utf-8")
    res = run("cliche_lint.py", "--deck-only", "--draft", str(draft))
    assert res.code == 0, res.out


def test_the_pitch_frame_is_still_caught(run, tmp_path):
    draft = tmp_path / "pitch.md"
    draft.write_text("Basically it is Slack meets Duolingo for hospital wards.\n", encoding="utf-8")
    res = run("cliche_lint.py", "--deck-only", "--draft", str(draft), "--json")
    assert res.code == 3
    assert any(f["id"] in {"x-meets-y", "x-for-y"} for f in res.json()["findings"])


# ===========================================================================
# Second adversarial round: the gate was three checks that never met.
# ===========================================================================

def test_an_unrelated_ban_list_is_rejected(run, tmp_path, references, instincts_file, skeleton):
    """The sidecar claimed consent while the linted contract came from another
    session; nothing compared them."""
    other = tmp_path / "other.txt"
    other.write_text("\n".join(f"an unrelated obvious answer number {i}" for i in range(12)), encoding="utf-8")
    res = run("banlist.py", "--brief", "something else entirely", "--instincts", str(other),
              "--skeleton", "A different structure that shares nothing with the session under test here.",
              "--confirmed", "--out", str(tmp_path))
    assert res.code == 0
    res = run("spec_gate.py", "--concept", str(references / "example-concept.json"),
              "--markdown", str(references / "example-concept.md"),
              "--banlist", str(tmp_path / "banlist.json"), "--json")
    assert res.code == 2
    failures = " ".join(res.json()["failures"])
    assert "skeleton" in failures and "differ" in failures


def test_an_unconfirmed_ban_list_is_rejected(run, tmp_path, references, instincts_file, skeleton, user_file):
    res = run("banlist.py", "--brief", "ward handover", "--instincts", str(instincts_file),
              "--user", str(user_file), "--skeleton", skeleton, "--out", str(tmp_path))
    assert res.code == 0
    res = run("spec_gate.py", "--concept", str(references / "example-concept.json"),
              "--markdown", str(references / "example-concept.md"),
              "--banlist", str(tmp_path / "banlist.json"), "--json")
    assert res.code == 2
    assert any("unconfirmed" in f for f in res.json()["failures"])


def test_zero_width_characters_cannot_hide_the_skeleton(gate, concept_path, example):
    """Joining a sentence with U+200B renders identically and used to tokenize
    to nothing, so the banned skeleton could be reproduced verbatim."""
    concept = deepcopy(example)
    skeleton = concept["banlist_contract"]["skeleton"]
    concept["chosen"]["why"] = "​".join(skeleton) + " That is what this design does, plainly stated."
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    assert any("restates the banned skeleton" in f for f in res.json()["failures"])


def test_varied_character_padding_is_caught():
    """'abc' repeated has three distinct characters and used to score 1.0."""
    assert distinct_ratio("abc" * 100) < 0.3
    assert distinct_ratio("The unit reviewed several options today. " * 4) < 0.3


def test_padding_in_previously_unchecked_fields_fails(gate, concept_path, example):
    concept = deepcopy(example)
    concept["decisions"][0]["why"] = "abc" * 20
    concept["handoff"]["why"] = "def" * 20
    res = gate(concept_path(concept), "--json")
    assert res.code == 2
    failures = " ".join(res.json()["failures"])
    assert "decisions[0].why" in failures and "handoff.why" in failures


@pytest.mark.parametrize("payload", [
    '{"entries": [{"phrase": "neverappears", "tier": "ban"}]}',
    '{"entries": [{"id": "x", "phrase": {}, "tier": "ban"}]}',
    '{"entries": [{"id": "x", "phrase": "y", "tier": "ban"}], "manual_checks": [null]}',
    '{"entries": [{"id": "x", "phrase": "y", "tier": "ban"}], "structural_patterns": [{"id": "p"}]}',
])
def test_ban_list_entries_are_validated(run, tmp_path, references, payload):
    """Shapes that passed the first validation and then crashed downstream, or
    quietly dropped the user's exclusions."""
    bad = tmp_path / "bad.json"
    bad.write_text(payload, encoding="utf-8")
    res = run("spec_gate.py", "--concept", str(references / "example-concept.json"),
              "--markdown", str(references / "example-concept.md"), "--banlist", str(bad))
    assert res.code == 1, res
    assert "ban list" in res.err


def test_duplicate_approach_ids_fail(run, tmp_path, example):
    concept = deepcopy(example)
    concept["approaches"][0]["id"] = concept["approaches"][2]["id"]
    path = tmp_path / "dupe.json"
    path.write_text(json.dumps(concept, ensure_ascii=False), encoding="utf-8")
    res = run("divergence_check.py", "--approaches", str(path), "--json")
    assert res.code == 3
    assert any("share the id" in f for f in res.json()["failures"])


def test_the_unsafe_alias_is_refused(run, tmp_path, example):
    """`unsafe: true` seated an approach in the checker while every documented
    `unsafe_seat` field said false."""
    concept = deepcopy(example)
    for a in concept["approaches"]:
        a["unsafe_seat"] = False
    concept["approaches"][1]["unsafe"] = True
    path = tmp_path / "alias.json"
    path.write_text(json.dumps(concept, ensure_ascii=False), encoding="utf-8")
    res = run("divergence_check.py", "--approaches", str(path), "--json")
    assert res.code == 3
    failures = " ".join(res.json()["failures"])
    assert "alias is not read" in failures and "unsafe seat" in failures


def test_usage_errors_are_not_reported_as_failed_gates(run):
    """argparse exits 2 by default, which is this package's 'gate failed' code;
    an agent seeing that from a typo would start rewriting a fine spec."""
    for script in ("spec_gate.py", "divergence_check.py", "deal.py", "banlist.py", "cliche_lint.py"):
        res = run(script, "--nonsense")
        assert res.code == 1, f"{script} returned {res.code} for a usage error"
