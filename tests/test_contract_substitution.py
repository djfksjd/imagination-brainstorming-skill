"""The gate must be reading this session's ban contract, not a file shaped like one.

Every test here failed before the contract was replayed at gate time: a
caller-written `--banlist` shrank a 76-phrase lint to whatever its author chose
to include, and because the user's long exclusions live in `manual_checks`,
dropping them discharged every check the user personally asked for.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

CLICHE_SENTENCE = "This is a seamless, frictionless solution.\n"


@pytest.fixture
def spec_with_cliches(tmp_path: Path, references: Path) -> str:
    """The shipped spec with two deck-banned words added to the concept section."""
    spec = (references / "example-concept.md").read_text(encoding="utf-8")
    marker = "<!-- section: concept -->"
    assert marker in spec
    spec = spec.replace(marker, marker + "\n\n" + CLICHE_SENTENCE, 1)
    path = tmp_path / "spec-with-cliches.md"
    path.write_text(spec, encoding="utf-8")
    return str(path)


def gate_with(run, references: Path, banlist_path: Path, markdown: str | None = None):
    return run(
        "spec_gate.py",
        "--concept", str(references / "example-concept.json"),
        "--markdown", markdown or str(references / "example-concept.md"),
        "--banlist", str(banlist_path), "--json",
    )


def rewrite(banlist: Path, tmp_path: Path, **changes) -> Path:
    payload = json.loads(banlist.read_text(encoding="utf-8"))
    payload.update(changes)
    path = tmp_path / "edited-banlist.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def test_a_hand_written_contract_cannot_stand_in_for_the_session_one(
    run, tmp_path, references, spec_with_cliches
):
    """One dummy entry used to pass a spec the genuine 76-entry contract failed."""
    fake = tmp_path / "fake-banlist.json"
    fake.write_text(json.dumps({
        "user_confirmed": True,
        "entries": [{"id": "zz", "phrase": "zzzqqq", "tier": "ban"}],
    }), encoding="utf-8")
    res = gate_with(run, references, fake, spec_with_cliches)
    assert res.code == 2, res
    failures = " ".join(res.json()["failures"])
    assert "not the contract this session built" in failures
    assert "banned phrase" in failures, "the bundled deck must be linted whatever contract is passed"


def test_the_bundled_cliche_deck_is_enforced_even_when_the_contract_omits_it(
    run, tmp_path, references, banlist, spec_with_cliches
):
    """A contract stripped of its deck entries is still linted against the deck."""
    payload = json.loads(banlist.read_text(encoding="utf-8"))
    trimmed = rewrite(
        banlist, tmp_path,
        entries=[e for e in payload["entries"] if e.get("source") != "deck"],
        structural_patterns=[],
    )
    res = gate_with(run, references, trimmed, spec_with_cliches)
    assert res.code == 2, res
    failures = " ".join(res.json()["failures"])
    assert "banned phrase" in failures
    assert "seamless" in failures and "frictionless" in failures
    assert "bundled cliche deck" in failures


def test_dropping_the_manual_checks_does_not_discharge_them(run, tmp_path, references, banlist):
    """The user's long exclusions cannot be matched mechanically, so deleting
    them from the file used to be enough to make them stop being asked."""
    trimmed = rewrite(banlist, tmp_path, manual_checks=[])
    res = gate_with(run, references, trimmed)
    assert res.code == 2, res
    failures = " ".join(res.json()["failures"])
    assert "long exclusions" in failures


def test_dropping_the_instinct_bans_is_refused(run, tmp_path, references, banlist):
    payload = json.loads(banlist.read_text(encoding="utf-8"))
    trimmed = rewrite(
        banlist, tmp_path,
        entries=[e for e in payload["entries"] if e.get("group") != "first-instinct"],
    )
    res = gate_with(run, references, trimmed)
    assert res.code == 2, res
    assert any("phrase(s) the sidecar says were burned" in f for f in res.json()["failures"])


def test_a_contract_with_no_skeleton_is_refused(run, tmp_path, references, banlist):
    """An absent field used to skip the comparison rather than fail it, so a
    stripped-down file was safer to pass than an honest one."""
    trimmed = rewrite(banlist, tmp_path, skeleton="")
    res = gate_with(run, references, trimmed)
    assert res.code == 2, res
    assert any("names no skeleton" in f for f in res.json()["failures"])


def test_releases_are_limited_to_the_deck(run, tmp_path, references, banlist):
    """`allowed` releases a cliche the user asked for; it can never be used to
    release an instinct, a user exclusion, or an id that does not exist."""
    trimmed = rewrite(banlist, tmp_path, allowed=["instinct-01", "not-a-cliche-id"])
    res = gate_with(run, references, trimmed)
    assert res.code == 2, res
    assert any("not in the cliche deck" in f for f in res.json()["failures"])


# --- the file being judged cannot grant itself an exemption ----------------


def test_the_contract_cannot_release_a_deck_ban_from_the_lint(
    run, tmp_path, references, banlist, spec_with_cliches
):
    """`allowed` was read from the file under test, so naming two cliche ids in
    it released those cliches from the verdict. This made the gate strictly
    weaker than the version before the replay was added, on exactly the phrases
    the replay exists to keep out."""
    released = rewrite(banlist, tmp_path, allowed=["hollow-seamless", "hollow-frictionless"])
    res = gate_with(run, references, released, spec_with_cliches)
    assert res.code == 2, res
    failures = " ".join(res.json()["failures"])
    assert "banned phrase" in failures
    assert "seamless" in failures and "frictionless" in failures
    warnings = " ".join(res.json()["warnings"])
    assert "does not honour releases" in warnings, "a release must be reported, not silently dropped"


def test_a_release_is_still_a_reason_for_an_entry_to_be_absent(
    run, tmp_path, references, banlist
):
    """The other half of the same rule: `banlist.py --allow` writes a file with
    the entry removed, and the replay must accept that rather than report the
    deck as incomplete. The phrase is still linted; only the completeness check
    is relaxed, and only by the file's own account of itself."""
    payload = json.loads(banlist.read_text(encoding="utf-8"))
    released = rewrite(
        banlist, tmp_path,
        allowed=["gamification"],
        entries=[e for e in payload["entries"] if e.get("id") != "gamification"],
    )
    res = gate_with(run, references, released)
    failures = " ".join(res.json()["failures"])
    assert "bundled cliche deck" not in failures, failures


def test_a_supplied_entry_cannot_displace_the_bundled_one_by_id(
    run, tmp_path, references, banlist, spec_with_cliches
):
    """Dedup was by id with the caller's copy first, so a contract carrying
    `hollow-seamless` at tier `warn` deleted the deck's ban-tier entry."""
    payload = json.loads(banlist.read_text(encoding="utf-8"))
    for entry in payload["entries"]:
        if entry.get("id") in ("hollow-seamless", "hollow-frictionless"):
            entry["tier"] = "warn"
    demoted = rewrite(banlist, tmp_path, entries=payload["entries"])
    res = gate_with(run, references, demoted, spec_with_cliches)
    assert res.code == 2, res
    failures = " ".join(res.json()["failures"])
    assert "seamless" in failures and "frictionless" in failures


def test_a_supplied_pattern_cannot_displace_the_bundled_one_by_id(
    run, tmp_path, references, banlist
):
    """Same shape, structural patterns: setting `cross-between` to a regex that
    never matches used to delete a shipped structural ban. That pattern rather
    than `x-for-y` because no phrase entry duplicates it, so the pattern is the
    only thing standing between this sentence and a pass."""
    spec = (references / "example-concept.md").read_text(encoding="utf-8")
    marker = "<!-- section: concept -->"
    spec = spec.replace(marker, marker + "\n\nIt is a cross between a checklist and a conversation.\n", 1)
    path = tmp_path / "spec-cross-between.md"
    path.write_text(spec, encoding="utf-8")

    payload = json.loads(banlist.read_text(encoding="utf-8"))
    control = gate_with(run, references, banlist, str(path))
    assert control.code == 2, "the control must fail, or the fixture proves nothing"

    for pattern in payload["structural_patterns"]:
        if pattern.get("id") == "cross-between":
            pattern["regex"] = "$^"
    neutered = rewrite(banlist, tmp_path, structural_patterns=payload["structural_patterns"])
    res = gate_with(run, references, neutered, str(path))
    assert res.code == 2, res
    assert "banned phrase" in " ".join(res.json()["failures"])


# --- one written answer discharges one exclusion ---------------------------


def test_two_manual_checks_sharing_an_id_are_refused(run, tmp_path, references, banlist):
    """Replay verifies the checks by statement, but enforcement joins answers to
    checks by an id neither file has to keep unique, so one note discharged
    both of the user's long exclusions."""
    payload = json.loads(banlist.read_text(encoding="utf-8"))
    assert len(payload["manual_checks"]) >= 2, "the fixture needs two long exclusions"
    for check in payload["manual_checks"]:
        check["id"] = "user-01"
    duplicated = rewrite(banlist, tmp_path, manual_checks=payload["manual_checks"])
    res = gate_with(run, references, duplicated)
    assert res.code == 2, res
    assert any("reuses manual check id" in f for f in res.json()["failures"])


def test_two_answers_sharing_an_id_are_refused(run, tmp_path, references, banlist, example):
    """The mirror image: two notes under one id leave the other check unanswered
    while the map looks full."""
    from copy import deepcopy

    concept = deepcopy(example)
    cleared = concept["banlist_contract"]["manual_checks_cleared"]
    assert len(cleared) >= 2
    first = cleared[0]["id"]
    for entry in cleared:
        entry["id"] = first
    path = tmp_path / "concept-dup-answers.json"
    path.write_text(json.dumps(concept, ensure_ascii=False), encoding="utf-8")
    res = run("spec_gate.py", "--concept", str(path),
              "--markdown", str(references / "example-concept.md"),
              "--banlist", str(banlist), "--json")
    assert res.code == 2, res
    assert any("manual_checks_cleared reuses id" in f for f in res.json()["failures"])


# --- the contract must belong to the session it is gating ------------------


def test_a_contract_built_for_another_brief_is_refused(run, tmp_path, references, instincts_file,
                                                       user_file, skeleton):
    """Nothing compared the two briefs, so a contract built for a bakery launch
    validated a concept about a hospital ward."""
    res = run("banlist.py", "--brief", "a launch campaign for a bakery",
              "--instincts", str(instincts_file), "--user", str(user_file),
              "--skeleton", skeleton, "--confirmed", "--out", str(tmp_path / "bakery"))
    assert res.code == 0, res
    gate = gate_with(run, references, tmp_path / "bakery" / "banlist.json")
    assert gate.code == 2, gate
    assert any("built for a different brief" in f for f in gate.json()["failures"])


def test_a_contract_with_no_brief_is_refused(run, tmp_path, references, banlist):
    trimmed = rewrite(banlist, tmp_path, brief="")
    res = gate_with(run, references, trimmed)
    assert res.code == 2, res
    assert any("names no brief" in f for f in res.json()["failures"])


# --- what the brief join can and cannot establish --------------------------
#
# It was a containment ratio at 0.5 between the ban list's brief and the
# sidecar's free-form one, and it failed in both directions at once: a ban list
# whose brief was the single word "ward" passed, because one word is contained
# in every longer brief, and an honest rewording of the same brief in synonyms
# was refused. A word-overlap score cannot establish provenance. What the gate
# checks now is that the two files record the same brief string, which is the
# join the skeleton already uses, and that the string names a subject.


def test_a_one_word_brief_no_longer_slips_a_contract_through(run, tmp_path, references, banlist):
    trimmed = rewrite(banlist, tmp_path, brief="ward")
    res = gate_with(run, references, trimmed)
    assert res.code == 2, res
    failures = " | ".join(res.json()["failures"])
    assert "names a word rather than a subject" in failures


def test_a_contract_whose_brief_differs_from_the_sidecar_is_refused(run, tmp_path, references, banlist):
    trimmed = rewrite(banlist, tmp_path, brief="a way for our clinic to hand over patients")
    res = gate_with(run, references, trimmed)
    assert res.code == 2, res
    assert any("different brief than the one concept.json records" in f for f in res.json()["failures"])


def test_rewording_the_concepts_own_brief_is_a_warning_not_a_failure(run, tmp_path, references,
                                                                     banlist, example):
    """The honest half: the sidecar's `brief` restates and expands the ask, so
    it is allowed to share no vocabulary with the contract's one-line version."""
    concept = deepcopy(example)
    concept["brief"] = (
        "Transferring clinical responsibility between nursing teams at changeover, so that whatever is "
        "still owed to a patient moves from one named person to another without being retyped."
    )
    path = tmp_path / "reworded.json"
    path.write_text(json.dumps(concept, ensure_ascii=False), encoding="utf-8")
    res = run("spec_gate.py", "--concept", str(path),
              "--markdown", str(references / "example-concept.md"),
              "--banlist", str(banlist), "--json")
    assert res.code == 0, res.out
    assert any("share little vocabulary" in w for w in res.json()["warnings"])


def test_a_sidecar_that_records_no_brief_is_refused(run, tmp_path, references, banlist, example):
    concept = deepcopy(example)
    del concept["banlist_contract"]["brief"]
    path = tmp_path / "nobrief.json"
    path.write_text(json.dumps(concept, ensure_ascii=False), encoding="utf-8")
    res = run("spec_gate.py", "--concept", str(path),
              "--markdown", str(references / "example-concept.md"),
              "--banlist", str(banlist), "--json")
    assert res.code == 2
    assert any("banlist_contract.brief: missing" in f for f in res.json()["failures"])


# --- who has to write a manual-check note ----------------------------------
#
# The rule was "every long entry", which made every model instinct longer than
# six words a mandatory written note. SKILL.md, concept-template.md and the
# shipped example all say only the user's exclusions need one, and the shipped
# product example carries zero model instincts in manual_checks while a
# narrative brief produces twelve - product instincts are short noun phrases
# and story instincts are clauses. The instructions describe the design; the
# rule was the thing that disagreed with them.


def long_instincts(n: int = 12) -> list[str]:
    return [
        f"a village that sacrifices one child a year to the thing in the woods, told for the {i}th time"
        for i in range(1, n + 1)
    ]


@pytest.fixture
def narrative_contract(run, tmp_path: Path, skeleton: str):
    """A contract whose model instincts are all clauses, as they are outside a
    product brief."""
    instincts = tmp_path / "narrative.txt"
    instincts.write_text("\n".join(long_instincts()) + "\n", encoding="utf-8")
    user = tmp_path / "user.txt"
    user.write_text("nothing that adds screen time at the bedside\n", encoding="utf-8")
    res = run("banlist.py", "--brief", "a way for our ward to hand over shifts",
              "--instincts", str(instincts), "--user", str(user), "--skeleton", skeleton,
              "--confirmed", "--out", str(tmp_path / "narrative"))
    assert res.code == 0, res
    return tmp_path / "narrative" / "banlist.json"


def gate_narrative(run, tmp_path, references, example, contract, cleared):
    concept = deepcopy(example)
    concept["banlist_contract"]["model_instincts"] = long_instincts()
    concept["banlist_contract"]["user_exclusions"] = ["nothing that adds screen time at the bedside"]
    concept["banlist_contract"]["manual_checks_cleared"] = cleared
    path = tmp_path / "narrative-concept.json"
    path.write_text(json.dumps(concept, ensure_ascii=False), encoding="utf-8")
    return run("spec_gate.py", "--concept", str(path),
               "--markdown", str(references / "example-concept.md"),
               "--banlist", str(contract), "--json")


def test_long_model_instincts_are_a_warning_not_twelve_failures(run, tmp_path, references, example,
                                                                narrative_contract):
    cleared = [{"id": "user-01", "note": "No screen is added at the bedside; the ward's paper board carries it."}]
    res = gate_narrative(run, tmp_path, references, example, narrative_contract, cleared)
    assert res.code == 0, res.out
    verdict = res.json()
    assert not any("instinct-" in f for f in verdict["failures"]), verdict["failures"]
    assert any("long instincts" in w and "reread rather than a failure" in w for w in verdict["warnings"])


def test_the_users_own_long_exclusion_is_still_required(run, tmp_path, references, example,
                                                        narrative_contract):
    res = gate_narrative(run, tmp_path, references, example, narrative_contract, [])
    assert res.code == 2, res.out
    assert any("user-01" in f and "no note saying how the concept avoids it" in f
               for f in res.json()["failures"])
