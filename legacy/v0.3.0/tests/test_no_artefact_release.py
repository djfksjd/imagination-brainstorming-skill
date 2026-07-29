"""Nothing the judged artefact says releases a burnt instinct or a user exclusion.

Five mechanisms have now produced the same defect. `allowed` released whatever
it named. Mention markers released whatever they named. A supplied regex hung
the gate so no verdict arrived. An `id` collided with a bundled deck id and the
supplied entry was dropped from the lint. Membership of `model_instincts`
turned one of the user's own exclusions into a warning. Two of those arrived
*inside* the commit that closed the previous one.

The version of this file that preceded this one was written specifically to
catch an unknown sixth route, and could not catch either of the two that came
next. It pinned `lint_text`'s parameter list and enumerated ban-list *fields*;
both new routes were new *values in existing fields*, acting *before*
`lint_text` was reached. A test that enumerates the shapes an attack has taken
so far catches the attacks that have already happened.

So this file asserts the property where it matters instead: hand the real entry
point a hand-edited artefact whose spec uses a burnt instinct and one of the
user's own exclusions, over a generated space of mutations of the contract -
ids rewritten and collided, tiers changed, statements moved between fields and
between the two files, entries duplicated, deleted and reordered, phrases
relocated in the markdown - and require the gate to refuse. Every case runs
`spec_gate.main` end to end. Mutations are also composed in pairs, so a route
that needs two edits at once is in the space too.

One mutation is whitelisted, with its reason, at the bottom: it is the limit the
code states in `engine.protected_statements`, and it is pinned here so that
closing it later is a visible change rather than a silent one.
"""

from __future__ import annotations

import contextlib
import inspect
import io
import itertools
import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "skills" / "imagination-brainstorming" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import spec_gate  # noqa: E402
from engine import (  # noqa: E402
    deck_lint_entries, lint_text, load_deck, protected_statements, releasable_ids,
)

INSTINCT = "handover app with structured form"
EXCLUSION = "no scoring or ranking of nurses"
PROTECTED = (INSTINCT, EXCLUSION)


# --- the entry point, in process -------------------------------------------


def gate(concept: dict, banlist: dict, markdown: str, tmp_path: Path, tag: str) -> tuple[int, str]:
    """Run `spec_gate.main` exactly as the command line does, and return its
    exit code. In process rather than through `subprocess` only because the
    space below runs it several hundred times; the argv, the parsing, the decks
    and every check are the real ones."""
    cpath = tmp_path / f"{tag}-concept.json"
    bpath = tmp_path / f"{tag}-banlist.json"
    mpath = tmp_path / f"{tag}-spec.md"
    cpath.write_text(json.dumps(concept, ensure_ascii=False), encoding="utf-8")
    bpath.write_text(json.dumps(banlist, ensure_ascii=False), encoding="utf-8")
    mpath.write_text(markdown, encoding="utf-8")
    out, err = io.StringIO(), io.StringIO()
    argv = ["--concept", str(cpath), "--markdown", str(mpath), "--banlist", str(bpath)]
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = spec_gate.main(argv)
    except SystemExit as exc:  # die() on a malformed artefact
        code = int(exc.code or 0)
    return code, out.getvalue() + err.getvalue()


@pytest.fixture(scope="module")
def artefacts(request) -> tuple[dict, dict, str]:
    """The shipped spec, its sidecar and its contract - with one sentence added
    to the spec that uses both protected phrases. Unmutated, this must fail."""
    references = SCRIPTS.parent / "references"
    concept = json.loads((references / "example-concept.json").read_text(encoding="utf-8"))
    banlist = json.loads((references / "example-banlist.json").read_text(encoding="utf-8"))
    markdown = (references / "example-concept.md").read_text(encoding="utf-8").rstrip()
    markdown += f"\n\n<!-- section: notes -->\n\nThe result is a {INSTINCT} with {EXCLUSION}.\n"
    return concept, banlist, markdown


# --- the mutation space -----------------------------------------------------


def _protected_entries(banlist: dict) -> list[dict]:
    return [e for e in banlist["entries"] if e.get("phrase") in PROTECTED]


def _deck_ids() -> list[str]:
    deck = load_deck("cliches")
    return [e["id"] for e in deck_lint_entries(deck)]


def m_id_collide_with_deck(concept: dict, banlist: dict) -> None:
    """The round-4 Critical: borrow a bundled deck id so the supplied entry is
    dropped by `lint_entries` while `replay_contract` still sees the phrase."""
    for entry, deck_id in zip(_protected_entries(banlist), _deck_ids()):
        entry["id"] = deck_id


def m_id_collide_with_each_other(concept: dict, banlist: dict) -> None:
    for entry in _protected_entries(banlist):
        entry["id"] = "instinct-01"


def m_id_rename(concept: dict, banlist: dict) -> None:
    for i, entry in enumerate(_protected_entries(banlist)):
        entry["id"] = f"zz-{i:02d}"


def m_id_strip_prefix(concept: dict, banlist: dict) -> None:
    """Remove the `instinct-`/`user-` prefix, which is the only id-shaped thing
    the protected set reads."""
    for i, entry in enumerate(_protected_entries(banlist)):
        entry["id"] = f"{i:02d}"
    for check in banlist.get("manual_checks", []):
        check["id"] = check["id"].split("-")[-1]


def m_id_relabel_user_as_instinct(concept: dict, banlist: dict) -> None:
    for entry in banlist["entries"]:
        if str(entry.get("id")).startswith("user-"):
            entry["id"] = "instinct-" + str(entry["id"]).split("-")[-1]
    for check in banlist.get("manual_checks", []):
        if str(check.get("id")).startswith("user-"):
            check["id"] = "instinct-" + str(check["id"]).split("-")[-1]


def m_tier_warn(concept: dict, banlist: dict) -> None:
    for entry in _protected_entries(banlist):
        entry["tier"] = "warn"


def m_tier_manual(concept: dict, banlist: dict) -> None:
    for entry in _protected_entries(banlist):
        entry["tier"] = "manual"


def m_entries_dropped(concept: dict, banlist: dict) -> None:
    banlist["entries"] = [e for e in banlist["entries"] if e.get("phrase") not in PROTECTED]


def m_entries_duplicated(concept: dict, banlist: dict) -> None:
    banlist["entries"] = banlist["entries"] + [deepcopy(e) for e in _protected_entries(banlist)]


def m_entries_reordered(concept: dict, banlist: dict) -> None:
    banlist["entries"] = list(reversed(banlist["entries"]))


def m_phrase_replaced(concept: dict, banlist: dict) -> None:
    """Keep the id and the tier, change the phrase - the entry looks intact."""
    for entry in _protected_entries(banlist):
        entry["phrase"] = "a phrase nobody burned"


def m_entry_moved_to_manual_checks(concept: dict, banlist: dict) -> None:
    moved = _protected_entries(banlist)
    banlist["entries"] = [e for e in banlist["entries"] if e.get("phrase") not in PROTECTED]
    banlist["manual_checks"] = banlist.get("manual_checks", []) + [
        {"id": e["id"], "statement": e["phrase"], "source": e.get("source", "model"), "note": "moved"}
        for e in moved
    ]


def m_banlist_lists_emptied(concept: dict, banlist: dict) -> None:
    banlist["model_instincts"] = []
    banlist["user_exclusions"] = []


def m_sidecar_lists_swapped(concept: dict, banlist: dict) -> None:
    contract = concept["banlist_contract"]
    contract["model_instincts"], contract["user_exclusions"] = (
        list(contract.get("user_exclusions") or []), list(contract.get("model_instincts") or []))


def m_user_declared_a_model_instinct(concept: dict, banlist: dict) -> None:
    """The round-4 Important: copy the user's own exclusions into the model's
    list, in both files, so the answer they require is discharged unanswered."""
    users = list(concept["banlist_contract"].get("user_exclusions") or [])
    concept["banlist_contract"]["model_instincts"] = (
        list(concept["banlist_contract"]["model_instincts"]) + users)
    banlist["model_instincts"] = list(banlist["model_instincts"]) + users
    concept["banlist_contract"]["manual_checks_cleared"] = []


def m_manual_checks_emptied(concept: dict, banlist: dict) -> None:
    banlist["manual_checks"] = []
    concept["banlist_contract"]["manual_checks_cleared"] = []


def m_allowed_everything(concept: dict, banlist: dict) -> None:
    banlist["allowed"] = [str(e["id"]) for e in banlist["entries"]] + [
        str(p["id"]) for p in banlist.get("structural_patterns", [])] + _deck_ids()


def m_structural_patterns_emptied(concept: dict, banlist: dict) -> None:
    banlist["structural_patterns"] = []


def m_structural_pattern_neutered(concept: dict, banlist: dict) -> None:
    """A supplied pattern borrowing a bundled id, with a regex that matches
    nothing - the same collision, on the pattern channel."""
    deck = load_deck("cliches")
    banlist["structural_patterns"] = [
        {"id": p["id"], "regex": "$^", "tier": "ban", "why": ""} for p in deck["structural_patterns"]
    ]


def m_unread_fields_named_release(concept: dict, banlist: dict) -> None:
    banlist["release"] = _deck_ids()
    banlist["exempt"] = [str(e["id"]) for e in banlist["entries"]]
    banlist["skip_lint"] = True
    banlist["protected"] = []
    concept["banlist_contract"]["release"] = [str(e["id"]) for e in banlist["entries"]]


def m_statements_relocated_into_unlinted_fields(concept: dict, banlist: dict) -> None:
    """Move the protected statements out of the lists and into fields the gate
    reads for other purposes."""
    banlist["notes"] = list(PROTECTED)
    concept["banlist_contract_notes"] = list(PROTECTED)


MUTATIONS = {
    "id-collide-with-deck": m_id_collide_with_deck,
    "id-collide-with-each-other": m_id_collide_with_each_other,
    "id-rename": m_id_rename,
    "id-strip-prefix": m_id_strip_prefix,
    "id-relabel-user-as-instinct": m_id_relabel_user_as_instinct,
    "tier-warn": m_tier_warn,
    "tier-manual": m_tier_manual,
    "entries-dropped": m_entries_dropped,
    "entries-duplicated": m_entries_duplicated,
    "entries-reordered": m_entries_reordered,
    "phrase-replaced": m_phrase_replaced,
    "entry-moved-to-manual-checks": m_entry_moved_to_manual_checks,
    "banlist-lists-emptied": m_banlist_lists_emptied,
    "sidecar-lists-swapped": m_sidecar_lists_swapped,
    "user-declared-a-model-instinct": m_user_declared_a_model_instinct,
    "manual-checks-emptied": m_manual_checks_emptied,
    "allowed-everything": m_allowed_everything,
    "structural-patterns-emptied": m_structural_patterns_emptied,
    "structural-pattern-neutered": m_structural_pattern_neutered,
    "unread-fields-named-release": m_unread_fields_named_release,
    "statements-relocated": m_statements_relocated_into_unlinted_fields,
}


def apply_all(names, artefacts):
    concept, banlist, markdown = deepcopy(artefacts[0]), deepcopy(artefacts[1]), artefacts[2]
    for name in names:
        MUTATIONS[name](concept, banlist)
    return concept, banlist, markdown


def test_the_unmutated_artefact_fails(artefacts, tmp_path):
    """The control. If this ever passes, every case below is vacuous."""
    code, out = gate(*apply_all([], artefacts), tmp_path, "control")
    assert code == 2, out
    assert INSTINCT in out and EXCLUSION in out, out


PROTECTED_REFUSAL = "burnt instinct(s) or user exclusion(s) are used in the spec"


def assert_refused(code: int, out: str, label: str) -> None:
    """Refused, and refused *for this reason*.

    Asserting only a non-zero exit would let a case pass on some unrelated
    schema failure while the release route it was written for stayed open, which
    is how a suite of 317 tests came to be green over two live release routes.
    Either the recomputed protected set fired, or the artefact was rejected as
    malformed before any linting happened.
    """
    assert code != 0, f"{label} was accepted:\n{out}"
    assert code == 1 or PROTECTED_REFUSAL in out, (
        f"{label} was refused, but not by the protected set - the route may still be open:\n{out}")


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_no_single_contract_mutation_lets_the_protected_phrases_pass(name, artefacts, tmp_path):
    code, out = gate(*apply_all([name], artefacts), tmp_path, name)
    assert_refused(code, out, name)


@pytest.mark.parametrize("pair", sorted(itertools.combinations(sorted(MUTATIONS), 2)))
def test_no_pair_of_contract_mutations_lets_them_pass(pair, artefacts, tmp_path):
    """Composed, because a route that needs one edit has always been followed by
    a route that needs two."""
    code, out = gate(*apply_all(pair, artefacts), tmp_path, "-".join(pair)[:60])
    assert_refused(code, out, " + ".join(pair))


# --- the same property, mutating where the phrases sit in the document ------


def _spec(references: Path, tail: str) -> str:
    text = (references / "example-concept.md").read_text(encoding="utf-8").rstrip()
    return f"{text}\n\n<!-- section: notes -->\n\n{tail}\n"


MARKDOWN_SHAPES = {
    "plain": f"The result is a {INSTINCT} with {EXCLUSION}.",
    "in-a-fenced-block": f"```\n{INSTINCT}\n{EXCLUSION}\n```",
    "in-a-mention-span": (
        f"<!-- mention: instinct-01 -->not a {INSTINCT}<!-- /mention -->\n\n"
        f"<!-- mention: hollow-magical -->not magical<!-- /mention --> {INSTINCT} {EXCLUSION}"
    ),
    "released-copy-repeated": (
        f"<!-- mention: hollow-magical -->\n```\n{INSTINCT}\n```\n<!-- /mention -->\n\n"
        + "\n\n".join([INSTINCT] * 4)
    ),
    "past-the-pattern-window": " ".join("w%04d" % i for i in range(900)) + f" {INSTINCT} {EXCLUSION}",
    "repeated-many-times": "\n\n".join([f"{INSTINCT} {EXCLUSION}"] * 12),
    "whole-document-marker": None,   # filled in below: one marker naming every id
    "split-by-a-marker": f"a hand{'<!-- mention: hollow-magical -->not magical<!-- /mention -->'}over app "
                         f"with structured form and {EXCLUSION}",
}


def _whole_document_marker() -> str:
    """Round 3's Critical, kept in the space: one marker naming every id in the
    contract and wrapping everything after it."""
    references = SCRIPTS.parent / "references"
    banlist = json.loads((references / "example-banlist.json").read_text(encoding="utf-8"))
    ids = ", ".join([str(e["id"]) for e in banlist["entries"]]
                    + [str(p["id"]) for p in banlist.get("structural_patterns", [])])
    return f"<!-- mention: {ids} -->not a {INSTINCT}, and {EXCLUSION}<!-- /mention -->"


MARKDOWN_SHAPES["whole-document-marker"] = _whole_document_marker()


@pytest.mark.parametrize("shape", sorted(MARKDOWN_SHAPES))
@pytest.mark.parametrize("mutation", ["", "id-collide-with-deck", "allowed-everything"])
def test_no_place_in_the_document_escapes_the_protected_set(shape, mutation, artefacts, tmp_path):
    references = SCRIPTS.parent / "references"
    concept, banlist, _ = apply_all([mutation] if mutation else [], artefacts)
    code, out = gate(concept, banlist, _spec(references, MARKDOWN_SHAPES[shape]),
                     tmp_path, f"{shape}-{mutation or 'none'}")
    assert_refused(code, out, f"{shape} + {mutation or 'unmutated'}")


# --- the whitelisted mutation, and the limit it pins ------------------------


def test_deleting_a_statement_from_every_location_in_both_files_is_not_caught(artefacts, tmp_path):
    """WHITELISTED, with its reason: this one is allowed to pass.

    The gate has no copy of the session's instincts or the user's exclusions
    that the judged party did not write. There is no dump, no signature and no
    record from outside the session at the moment the gate runs, so a statement
    removed from `entries`, from `manual_checks`, from `model_instincts` and
    from `user_exclusions` in *both* files is simply not in the artefact any
    more, and nothing here can know it was ever there. What the protected set
    closes is every route that *keeps* the statement somewhere while stopping it
    firing; what it does not close is deletion, and the note above
    `engine.protected_statements` says exactly that.

    Pinned as a passing case rather than left out of the generator, so that a
    later wave which does close it - by carrying the instinct dump into the gate,
    for instance - fails here and has to come and delete this test and the
    paragraph in SKILL.md that admits the gap.
    """
    concept, banlist, markdown = apply_all([], artefacts)
    banlist["entries"] = [e for e in banlist["entries"] if e.get("phrase") not in PROTECTED]
    for holder in (banlist, concept["banlist_contract"]):
        for key in ("model_instincts", "user_exclusions"):
            holder[key] = [v for v in holder.get(key, []) if v not in PROTECTED]
    code, out = gate(concept, banlist, markdown, tmp_path, "deleted-everywhere")
    assert code == 0, (
        "deletion from every location in both files is the documented limit and used to pass; if it now "
        "fails, the limit has been closed - delete this test and the disclosure that goes with it:\n" + out
    )
    assert not protected_statements(concept, banlist).get("handover app with structured form")


# --- what is still pinned about the release surface -------------------------


def test_the_release_surface_is_narrowed_to_the_bundled_deck():
    """`allow` is the only release parameter `lint_text` has, and it is
    intersected with the bundled deck inside the function.

    This pin is worth keeping and worth stating accurately, which the version it
    replaces did not: it catches a new release *parameter*, and it catches
    nothing that acts before `lint_text` is reached. Both routes found in round 4
    acted before it. The tests above, not this one, are what covers those.
    """
    params = list(inspect.signature(lint_text).parameters)
    assert params == ["text", "entries", "patterns", "allow", "line_offset"], (
        "a new parameter of lint_text may be a new release route; drive it from the mutation space "
        "above before shipping it, then update this list"
    )
    assert not inspect.signature(releasable_ids).parameters, (
        "releasable_ids() takes no argument on purpose - a caller that can widen the releasable set "
        "is the hole this file exists to prevent"
    )


def test_the_releasable_set_is_the_bundled_deck_and_nothing_else():
    deck = load_deck("cliches")
    expected = {e["id"] for e in deck_lint_entries(deck)} | {str(p["id"]) for p in deck["structural_patterns"]}
    assert releasable_ids() == expected
    assert not any(i.startswith(("instinct-", "user-", "extra-", "protected-")) for i in releasable_ids())


def test_the_protected_set_is_a_union_that_editing_can_only_grow():
    """The property the whole mechanism rests on: every source is additive, so
    moving a statement between fields or files cannot subtract it."""
    concept = {"banlist_contract": {"model_instincts": ["alpha beta"], "user_exclusions": ["gamma delta"]}}
    banlist = {"entries": [{"id": "instinct-07", "phrase": "epsilon zeta", "tier": "warn"}],
               "manual_checks": [{"id": "user-04", "statement": "eta theta iota kappa lambda mu nu"}]}
    full = protected_statements(concept, banlist)
    assert set(full) == {"alpha beta", "gamma delta", "epsilon zeta", "eta theta iota kappa lambda mu nu"}
    assert full["gamma delta"][1] == "user"
    assert full["epsilon zeta"][1] == "model"

    # declared as both: the user's reading wins, so a copy into model_instincts
    # adds a claim rather than discharging an obligation
    concept["banlist_contract"]["model_instincts"].append("gamma delta")
    assert protected_statements(concept, banlist)["gamma delta"][1] == "user"

    # every id rewritten: the lists still hold both statements
    banlist["entries"][0]["id"] = "hollow-magical"
    banlist["manual_checks"][0]["id"] = "hollow-seamless"
    assert set(protected_statements(concept, banlist)) >= {"alpha beta", "gamma delta"}
