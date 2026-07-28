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
    bad.write_text(json.dumps({"counts": {}, "min_units": {}}), encoding="utf-8")
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


# ===========================================================================
# Third round, found by using the skill on a real Korean brief: the binding
# between the written spec and its sidecar passed on token overlap alone.
# ===========================================================================

def test_token_overlap_is_not_containment():
    """In a long spec the words of any one paragraph are scattered through the
    rest, so a bag-of-tokens score passes even when the paragraph was replaced."""
    from engine import coverage, passage_coverage  # noqa: PLC0415

    passage = ("근거 레코드에 없는 사실과 숫자를 문장에 만들어 넣는 일을 금지한다. "
               "숨겨진 가중치와 설명할 수 없는 종합점수를 금지한다.")
    scattered = ("이 문서는 근거와 레코드를 다룬다. 숫자와 사실은 문장에서 확인된다. "
                 "가중치는 숨겨지지 않으며 종합점수는 설명할 수 있어야 한다. 금지 사항은 따로 있다.")
    assert coverage(passage, scattered) > 0.5, "the old check would have passed this"
    assert passage_coverage(passage, scattered) < 0.5, "the passage is not actually present"
    assert passage_coverage(passage, "머리말. " + passage + " 꼬리말.") == 1.0


def test_a_spec_missing_the_refusal_fails(gate, concept_path, example, tmp_path, spec_md):
    """Swap the whole concept section for unrelated prose: the refusal is gone
    from the document while every other binding is untouched."""
    import re as _re  # noqa: PLC0415
    from pathlib import Path as _Path  # noqa: PLC0415

    spec = _Path(spec_md).read_text(encoding="utf-8")
    marks = list(_re.finditer(r"<!--\s*section:\s*([\w-]+)\s*-->", spec, _re.IGNORECASE))
    start = next(m for m in marks if m.group(1) == "concept")
    end = next(m for m in marks if m.start() > start.start())
    filler = ("The team reviewed the ward rota and the existing paperwork over several weeks and agreed "
              "that the arrangement suits the unit as it currently stands. " * 3)
    md = tmp_path / "swapped.md"
    md.write_text(spec[:start.end()] + "\n" + filler + "\n\n" + spec[end.start():], encoding="utf-8")
    res = gate(concept_path(example), "--markdown", str(md), "--json")
    assert res.code == 2
    assert any("no <!-- bind: chosen.forbids -->" in f for f in res.json()["failures"])


def test_the_tail_of_a_passage_is_checked():
    """The stepped range stops early unless the length is a multiple of the
    step, so up to window-1 characters at the end went unchecked - and the end
    of a sentence is where its conclusion and its negation live."""
    from engine import passage_coverage
    original = "the system must never invent a figure absent from the record, and it is forbidden"
    reversed_tail = original[:62] + ", and it is expressly permitted"
    assert len(reversed_tail) % 12 != 0, "the hole only opens when the length is not a multiple of the step"
    assert passage_coverage(original, original) == 1.0
    # Before the tail window was added this scored 1.0: every stepped window
    # fell inside the unchanged first 62 characters.
    assert passage_coverage(reversed_tail, original) < 1.0, "the tail was never being compared"


def test_a_binding_outside_its_own_section_is_caught(run, tmp_path, references, banlist):
    """A refusal quoted in the ban list, or logged in the decision record as
    rejected, is not the same as one the spec makes."""
    import re as _re  # noqa: PLC0415

    markdown = (references / "example-concept.md").read_text(encoding="utf-8")
    block = _re.search(r"<!-- bind: chosen\.forbids -->.*?<!-- /bind -->", markdown, _re.S).group(0)
    moved = markdown.replace(block, "The refusal used to be stated here, at length, in the spec's own voice.")
    moved = moved.replace("<!-- section: decisions -->", f"<!-- section: decisions -->\n\n{block}\n", 1)
    path = tmp_path / "moved.md"
    path.write_text(moved, encoding="utf-8")
    res = run("spec_gate.py", "--concept", str(references / "example-concept.json"),
              "--markdown", str(path), "--banlist", str(banlist), "--json")
    assert res.code == 2
    assert any("is not inside the 'concept' section" in f for f in res.json()["failures"])


def test_a_quoted_assertion_does_not_count_as_one(run, tmp_path, references, banlist):
    """The concrete case: the words are present while the sentence around them
    rejects the proposition. A similarity score cannot tell those apart."""
    import re as _re  # noqa: PLC0415

    markdown = (references / "example-concept.md").read_text(encoding="utf-8")
    quoted = _re.sub(
        r"(<!-- bind: chosen\.forbids -->\n)(.*?)(\n<!-- /bind -->)",
        lambda m: m.group(1) + "> " + m.group(2).replace("\n", "\n> ") + m.group(3),
        markdown, count=1, flags=_re.S)
    path = tmp_path / "quoted.md"
    path.write_text(quoted, encoding="utf-8")
    res = run("spec_gate.py", "--concept", str(references / "example-concept.json"),
              "--markdown", str(path), "--banlist", str(banlist), "--json")
    assert res.code == 2
    assert any("in its own voice" in f for f in res.json()["failures"])


def test_the_gate_grants_no_exceptions_at_verdict_time(run, references, banlist):
    """--allow let the same party the verdict is about release the finding that
    was about to fail. Exceptions belong in the contract, made once, in front
    of the user."""
    res = run("spec_gate.py", "--concept", str(references / "example-concept.json"),
              "--markdown", str(references / "example-concept.md"),
              "--banlist", str(banlist), "--allow", "cyberpunk")
    assert res.code == 1
    assert "unrecognized arguments" in res.err

def test_cjk_prose_is_not_held_to_twice_the_bar():
    """A floor asks for an amount of argument, not an amount of Unicode. One
    Hangul syllable carries roughly what two Latin letters carry."""
    from engine import text_units
    assert text_units("column") == 6
    assert text_units("기둥") == 4
    assert text_units("ＡＢＣ") == 3, "fullwidth Latin must not inflate the count"
    # Tightened twice, never relaxed: a run of characters that are neither
    # letters nor digits first went from ten units to one, and now to zero -
    # punctuation and whitespace pay nothing at all. The property this line has
    # always asserted - decoration must not clear a prose floor - holds more
    # strongly at each step.
    assert text_units("★" * 10) == 0, "decoration must not clear a prose floor"
