"""The floors are calibrated, not scaled.

An earlier version of this branch multiplied every floor by 0.8, on the
reasoning that dropping word gaps costs a text about a fifth of its units. That
holds for a script that has word gaps and for nothing else: measured on the same
passage, the new function returns 0.82 of the old count in Latin and 0.98 in
Thai, so a flat 0.8 loosened Japanese, Chinese and Thai by roughly a fifth while
leaving Latin at parity.

So the floors are measured instead. One passage - the thinnest first-use scene
worth accepting - is translated into eight scripts below, together with the same
subject written as a flat description rather than a scene, which is what the
floor exists to catch. Both are measured under the function that actually runs.
"""

from __future__ import annotations

from copy import deepcopy

import pytest

ACCEPT = {
"latin": "At seven in the evening the nurse stops at the station screen. The fourth line says an ultrasound request has been unacknowledged since twenty to three, which she had forgotten. She clears it, then stands for a moment over the seventh line, which claims nothing is outstanding for bed seven, and walks over to look before she puts her name against it.",
"korean": "저녁 일곱 시, 간호사가 스테이션 화면 앞에 선다. 네 번째 줄에는 두 시 사십 분부터 아무도 확인하지 않은 초음파 요청이 떠 있고, 그는 그것을 까맣게 잊고 있었다. 그 줄을 지운 뒤 일곱 번째 줄 앞에서 잠시 멈춘다. 칠 번 침대에는 남은 일이 없다고 적혀 있고, 그는 이름을 붙이기 전에 직접 가서 확인하고 온다.",
"japanese": "午後七時、看護師がステーションの画面の前で足を止める。四行目には二時四十分から誰も確認していない超音波の依頼が残っていて、彼女はそれをすっかり忘れていた。その行を消したあと、七行目の前で少し立ち止まる。七番のベッドには残った仕事がないと書かれていて、彼女は自分の名前を入れる前に実際に見に行く。",
"chinese": "晚上七点，护士在护士站的屏幕前停下。第四行写着一份从两点四十起就没人确认的超声申请，她已经完全忘了这回事。她把那一行清掉，又在第七行前停了一会儿：上面说七号床没有未了的事，她在署名之前先走过去看了一眼。",
"thai": "เวลาหนึ่งทุ่ม พยาบาลหยุดอยู่หน้าจอที่โต๊ะพยาบาล บรรทัดที่สี่บอกว่าใบขอตรวจอัลตราซาวด์ยังไม่มีใครรับทราบตั้งแต่บ่ายสองโมงสี่สิบ เธอลืมไปสนิท เธอลบบรรทัดนั้นแล้วยืนนิ่งอยู่ครู่หนึ่งตรงบรรทัดที่เจ็ด ซึ่งบอกว่าเตียงเจ็ดไม่มีสิ่งใดค้าง เธอเดินไปดูก่อนจะลงชื่อกำกับ",
"devanagari": "शाम के सात बजे नर्स स्टेशन के परदे के सामने रुकती है। चौथी पंक्ति कहती है कि दो बजकर चालीस मिनट से अल्ट्रासाउंड की एक मांग को किसी ने स्वीकार नहीं किया, और वह इसे पूरी तरह भूल चुकी थी। वह उस पंक्ति को हटाती है, फिर सातवीं पंक्ति पर एक पल ठहरती है, जो कहती है कि सात नंबर बिस्तर पर कुछ बाकी नहीं है, और नाम लिखने से पहले खुद जाकर देखती है।",
"hebrew": "בשעה שבע בערב האחות עוצרת מול המסך בעמדת האחיות. השורה הרביעית אומרת שבקשה לאולטרסאונד לא אושרה מאז שתיים וארבעים, והיא שכחה מזה לגמרי. היא מוחקת את השורה, ואז עומדת רגע מול השורה השביעית, שאומרת שלא נשאר דבר במיטה שבע, והולכת לבדוק לפני שהיא רושמת את שמה.",
"arabic": "في السابعة مساء تقف الممرضة أمام الشاشة في مكتب القسم. يقول السطر الرابع إن طلب تصوير بالموجات فوق الصوتية لم يستلمه أحد منذ الثانية والأربعين دقيقة، وهي نسيته تماما. تمسح ذلك السطر ثم تتوقف لحظة عند السطر السابع الذي يقول إنه لا شيء متبق في السرير السابع، وتذهب لتنظر بنفسها قبل أن تكتب اسمها.",
}

REJECT = {
"latin": "The nurse uses the screen at the end of the shift and it works well for the ward.",
"korean": "간호사는 근무가 끝날 때 화면을 사용하고, 그것은 병동에 잘 맞는다.",
"japanese": "看護師は勤務の終わりに画面を使い、それは病棟にとってうまく機能する。",
"chinese": "护士在交班时使用这块屏幕，它对病房来说很好用。",
"thai": "พยาบาลใช้จอนี้ตอนสิ้นเวรและมันทำงานได้ดีสำหรับหอผู้ป่วย",
"devanagari": "नर्स पाली के अंत में परदे का उपयोग करती है और यह वार्ड के लिए ठीक काम करता है।",
"hebrew": "האחות משתמשת במסך בסוף המשמרת וזה עובד טוב במחלקה.",
"arabic": "تستخدم الممرضة الشاشة في نهاية المناوبة وهي تعمل جيدا للقسم.",
}


SCRIPTS = sorted(ACCEPT)


@pytest.mark.parametrize("script", SCRIPTS)
def test_the_thinnest_acceptable_scene_passes_in_every_script(example, check, script):
    """Chinese fails this against the floor of 200 that a flat 0.8 rescale
    produced: a minimal scene measures 186 units there and 283 in Latin, because
    the same content is worth about a third fewer units in Chinese."""
    concept = deepcopy(example)
    concept["first_use_scene"] = ACCEPT[script]
    assert "first_use_scene" not in check(concept), f"{script}: a legitimate minimal scene was refused"


@pytest.mark.parametrize("script", SCRIPTS)
def test_a_description_rather_than_a_scene_is_refused_in_every_script(example, check, script):
    concept = deepcopy(example)
    concept["first_use_scene"] = REJECT[script]
    assert "first_use_scene" in check(concept), f"{script}: filler cleared the scene floor"


def test_one_number_separates_them_in_all_eight_scripts(schema):
    """What makes a single floor honest here: the two populations do not overlap.
    If they ever do, the floor has to be replaced by something other than length,
    not moved until the fixtures agree."""
    from engine import text_units
    accepts = [text_units(v) for v in ACCEPT.values()]
    rejects = [text_units(v) for v in REJECT.values()]
    assert max(rejects) < min(accepts), "no single floor can separate these"
    floor = schema["min_units"]["first_use_scene"]
    assert max(rejects) < floor <= min(accepts), (
        f"floor {floor} must sit above every description ({max(rejects)}) and at or below the "
        f"thinnest legitimate scene ({min(accepts)})"
    )
