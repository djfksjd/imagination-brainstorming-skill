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
    # Padded with a letter rather than a full stop: a run of characters that are
    # neither letters nor digits counts as one unit however long it is, so a
    # second full stop would add nothing and this loop would not terminate.
    while text_units(out) < units:
        out += "n"
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


# --- padding must not buy units -------------------------------------------
#
# `text_units` counted whitespace toward every floor while `distinct_ratio`
# tokenized it away, so two words separated by enough spaces measured whatever
# the author wanted at a perfect 1.00 distinct ratio. Fixed at the measurement
# rather than per field, so every floor in the schema is covered by it.

PADDED = {
    "space": "Nurse" + " " * 240 + "waits",
    "dot": "Nurse" + "." * 240 + "waits",
    "dash": "Nurse" + "-" * 240 + "waits",
    "wide-space": "Nurse" + "　" * 240 + "waits",
}


@pytest.mark.parametrize("kind", sorted(PADDED))
def test_padding_with_non_content_characters_buys_no_units(kind):
    padded = PADDED[kind]
    assert len(padded) >= 250, "the fixture is long enough in code points to clear the floor"
    assert text_units(padded) == 11, f"{kind}: a run of non-content characters counts once"


@pytest.mark.parametrize("kind", sorted(PADDED))
def test_a_padded_field_does_not_clear_its_floor(example, check, kind):
    concept = deepcopy(example)
    concept["first_use_scene"] = PADDED[kind]
    assert "first_use_scene" in check(concept), f"{kind}: padding cleared a 250-unit floor"


# --- scripts that write vowels and tones as combining marks ----------------
#
# Dropping every Mn/Me code point was right for stray zero-width joiners and
# wrong for Thai, Devanagari, Arabic and Hebrew, where the marks are the
# orthography: 282 characters of Thai prose measured 209 units and were refused
# by a 250-unit floor that plain English of the same length cleared.

THAI = (
    "เวลา 19:12 ที่โต๊ะพยาบาล หอผู้ป่วยยังอึกทึกจากการรับผู้ป่วยใหม่ พยาบาลเวรดึกอ่านรายการที่ยังค้างอยู่ "
    "ผู้ป่วยสิบเอ็ดรายบรรทัดละหนึ่งราย บรรทัดที่สี่บอกว่าใบขอตรวจอัลตราซาวด์ยังไม่มีใครรับทราบตั้งแต่บ่ายสองโมงสี่สิบ "
    "เธอลืมไปสนิท บรรทัดที่เจ็ดบอกว่าเตียงเจ็ดไม่มีสิ่งใดค้างและระบบไม่ยอมให้ผ่านไปจนกว่าเธอจะลงชื่อกำกับ"
)

DEVANAGARI = (
    "रात की पाली खत्म होने पर नर्स स्टेशन के परदे पर पिछले बारह घंटों के अधूरे काम एक सूची की तरह दिखते हैं। "
    "खून की जांच का नतीजा देखना, दर्द की दवा का दोबारा आकलन करना, और परिवार को छुट्टी का समय बताना अब भी "
    "किसी के नाम पर दर्ज नहीं है। नर्स पहली पंक्ति पढ़कर उसे पूरा बताती है और बाकी दो वैसी ही छोड़ देती है।"
)

ARABIC = (
    "في الساعة السابعة مساء تقف الممرضة أمام الشاشة في مكتب القسم وتقرأ ما تبقى من الالتزامات خلال "
    "الساعات الاثنتي عشرة الماضية، وهي نتيجة تحليل الدم ومراجعة مسكن الألم وموعد الخروج الذي لم يبلغ "
    "به أحد بعد. تمسح السطر الأول لأنها أنهته بنفسها وتترك السطرين الآخرين لزميلتها كما هما تماما."
)

MARK_SCRIPTS = {"thai": THAI, "devanagari": DEVANAGARI, "arabic": ARABIC}


@pytest.mark.parametrize("script", sorted(MARK_SCRIPTS))
def test_marks_are_orthography_not_decoration(script):
    prose = MARK_SCRIPTS[script]
    units = text_units(prose)
    assert units >= 250, f"{script}: {units} units for {len(prose)} characters of ordinary prose"
    # Close to the code-point count rather than exactly it: NFKC decomposes a
    # handful of composite characters (Thai SARA AM among them) before counting.
    assert units <= len(prose) + 5, f"{script}: marks must not inflate the count either"


@pytest.mark.parametrize("script", sorted(MARK_SCRIPTS))
def test_prose_in_a_mark_using_script_clears_the_scene_floor(example, check, script):
    concept = deepcopy(example)
    concept["first_use_scene"] = MARK_SCRIPTS[script]
    assert "first_use_scene" not in check(concept), f"{script}: legitimate prose was refused"


def test_marks_stacked_on_one_letter_stop_paying():
    """The cap is what keeps 'count the marks' from being a padding vector: two
    marks per base is ordinary orthography, two hundred is decoration."""
    assert text_units("a" + "́" * 200) == 3
