"""Every length floor is a floor on argument, not on Unicode.

The schema says so in its own `units_note` and names the key `min_units`, but
four floors were still counted in code points, so a Korean, Japanese or Chinese
session had to write roughly twice the content of an English one to clear them.
Each test below submits CJK prose measuring exactly the floor - the value the
schema promises passes - and the same field one unit short.
"""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "imagination-brainstorming" / "scripts"))

import spec_gate  # noqa: E402
from engine import load_banlist, load_deck, text_units  # noqa: E402

# Ordinary prose about the shipped example's subject, long enough to trim to any
# floor in the schema. Trimmed rather than repeated, so distinct_ratio stays the
# ratio of real writing.
KO = (
    "야간 근무를 마친 간호사가 스테이션 화면 앞에 서면 지난 열두 시간 동안 남은 의무가 목록으로 떠 있다. "
    "혈액 배양 결과 확인, 통증 조절 재평가, 보호자에게 전달할 퇴원 일정 세 가지가 아직 누구에게도 넘어가지 "
    "않은 상태로 표시된다. 간호사는 첫 줄을 읽고 이미 처리했다고 손짓 한 번으로 지운 뒤, 나머지 두 줄은 "
    "그대로 둔다. 인수받는 동료가 옆에 서서 그 두 줄을 소리 내어 읽고 자기 이름이 붙는 것을 확인한다. "
    "누구도 새 문장을 입력하지 않았고, 화면은 남은 의무만 사람에서 사람으로 옮겼을 뿐이다. 병동 시계가 "
    "일곱 시를 가리키고 두 사람은 각자 침대 쪽으로 흩어진다."
)


def ko(units: int) -> str:
    """Korean prose measuring exactly `units` units, and about half that in code points."""
    out = ""
    for ch in KO:
        if text_units(out + ch) > units:
            break
        out += ch
    # The gate strips its values, so a trailing space would not be counted.
    out = out.rstrip()
    while text_units(out) < units:
        out += "."
    assert text_units(out) == units, f"could not build {units} units"
    assert len(out) < units, "the point of the test is that code points and units differ"
    return out


@pytest.fixture(scope="module")
def schema():
    return load_deck("spec-schema")


@pytest.fixture
def check(banlist: Path, schema):
    frames = load_deck("frames")
    cliches = load_deck("cliches")
    contract = load_banlist(str(banlist))

    def _check(concept: dict) -> str:
        result = spec_gate.check_concept(concept, schema, frames, contract, cliches)
        return " | ".join(result["failures"])

    return _check


def set_premise_why(concept, value):
    concept["premises"][0]["why"] = value


def set_first_use_scene(concept, value):
    concept["first_use_scene"] = value


def set_how_it_differs(concept, value):
    concept["nearest_existing"][0]["how_it_differs"] = value


def set_manual_check_note(concept, value):
    concept["banlist_contract"]["manual_checks_cleared"][0]["note"] = value


CASES = [
    ("premise_why", set_premise_why, "premises[0].why"),
    ("first_use_scene", set_first_use_scene, "first_use_scene"),
    ("how_it_differs", set_how_it_differs, "nearest_existing[0].how_it_differs"),
    ("manual_check_note", set_manual_check_note, "user-01"),
]


@pytest.mark.parametrize("key,setter,label", CASES)
def test_cjk_text_at_the_floor_is_accepted(example, check, schema, key, setter, label):
    concept = deepcopy(example)
    setter(concept, ko(schema["min_units"][key]))
    assert label not in check(concept), f"{key}: CJK text of exactly the floor must pass"


@pytest.mark.parametrize("key,setter,label", CASES)
def test_cjk_text_one_unit_short_is_still_refused(example, check, schema, key, setter, label):
    concept = deepcopy(example)
    setter(concept, ko(schema["min_units"][key] - 1))
    assert label in check(concept), f"{key}: the floor must still be a floor"
