"""The ban contract is what makes "avoid the obvious" checkable rather than
aspirational. The gates that matter here are the two ways it can be faked: too
few instincts, and no named skeleton."""

from __future__ import annotations

import json


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_builds_from_instincts_and_deck(run, tmp_path, instincts_file, skeleton):
    res = run("banlist.py", "--brief", "ward handover", "--instincts", str(instincts_file),
              "--skeleton", skeleton, "--out", str(tmp_path))
    assert res.code == 0, res
    payload = load(tmp_path / "banlist.json")
    ids = {e["id"] for e in payload["entries"]}
    assert "uber-for" in ids, "deck defaults missing"
    assert any(i.startswith("instinct-") for i in ids), "model instincts missing"
    assert any(i.startswith("hollow-") for i in ids), "hollow adjectives missing"
    assert payload["counts"]["model_instincts"] == 12


def test_short_instinct_list_is_refused_with_code_2(run, tmp_path, skeleton):
    thin = tmp_path / "thin.txt"
    thin.write_text("a form\na board\n", encoding="utf-8")
    res = run("banlist.py", "--brief", "x", "--instincts", str(thin), "--skeleton", skeleton, "--out", str(tmp_path))
    assert res.code == 2
    assert "still on the table" in res.err


def test_missing_skeleton_is_refused_with_code_2(run, tmp_path, instincts_file):
    res = run("banlist.py", "--brief", "x", "--instincts", str(instincts_file), "--skeleton", "a form")
    assert res.code == 2
    assert "thirteenth version" in res.err


def test_unconfirmed_contract_is_recorded_as_such(run, tmp_path, instincts_file, skeleton):
    res = run("banlist.py", "--brief", "x", "--instincts", str(instincts_file),
              "--skeleton", skeleton, "--out", str(tmp_path))
    assert res.code == 0
    assert load(tmp_path / "banlist.json")["user_confirmed"] is False
    assert "NEXT: show these to the user as exclusions" in res.out


def test_confirmed_flag_signs_the_contract(run, tmp_path, instincts_file, skeleton):
    run("banlist.py", "--brief", "x", "--instincts", str(instincts_file),
        "--skeleton", skeleton, "--confirmed", "--out", str(tmp_path))
    assert load(tmp_path / "banlist.json")["user_confirmed"] is True


def test_user_exclusions_are_merged_and_labelled(run, tmp_path, instincts_file, skeleton):
    user = tmp_path / "user.txt"
    user.write_text("- no scoring of nurses\n1. no extra screens\n", encoding="utf-8")
    run("banlist.py", "--brief", "x", "--instincts", str(instincts_file), "--skeleton", skeleton,
        "--user", str(user), "--out", str(tmp_path))
    payload = load(tmp_path / "banlist.json")
    phrases = {e["phrase"] for e in payload["entries"]}
    assert {"no scoring of nurses", "no extra screens"} <= phrases
    assert payload["counts"]["user_exclusions"] == 2
    assert any(e["group"] == "user-exclusion" for e in payload["entries"])


def test_long_entries_become_manual_checks(run, tmp_path, instincts_file, skeleton):
    user = tmp_path / "user.txt"
    user.write_text("nothing that adds screen time at the bedside during a round\n", encoding="utf-8")
    run("banlist.py", "--brief", "x", "--instincts", str(instincts_file), "--skeleton", skeleton,
        "--user", str(user), "--out", str(tmp_path))
    payload = load(tmp_path / "banlist.json")
    assert payload["counts"]["manual"] >= 1
    assert payload["manual_checks"][-1]["source"] == "user"


def test_allow_releases_a_deck_entry(run, tmp_path, instincts_file, skeleton):
    run("banlist.py", "--brief", "x", "--instincts", str(instincts_file), "--skeleton", skeleton,
        "--allow", "gamification", "--out", str(tmp_path))
    payload = load(tmp_path / "banlist.json")
    assert "gamification" not in {e["id"] for e in payload["entries"]}
    assert payload["allowed"] == ["gamification"]


def test_unknown_allow_id_is_an_error(run, tmp_path, instincts_file, skeleton):
    res = run("banlist.py", "--brief", "x", "--instincts", str(instincts_file),
              "--skeleton", skeleton, "--allow", "not-a-thing")
    assert res.code == 1
    assert "unknown cliche id" in res.err


def test_stdin_input(run, tmp_path, skeleton):
    dump = "\n".join(f"obvious answer {i}" for i in range(10))
    res = run("banlist.py", "--brief", "x", "--instincts", "-", "--skeleton", skeleton,
              "--out", str(tmp_path), stdin=dump)
    assert res.code == 0, res
