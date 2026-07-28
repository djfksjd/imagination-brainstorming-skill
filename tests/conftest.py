"""Shared fixtures. Offline by construction: the scripts make no network calls
and read nothing outside the repository, so the suite runs anywhere."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# The brief the shipped example was built with. The gate requires the ban list
# and the sidecar to record the same brief string, so a fixture contract has to
# carry the real one.
BRIEF = "a way for our ward to hand over shifts"

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "imagination-brainstorming"
SCRIPTS = SKILL / "scripts"
REFERENCES = SKILL / "references"
DECKS = REFERENCES / "decks"


class Result:
    def __init__(self, proc: subprocess.CompletedProcess[str]):
        self.code = proc.returncode
        self.out = proc.stdout
        self.err = proc.stderr

    def json(self):
        return json.loads(self.out)

    def __repr__(self) -> str:  # pragma: no cover - only used on failure
        return f"Result(code={self.code}, out={self.out[:400]!r}, err={self.err[:400]!r})"


@pytest.fixture(scope="session")
def repo() -> Path:
    return REPO


@pytest.fixture(scope="session")
def references() -> Path:
    return REFERENCES


@pytest.fixture(scope="session")
def decks() -> dict:
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in DECKS.glob("*.json")}


@pytest.fixture(scope="session")
def example(references: Path) -> dict:
    return json.loads((references / "example-concept.json").read_text(encoding="utf-8"))


@pytest.fixture
def run():
    def _run(script: str, *args: str, stdin: str | None = None, timeout: float | None = None) -> Result:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return Result(proc)

    return _run


@pytest.fixture(scope="session")
def schema():
    sys.path.insert(0, str(SCRIPTS))
    from engine import load_deck  # noqa: E402
    return load_deck("spec-schema")


@pytest.fixture
def check(banlist, schema):
    """Run check_concept directly and return its failures as one string. Shared
    because the length floors are now exercised from two files."""
    sys.path.insert(0, str(SCRIPTS))
    import spec_gate  # noqa: E402
    from engine import load_banlist, load_deck  # noqa: E402

    frames, cliches = load_deck("frames"), load_deck("cliches")
    contract = load_banlist(str(banlist))

    def _check(concept: dict) -> str:
        return " | ".join(spec_gate.check_concept(concept, schema, frames, contract, cliches)["failures"])

    return _check


@pytest.fixture
def instincts_file(tmp_path: Path, example: dict) -> Path:
    path = tmp_path / "instincts.txt"
    path.write_text("\n".join(example["banlist_contract"]["model_instincts"]) + "\n", encoding="utf-8")
    return path


@pytest.fixture
def skeleton(example: dict) -> str:
    return example["banlist_contract"]["skeleton"]


@pytest.fixture
def user_file(tmp_path: Path, example: dict) -> Path:
    path = tmp_path / "user.txt"
    path.write_text("\n".join(example["banlist_contract"]["user_exclusions"]) + "\n", encoding="utf-8")
    return path


@pytest.fixture
def banlist(tmp_path: Path, run, instincts_file: Path, user_file: Path, skeleton: str) -> Path:
    """The contract the shipped example was built against: same instincts, same
    user exclusions, signed."""
    res = run(
        "banlist.py", "--brief", BRIEF, "--instincts", str(instincts_file),
        "--user", str(user_file), "--skeleton", skeleton, "--confirmed", "--out", str(tmp_path),
    )
    assert res.code == 0, res
    return tmp_path / "banlist.json"


@pytest.fixture
def spec_md(references: Path) -> str:
    return str(references / "example-concept.md")


@pytest.fixture
def gate(run, spec_md: str, banlist: Path):
    """spec_gate.py needs all three inputs; tests vary the concept."""
    def _gate(concept: str, *extra: str):
        return run("spec_gate.py", "--concept", concept, "--markdown", spec_md,
                   "--banlist", str(banlist), *extra)

    return _gate


@pytest.fixture
def concept_path(tmp_path: Path, example: dict):
    def _write(payload: dict | None = None) -> str:
        path = tmp_path / "concept.json"
        path.write_text(json.dumps(payload if payload is not None else example, ensure_ascii=False), encoding="utf-8")
        return str(path)

    return _write
