"""The shipped example must be runnable exactly as documented.

Until these existed, the third input the gate requires - the ban contract - was
not in the repository at all, so the only way to see the example pass was to
reconstruct a fixture out of the test suite. approaches.json was worse: a
documented input with no producer, no example and no written shape.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "imagination-brainstorming" / "scripts"))

import divergence_check  # noqa: E402

# The brief and skeleton the shipped contract was built with. Documented in
# SKILL.md and README.md as one runnable block; changing either here means
# changing it there.
BRIEF = "a way for our ward to hand over shifts"
SKELETON = (
    "A capture tool that turns a spoken conversation into a structured record, "
    "with completeness enforced by a form and a signature at the end."
)


def test_the_shipped_contract_gates_the_shipped_spec(run, references):
    """The command SKILL.md step 6 gives the user, against shipped files only."""
    res = run(
        "spec_gate.py",
        "--concept", str(references / "example-concept.json"),
        "--markdown", str(references / "example-concept.md"),
        "--banlist", str(references / "example-banlist.json"),
    )
    assert res.code == 0, res
    assert "PASSED" in res.out


def test_the_shipped_approaches_pass_the_divergence_check(run, references):
    """The command SKILL.md step 3 gives the user, against shipped files only."""
    res = run(
        "divergence_check.py",
        "--approaches", str(references / "example-approaches.json"),
        "--banlist", str(references / "example-banlist.json"),
    )
    assert res.code == 0, res
    assert "PASSED" in res.out


def test_the_shipped_contract_is_what_banlist_py_produces(run, tmp_path, references):
    """A shipped artefact that cannot be regenerated is a fixture, not an example."""
    res = run(
        "banlist.py", "--brief", BRIEF,
        "--instincts", str(references / "example-instincts.txt"),
        "--user", str(references / "example-exclusions.txt"),
        "--skeleton", SKELETON, "--confirmed", "--out", str(tmp_path),
    )
    assert res.code == 0, res
    rebuilt = json.loads((tmp_path / "banlist.json").read_text(encoding="utf-8"))
    shipped = json.loads((references / "example-banlist.json").read_text(encoding="utf-8"))
    assert rebuilt == shipped, "example-banlist.json has drifted from the deck or the documented command"


def test_the_shipped_contract_is_the_one_the_sidecar_declares(references):
    concept = json.loads((references / "example-concept.json").read_text(encoding="utf-8"))
    contract = concept["banlist_contract"]
    shipped = json.loads((references / "example-banlist.json").read_text(encoding="utf-8"))
    assert shipped["skeleton"] == contract["skeleton"] == SKELETON
    assert shipped["model_instincts"] == contract["model_instincts"]
    assert shipped["user_exclusions"] == contract["user_exclusions"]
    assert shipped["user_confirmed"] is True


def test_the_shipped_approaches_are_the_ones_in_the_sidecar(references):
    concept = json.loads((references / "example-concept.json").read_text(encoding="utf-8"))
    approaches = json.loads((references / "example-approaches.json").read_text(encoding="utf-8"))
    assert approaches["approaches"] == concept["approaches"]


def test_the_approaches_schema_documents_every_field_the_check_reads(decks, references):
    schema = decks["approaches-schema"]
    documented = {f["name"] for f in schema["fields"]}
    assert {"id", "frame_id", "summary", "failure_mode", "unsafe_seat"} <= documented
    for field in schema["fields"]:
        assert len(field["note"]) > 40, f"{field['name']} is named but not explained"
        assert field["type"] in {"string", "boolean"}
    example = json.loads((references / "example-approaches.json").read_text(encoding="utf-8"))
    required = {f["name"] for f in schema["fields"] if f["required"]}
    for approach in example["approaches"]:
        assert required <= set(approach), "the shipped example omits a field the schema requires"


@pytest.mark.parametrize("constant,path", [
    ("DEFAULT_COUNT", ("counts", "approaches")),
    ("MIN_SUMMARY_UNITS", ("min_units", "summary")),
    ("MIN_FAILURE_UNITS", ("min_units", "failure_mode")),
    ("MIN_FRAME_FIT_UNITS", ("min_units", "frame_fit")),
    ("SUMMARY_MAX_OVERLAP", ("thresholds", "max_summary_overlap")),
    ("FAILURE_MAX_OVERLAP", ("thresholds", "max_failure_overlap")),
    ("DETAIL_RATIO", ("thresholds", "min_detail_ratio")),
    ("MIN_DISTINCT_RATIO", ("thresholds", "min_distinct_ratio")),
])
def test_the_deck_and_the_script_agree(decks, constant, path):
    """The schema is the documentation a stranger reads; a value that drifts from
    the code turns it into a description of a program that no longer exists."""
    section, key = path
    assert getattr(divergence_check, constant) == decks["approaches-schema"][section][key]


# --- the worked example that is not a product or a service -----------------
#
# The decks, the four original examples and the manual-check calibration were
# all built on one hospital-ward service, and it showed: the gate workload and
# half the deck vocabulary only make sense for a product. The ritual example
# below is shipped so that a stranger on a story, world, ritual or mechanic
# brief has something to copy the shape from. It is gated by the same commands.

RITUAL_BRIEF = "a ritual for closing a family bakery that has traded on one street for ninety years"
RITUAL_SKELETON = (
    "A gathering held on the final trading day at which the shop is thanked, photographed and "
    "remembered aloud, ending with an object handed over to be kept."
)


def test_the_ritual_example_passes_the_gate(run, references):
    res = run(
        "spec_gate.py",
        "--concept", str(references / "example-ritual-concept.json"),
        "--markdown", str(references / "example-ritual-concept.md"),
        "--banlist", str(references / "example-ritual-banlist.json"),
    )
    assert res.code == 0, res
    assert "PASSED" in res.out


def test_the_ritual_approaches_pass_the_divergence_check(run, references):
    res = run(
        "divergence_check.py",
        "--approaches", str(references / "example-ritual-approaches.json"),
        "--banlist", str(references / "example-ritual-banlist.json"),
    )
    assert res.code == 0, res


def test_the_ritual_contract_is_what_banlist_py_produces(run, tmp_path, references):
    res = run(
        "banlist.py", "--brief", RITUAL_BRIEF,
        "--instincts", str(references / "example-ritual-instincts.txt"),
        "--user", str(references / "example-ritual-exclusions.txt"),
        "--skeleton", RITUAL_SKELETON, "--confirmed", "--out", str(tmp_path),
    )
    assert res.code == 0, res
    rebuilt = json.loads((tmp_path / "banlist.json").read_text(encoding="utf-8"))
    shipped = json.loads((references / "example-ritual-banlist.json").read_text(encoding="utf-8"))
    assert rebuilt == shipped


def test_the_ritual_example_is_not_about_a_product(references):
    """The point of shipping it. If this file ever acquires users, a roadmap and
    a dashboard, the skill has quietly become a product tool again."""
    text = (references / "example-ritual-concept.md").read_text(encoding="utf-8").lower()
    for word in ("user", "customer journey", "roadmap", "launch", "kpi", "onboarding"):
        assert word not in text.split("<!-- section: banlist -->")[0], word


def test_the_ritual_example_shows_the_gate_naming_its_own_limits(run, references):
    res = run(
        "spec_gate.py",
        "--concept", str(references / "example-ritual-concept.json"),
        "--markdown", str(references / "example-ritual-concept.md"),
        "--banlist", str(references / "example-ritual-banlist.json"), "--json",
    )
    warnings = " | ".join(res.json()["warnings"])
    assert "long instincts" in warnings, "a narrative brief produces model-instinct manual checks"
    assert "the chosen approach fails like this" in warnings
