"""The gate must be reading this session's ban contract, not a file shaped like one.

Every test here failed before the contract was replayed at gate time: a
caller-written `--banlist` shrank a 76-phrase lint to whatever its author chose
to include, and because the user's long exclusions live in `manual_checks`,
dropping them discharged every check the user personally asked for.
"""

from __future__ import annotations

import json
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
