#!/usr/bin/env python3
"""spec_gate.py - fail-closed gate between a concept spec and the user's review.

Validates three things together, and refuses to run on fewer: the written spec,
its machine-readable sidecar `concept.json`, and the session's ban contract.
Checking the sidecar alone would let a session pass the gate without ever
writing the document the gate claims to be about.

What it proves: premises were tested, the ban contract exists and the user
signed it, three approaches diverge with one honestly occupying the unsafe
seat, the chosen concept forbids something and does not restate the banned
skeleton, the neighbours are named, the unknowns are written down, and the
user's own exclusions were each answered.

What it does not prove: that the concept is any good. Nothing mechanical can.

Usage:
  spec_gate.py --concept ./work/concept.json \
               --markdown docs/concepts/2026-07-28-handover-concept.md \
               --banlist ./work/banlist.json

Exit codes: 0 pass, 1 usage or parse error, 2 gate failed.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

try:
    from engine import (  # type: ignore
        VERSION, UsageParser, EngineError, content_tokens, coverage, csv_list, deck_lint_entries, die,
        distinct_ratio, extract_mentions, jaccard, load_banlist, load_deck, lint_text, normalize,
        read_json_arg, require_mapping, strip_mention_markers, text_units,
    )
    from divergence_check import check as divergence_check  # type: ignore
    from banlist import classify as classify_exclusions  # type: ignore
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from engine import (  # type: ignore
        VERSION, UsageParser, EngineError, content_tokens, coverage, csv_list, deck_lint_entries, die,
        distinct_ratio, extract_mentions, jaccard, load_banlist, load_deck, lint_text, normalize,
        read_json_arg, require_mapping, strip_mention_markers, text_units,
    )
    from divergence_check import check as divergence_check  # type: ignore
    from banlist import classify as classify_exclusions  # type: ignore

GATE_FAIL = 2
MIN_QUESTION_TOKENS = 6
# "This design does not restrict anything" satisfies the character count while
# saying the opposite of what the field is for.
SELF_NEGATING_FORBID = re.compile(
    r"\b(?:no|not|nothing|none|never)\b[^.]{0,40}\b(?:forbid|restrict|prevent|limit|rule out|constrain|refus)",
    re.IGNORECASE,
)
SECTION_MARKER = re.compile(r"<!--\s*section:\s*([\w-]+)\s*-->", re.IGNORECASE)


def build_parser() -> argparse.ArgumentParser:
    p = UsageParser(description="Gate a concept spec before the user is asked to review it.")
    p.add_argument("--concept", required=True, help="concept.json, or '-'")
    p.add_argument("--markdown", required=True, help="the written spec; required - the gate is about this file")
    p.add_argument("--banlist", required=True, help="banlist.json from banlist.py")
    # No --allow here. An exception granted at verdict time is granted by the
    # same party the verdict is about, which is the identical bypass as a
    # threshold override. A legitimate exception is made once, while the ban
    # contract is being built (banlist.py --allow), recorded there with an id
    # and a reason, shown to the user before they confirm it, and inherited by
    # every later gate.
    p.add_argument("--json", action="store_true", help="emit the verdict as JSON")
    return p


def text_of(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def split_sections(markdown: str) -> list[tuple[str, str]]:
    """Return [(section id, body)] in the order the markers appear."""
    matches = list(SECTION_MARKER.finditer(markdown))
    out: list[tuple[str, str]] = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
        out.append((m.group(1).lower(), markdown[m.end():end].strip()))
    return out


def lintable_markdown(markdown: str) -> str:
    """The whole document minus the ban-contract span.

    Two earlier versions leaked: one blanked everything after the contract
    marker, the other rebuilt the text from parsed section bodies and so
    dropped the preamble - a banned phrase in the title or the opening
    paragraph went unseen. This cuts out exactly the contract span and keeps
    every other character.
    """
    matches = list(SECTION_MARKER.finditer(markdown))
    spans: list[tuple[int, int]] = []
    for i, m in enumerate(matches):
        if m.group(1).lower() == "banlist":
            end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
            spans.append((m.start(), end))
    if not spans:
        return markdown
    out, cursor = [], 0
    for start, end in spans:
        out.append(markdown[cursor:start])
        cursor = end
    out.append(markdown[cursor:])
    return "".join(out)


COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
FENCE = re.compile(r"```.*?```", re.DOTALL)


def visible_text(markdown: str) -> str:
    """What a reader actually sees: HTML comments and fenced blocks removed.

    Section bodies used to be measured in raw characters, so ten markers each
    followed by a long HTML comment produced a document that rendered as a
    title and nothing else - and passed."""
    return FENCE.sub(" ", COMMENT.sub(" ", markdown))


def walk_strings(node: Any, path: str = "") -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if isinstance(node, str):
        out.append((path or "root", node))
    elif isinstance(node, dict):
        for k, v in node.items():
            out.extend(walk_strings(v, f"{path}.{k}" if path else str(k)))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out.extend(walk_strings(v, f"{path}[{i}]"))
    return out


def check_padding(label: str, value: str, threshold: float, failures: list[str]) -> None:
    """A field padded to its minimum with a repeated word or one letter repeated
    meets the character count and says nothing."""
    if value and distinct_ratio(value) < threshold:
        failures.append(f"{label}: repeated filler rather than content ({distinct_ratio(value):.2f} distinct)")


def replay_contract(contract: dict[str, Any], banlist: dict[str, Any],
                    cliches: dict[str, Any], warnings: list[str] | None = None) -> list[str]:
    """Rebuild the ban contract from what the sidecar declares and require the
    supplied file to contain it.

    A gate that reads whatever file is handed to it under `--banlist` is not
    gating stage 2 at all: a one-entry list written by the caller turned a
    76-phrase lint into a one-phrase lint and, because the user's long
    exclusions live in `manual_checks`, silently discharged every check the
    user personally asked for. So the contract is replayed the way the draw is
    replayed next door: the instincts and exclusions the sidecar claims are
    reclassified here, with the same rules `banlist.py` used, and every
    resulting ban and manual check must be present in the file. The bundled
    cliche deck must be present too, minus only the ids the contract itself
    released while it was being built.

    Containment rather than equality, deliberately: a later contract may add
    bans (`--extra`, a second round of exclusions) and adding bans cannot
    weaken a verdict. Removing them can, and that is what this refuses.
    """
    failures: list[str] = []

    instincts = [v for v in (contract.get("model_instincts") or []) if isinstance(v, str) and v.strip()]
    exclusions = [v for v in (contract.get("user_exclusions") or []) if isinstance(v, str) and v.strip()]

    supplied_entries = [e for e in banlist.get("entries", []) if isinstance(e, dict)]
    supplied_phrases = {normalize(e.get("phrase", "")) for e in supplied_entries}
    supplied_ids = {e.get("id") for e in supplied_entries}
    supplied_manual = {
        normalize(m.get("statement", "")) for m in banlist.get("manual_checks", []) if isinstance(m, dict)
    }

    expected_entries: list[dict[str, Any]] = []
    expected_manual: list[dict[str, str]] = []
    classify_exclusions(instincts, "instinct", "first-instinct", "model", expected_entries, expected_manual)
    classify_exclusions(exclusions, "user", "user-exclusion", "user", expected_entries, expected_manual)

    missing_bans = [e["phrase"] for e in expected_entries if normalize(e["phrase"]) not in supplied_phrases]
    if missing_bans:
        failures.append(
            f"the ban list is missing {len(missing_bans)} phrase(s) the sidecar says were burned "
            f"({', '.join(missing_bans[:3])}...) - this is not the contract this session built, and a "
            "substituted contract lints against a shorter list than the user signed"
        )
    missing_manual = [m["statement"] for m in expected_manual if normalize(m["statement"]) not in supplied_manual]
    if missing_manual:
        failures.append(
            f"the ban list is missing {len(missing_manual)} of the user's long exclusions "
            f"({missing_manual[0][:60]}...) - dropping them from the file is how every manual check "
            "gets discharged without being answered"
        )

    # `allowed` is read here for one purpose only: to say why a bundled entry is
    # absent from the file. It grants nothing at lint time - see lint_entries.
    # An instinct or a user exclusion is not releasable at all: those are checked
    # above by phrase, and a release naming one is refused below as unknown.
    deck = deck_lint_entries(cliches)
    known_ids = {e["id"] for e in deck}
    allowed = banlist.get("allowed", [])
    if not isinstance(allowed, list) or any(not isinstance(i, str) for i in allowed):
        failures.append("the ban list's 'allowed' field must be a list of cliche ids")
        allowed = []
    unknown = sorted(set(allowed) - known_ids)
    if unknown:
        failures.append(
            f"the ban list releases id(s) that are not in the cliche deck: {', '.join(unknown)}"
        )
    missing_deck = [e["id"] for e in deck if e["id"] not in supplied_ids and e["id"] not in set(allowed)]
    if missing_deck:
        failures.append(
            f"the ban list is missing {len(missing_deck)} entries of the bundled cliche deck "
            f"({', '.join(missing_deck[:3])}...) - rebuild it with banlist.py rather than by hand"
        )
    if allowed and warnings is not None:
        warnings.append(
            f"the ban list releases {len(allowed)} cliche id(s) ({', '.join(sorted(allowed)[:3])}); this gate "
            "does not honour releases - a file cannot exempt itself from the verdict it is being judged by, "
            "so those phrases are still linted here"
        )
    return failures


def lint_entries(banlist: dict[str, Any], cliches: dict[str, Any]) -> list[dict[str, Any]]:
    """What the spec is linted against: the bundled deck, plus the contract.

    The deck goes in first and wins. Two rules follow, and each closes a hole
    that was open in a version of this file.

    A supplied entry carrying a bundled id is dropped, not merged. Dedup used to
    be by id alone with the caller's copy processed first, so a contract could
    carry `{"id": "hollow-seamless", "tier": "warn"}` and the deck's ban-tier
    entry was never added - the deck was displaceable by the file under
    judgement. A supplied entry that adds a *new* phrase is still added; adding
    bans cannot weaken a verdict.

    `allowed` is not read here at all. It is an assertion made by the artefact
    being judged, and honouring it made naming a cliche id in the ban list
    enough to release that cliche from the lint - the same bypass as a `--allow`
    flag at verdict time, only cheaper. A release recorded by `banlist.py
    --allow` still shortens the drafting lint (`cliche_lint.py`) and is still
    accepted by the replay as a reason for the entry to be absent from the file;
    it buys nothing at this gate. Releasing a bundled cliche at the gate means
    changing the deck in the repository, where the change is reviewed outside
    the session that wants it.
    """
    deck = deck_lint_entries(cliches)
    reserved = {e["id"] for e in deck}
    out: list[dict[str, Any]] = list(deck)
    seen = {f"{e['id']}\x1f{normalize(str(e['phrase']))}" for e in deck}
    for entry in banlist.get("entries", []):
        if not isinstance(entry, dict) or entry.get("id") in reserved:
            continue
        key = f"{entry.get('id')}\x1f{normalize(str(entry.get('phrase', '')))}"
        if key in seen:
            continue
        seen.add(key)
        out.append(entry)
    return out


def lint_patterns(banlist: dict[str, Any], cliches: dict[str, Any]) -> list[dict[str, Any]]:
    """The structural patterns, deck first and likewise not displaceable.

    A supplied pattern bearing a bundled id used to replace it, so setting
    `x-for-y` to the regex `$^` deleted a shipped structural ban.
    """
    deck = list(cliches["structural_patterns"])
    seen = {str(p.get("id")) for p in deck}
    out: list[dict[str, Any]] = list(deck)
    for pattern in banlist.get("structural_patterns", []):
        if not isinstance(pattern, dict) or str(pattern.get("id")) in seen:
            continue
        seen.add(str(pattern.get("id")))
        out.append(pattern)
    return out


def check_concept(concept: dict[str, Any], schema: dict[str, Any], frames: dict[str, Any],
                  banlist: dict[str, Any], cliches: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    counts = schema["counts"]
    mins = schema["min_units"]
    thresholds = schema["thresholds"]

    brief = text_of(concept.get("brief"))
    if text_units(brief) < mins["brief"]:
        failures.append(f"brief: needs at least {mins['brief']} units - state what was asked and what you learned it actually is")
    check_padding("brief", brief, thresholds["min_distinct_ratio"], failures)

    # --- premises -----------------------------------------------------------
    premises = concept.get("premises")
    if not isinstance(premises, list) or len(premises) < counts["min_premises"]:
        failures.append(f"premises: at least {counts['min_premises']} entries required")
    else:
        broken = 0
        seen: dict[str, int] = {}
        for i, p in enumerate(premises):
            if not isinstance(p, dict):
                failures.append(f"premises[{i}]: not an object")
                continue
            verdict = text_of(p.get("verdict"))
            if verdict not in {"deleted", "inverted", "kept"}:
                failures.append(f"premises[{i}].verdict: must be deleted, inverted or kept")
            if verdict in {"deleted", "inverted"}:
                broken += 1
            statement = text_of(p.get("premise"))
            if not statement:
                failures.append(f"premises[{i}].premise: missing")
            else:
                key = normalize(statement)
                if key in seen:
                    failures.append(f"premises[{i}]: repeats premises[{seen[key]}]")
                else:
                    seen[key] = i
            why = text_of(p.get("why"))
            if text_units(why) < mins["premise_why"]:
                failures.append(f"premises[{i}].why: needs at least {mins['premise_why']} units")
            check_padding(f"premises[{i}].why", why, thresholds["min_distinct_ratio"], failures)
        check_padding("premises_note", text_of(concept.get("premises_note")),
                      thresholds["min_distinct_ratio"], failures)
        if broken < counts["min_premises_broken"]:
            failures.append(
                f"no premise was deleted or inverted - a session that kept every premise refined the brief "
                "instead of testing it"
            )
        elif broken < counts["premises_broken_without_note"] and text_units(text_of(concept.get("premises_note"))) < mins["premises_note"]:
            # Honest sessions do sometimes overturn only one premise. That is
            # allowed, but it has to be argued rather than passed over - and
            # inventing a second inversion to hit a quota is worse than saying
            # the others held.
            failures.append(
                f"only {broken} premise was overturned; add premises_note ({mins['premises_note']}+ units) "
                "explaining why the others held rather than inventing an inversion"
            )

    # --- ban contract -------------------------------------------------------
    contract = concept.get("banlist_contract")
    if not isinstance(contract, dict):
        failures.append("banlist_contract: missing - the shared ban contract is what makes 'avoid the obvious' checkable")
        contract = {}
    else:
        instincts = contract.get("model_instincts")
        if not isinstance(instincts, list) or len(instincts) < counts["min_model_instincts"]:
            failures.append(f"banlist_contract.model_instincts: at least {counts['min_model_instincts']} required")
        else:
            bad = [i for i, v in enumerate(instincts) if not isinstance(v, str) or len(v.strip()) < 3]
            if bad:
                failures.append(f"banlist_contract.model_instincts: entries {bad} are empty or not text")
            distinct = {normalize(v) for v in instincts if isinstance(v, str)}
            if len(distinct) < counts["min_model_instincts"]:
                failures.append("banlist_contract.model_instincts: duplicates - the list must hold distinct answers")
        skeleton = text_of(contract.get("skeleton"))
        if text_units(skeleton) < mins["skeleton"]:
            failures.append(f"banlist_contract.skeleton: needs at least {mins['skeleton']} units naming the shared structure")
        if contract.get("user_confirmed") is not True:
            failures.append(
                "banlist_contract.user_confirmed is not true - present the contract to the user as a list of "
                "exclusions and record their agreement before the spec is written"
            )
        if isinstance(contract.get("user_exclusions"), list) and not contract["user_exclusions"]:
            warnings.append("the user added no exclusions of their own; ask once more, it is the cheapest constraint available")

    # --- approaches ---------------------------------------------------------
    approaches = concept.get("approaches")
    chosen_ids: list[str] = []
    if not isinstance(approaches, list) or len(approaches) != counts["approaches"]:
        failures.append(f"approaches: exactly {counts['approaches']} required")
    else:
        # The same structural checks the user-facing divergence gate runs, so a
        # set that would never have been shown cannot arrive here in a spec.
        try:
            verdict = divergence_check(approaches, frames, counts["approaches"])
            failures.extend(f"approaches: {f}" for f in verdict["failures"])
            warnings.extend(verdict["warnings"])
        except EngineError as exc:
            failures.append(f"approaches: {exc}")
        for i, a in enumerate(approaches):
            if not isinstance(a, dict):
                continue
            label = text_of(a.get("id")) or f"approaches[{i}]"
            if "chosen" in a and not isinstance(a["chosen"], bool):
                failures.append(f"{label}.chosen: must be true or false, not {a['chosen']!r}")
            elif a.get("chosen") is True:
                chosen_ids.append(label)
            check_padding(f"{label}.summary", text_of(a.get("summary")), thresholds["min_distinct_ratio"], failures)
        if len(chosen_ids) != 1:
            failures.append(f"{len(chosen_ids)} approaches marked chosen, exactly 1 required")

    # --- the chosen concept -------------------------------------------------
    chosen = concept.get("chosen")
    chosen_text = ""
    if not isinstance(chosen, dict):
        failures.append("chosen: missing")
    else:
        if not text_of(chosen.get("approach_id")):
            failures.append("chosen.approach_id: missing")
        elif chosen_ids and text_of(chosen.get("approach_id")) not in chosen_ids:
            failures.append(f"chosen.approach_id '{chosen.get('approach_id')}' does not match the approach marked chosen")
        for field, key in (("why", "chosen_why"), ("forbids", "forbids"), ("impossible_now", "impossible_now")):
            value = text_of(chosen.get(field))
            if text_units(value) < mins[key]:
                hint = {
                    "why": ", argued against the alternatives",
                    "forbids": " - a design that forbids nothing is a wish list",
                    "impossible_now": " - name what this makes impossible that was possible before",
                }[field]
                failures.append(f"chosen.{field}: needs at least {mins[key]} units{hint}")
            check_padding(f"chosen.{field}", value, thresholds["min_distinct_ratio"], failures)
        forbids = text_of(chosen.get("forbids"))
        if SELF_NEGATING_FORBID.search(forbids):
            warnings.append(
                "chosen.forbids reads as a denial that anything is forbidden; if that is accurate, "
                "the concept is a wish list and the direction needs rework rather than rewording"
            )
        chosen_text = " ".join(text_of(chosen.get(f)) for f in ("why", "forbids", "impossible_now"))

    scene = text_of(concept.get("first_use_scene"))
    if text_units(scene) < mins["first_use_scene"]:
        failures.append(
            f"first_use_scene: needs at least {mins['first_use_scene']} units - one concrete scene, "
            "not a description of the concept"
        )
    check_padding("first_use_scene", scene, thresholds["min_distinct_ratio"], failures)

    # The point of naming the skeleton is that the result must not be another
    # instance of it. Nothing else in the pipeline checks this.
    skeleton = text_of(contract.get("skeleton")) if isinstance(contract, dict) else ""
    if skeleton and (chosen_text or scene):
        # Containment, not similarity: a short skeleton reproduced inside a long
        # passage scores low on overlap while being restated word for word.
        overlap = max(coverage(skeleton, chosen_text), coverage(skeleton, scene))
        if overlap > thresholds["max_skeleton_overlap"]:
            failures.append(
                f"the chosen concept restates the banned skeleton ({overlap:.0%} of it reappears) - "
                "this is the thirteenth version of the answer the session excluded"
            )

    neighbours = concept.get("nearest_existing")
    if not isinstance(neighbours, list) or len(neighbours) < counts["min_nearest_existing"]:
        failures.append(
            "nearest_existing: name what already exists nearby and how this differs, or state what you checked "
            "and found nothing close to"
        )
    else:
        for i, n in enumerate(neighbours):
            if not isinstance(n, dict):
                failures.append(f"nearest_existing[{i}]: not an object")
                continue
            if not text_of(n.get("thing")):
                failures.append(f"nearest_existing[{i}].thing: missing")
            differs = text_of(n.get("how_it_differs"))
            if text_units(differs) < mins["how_it_differs"]:
                failures.append(f"nearest_existing[{i}].how_it_differs: needs at least {mins['how_it_differs']} units")
            check_padding(f"nearest_existing[{i}].how_it_differs", differs, thresholds["min_distinct_ratio"], failures)

    questions = concept.get("open_questions")
    if not isinstance(questions, list) or len(questions) < counts["min_open_questions"]:
        failures.append(
            f"open_questions: at least {counts['min_open_questions']} required - a spec with none has hidden "
            "its unknowns rather than resolved them"
        )
    else:
        marks = tuple(schema["question_marks"])
        seen_q: set[str] = set()
        for i, q in enumerate(questions):
            value = text_of(q)
            if text_units(value) < mins["open_question"]:
                failures.append(f"open_questions[{i}]: too short to be a real question")
                continue
            if not any(mark in value for mark in marks):
                failures.append(f"open_questions[{i}]: not phrased as a question")
            key = normalize(value)
            if key in seen_q:
                failures.append(f"open_questions[{i}]: repeats an earlier question")
            seen_q.add(key)
            if len(content_tokens(value)) < MIN_QUESTION_TOKENS:
                warnings.append(
                    f"open_questions[{i}] names very little: a usable open question points at a specific "
                    "party, artefact or decision, not at 'the remaining considerations'"
                )

    decisions = concept.get("decisions")
    if not isinstance(decisions, list) or len(decisions) < counts["min_decisions"]:
        failures.append(f"decisions: at least {counts['min_decisions']} log entries required")
    else:
        seen_d: set[str] = set()
        for i, d in enumerate(decisions):
            if not isinstance(d, dict):
                failures.append(f"decisions[{i}]: not an object")
                continue
            statement = text_of(d.get("decision"))
            if not statement:
                failures.append(f"decisions[{i}].decision: missing")
            elif normalize(statement) in seen_d:
                failures.append(f"decisions[{i}]: repeats an earlier decision")
            else:
                seen_d.add(normalize(statement))
            if text_units(text_of(d.get("why"))) < mins["decision_why"]:
                failures.append(f"decisions[{i}].why: needs at least {mins['decision_why']} units")
            check_padding(f"decisions[{i}].why", text_of(d.get("why")), thresholds["min_distinct_ratio"], failures)

    handoff = concept.get("handoff")
    if not isinstance(handoff, dict):
        failures.append("handoff: missing - state what happens next and what this spec does not cover")
    else:
        target = text_of(handoff.get("next"))
        if target not in schema["handoff_targets"]:
            failures.append(f"handoff.next: must be one of {', '.join(schema['handoff_targets'])}")
        if text_units(text_of(handoff.get("why"))) < mins["handoff_why"]:
            failures.append(f"handoff.why: needs at least {mins['handoff_why']} units")
        check_padding("handoff.why", text_of(handoff.get("why")), thresholds["min_distinct_ratio"], failures)

    # --- the supplied contract must be this session's contract --------------
    if banlist.get("user_confirmed") is not True:
        failures.append(
            "the supplied ban list is unconfirmed - present it to the user as exclusions and rerun "
            "banlist.py with --confirmed; a sidecar claiming consent proves nothing on its own"
        )
    # An absent field on either side used to skip these comparisons rather than
    # fail them, which made a stripped-down file safer to pass than an honest
    # one from another session.
    #
    # This was a containment ratio between the ban list's brief and the
    # sidecar's free-form `brief`, at 0.5, and it failed in both directions: a
    # ban list whose brief was the single word "ward" passed, because one word
    # is fully contained in anything, while an honest rewording of the same
    # brief in synonyms was refused. A word-overlap score cannot establish
    # provenance and should never have been asked to.
    #
    # So the join is the one the skeleton already uses: the sidecar records the
    # brief the contract was built for, and the two strings must be the same
    # string. That is a consistency check between two files the same caller
    # writes - exactly as strong as the skeleton check and no stronger - and it
    # is stated that way everywhere. It does establish that substituting
    # another session's contract means editing the sidecar to match, and that a
    # contract must name a subject rather than a word. The free-form `brief`,
    # which is meant to restate and expand the ask, is now compared only as a
    # warning, because differing there is what an honest session looks like.
    banlist_brief = text_of(banlist.get("brief"))
    contract_brief = text_of(contract.get("brief")) if isinstance(contract, dict) else ""
    if not banlist_brief:
        failures.append(
            "the ban list names no brief - a contract that does not say what it was built for cannot be "
            "shown to belong to this session"
        )
    elif text_units(banlist_brief) < mins["contract_brief"] or \
            len(content_tokens(banlist_brief)) < counts["min_brief_tokens"]:
        failures.append(
            f"the ban list's brief '{banlist_brief[:40]}' names a word rather than a subject "
            f"(at least {mins['contract_brief']} units and {counts['min_brief_tokens']} content words). "
            "A one-word brief is contained in every other brief, which is how a contract from another "
            "session used to pass this check"
        )
    if not contract_brief:
        failures.append(
            "banlist_contract.brief: missing - the sidecar has to record the brief the contract was built "
            "for, or nothing joins the two files but the caller's word"
        )
    elif banlist_brief and normalize(contract_brief) != normalize(banlist_brief):
        failures.append(
            "the ban list was built for a different brief than the one concept.json records: ban list "
            f"'{banlist_brief[:50]}' vs sidecar '{contract_brief[:50]}'. A contract gates the session it "
            "was built in, and the two files must at least agree on which session that is"
        )
    if banlist_brief and brief:
        shared = max(coverage(banlist_brief, brief), coverage(brief, banlist_brief))
        if shared < thresholds["min_brief_overlap"]:
            warnings.append(
                f"the concept's brief and the contract's share little vocabulary ({shared:.0%}): "
                f"'{banlist_brief[:40]}' vs '{brief[:40]}'. Rewording in synonyms looks the same as "
                "swapping the contract from here, so this is a note to read, not a verdict"
            )

    contract_skeleton = text_of(contract.get("skeleton")) if isinstance(contract, dict) else ""
    banlist_skeleton = text_of(banlist.get("skeleton"))
    if not banlist_skeleton:
        failures.append(
            "the ban list names no skeleton - a contract without one cannot be the contract this "
            "session built, and the skeleton is the thing the concept must not restate"
        )
    elif contract_skeleton and normalize(contract_skeleton) != normalize(banlist_skeleton):
        failures.append(
            "the skeleton in concept.json and the one in the ban list differ - the gate would be checking "
            "one contract and linting another"
        )
    sidecar_instincts = {normalize(v) for v in (contract.get("model_instincts") or []) if isinstance(v, str)}
    banlist_instincts = {normalize(v) for v in banlist.get("model_instincts", []) if isinstance(v, str)}
    if sidecar_instincts and not sidecar_instincts <= banlist_instincts:
        missing = sorted(sidecar_instincts - banlist_instincts)[:3]
        failures.append(
            f"instincts in concept.json are absent from the ban list ({', '.join(missing)}...) - "
            "the two were built from different sessions"
        )
    failures.extend(replay_contract(contract if isinstance(contract, dict) else {}, banlist, cliches, warnings))

    # --- the user's own long exclusions ------------------------------------
    manual = [m for m in banlist.get("manual_checks", []) if isinstance(m, dict)]
    if manual:
        # An answer is joined to a check by id, and the id is written by the same
        # caller that writes both files. Two checks sharing one id were therefore
        # discharged by one written answer, and the second exclusion the user
        # asked for was never answered. The join is still by id - that is what
        # the sidecar records - but a collision on either side is now a failure
        # rather than a silent merge, so the cheap version of this costs a
        # rejected contract.
        ids = [text_of(m.get("id")) for m in manual]
        repeated = sorted({i for i in ids if ids.count(i) > 1})
        if repeated:
            failures.append(
                f"the ban list reuses manual check id(s) ({', '.join(repeated)}) - answers are joined to "
                "checks by id, so two exclusions sharing one id would be discharged by one written answer"
            )
        cleared = contract.get("manual_checks_cleared") if isinstance(contract, dict) else None
        cleared_map: dict[str, str] = {}
        if isinstance(cleared, list):
            cleared_ids = [text_of(e.get("id")) for e in cleared if isinstance(e, dict) and text_of(e.get("id"))]
            repeated_cleared = sorted({i for i in cleared_ids if cleared_ids.count(i) > 1})
            if repeated_cleared:
                failures.append(
                    f"banlist_contract.manual_checks_cleared reuses id(s) ({', '.join(repeated_cleared)}) - "
                    "each exclusion is answered once, in its own note"
                )
            for entry in cleared:
                if isinstance(entry, dict) and text_of(entry.get("id")):
                    cleared_map[text_of(entry.get("id"))] = text_of(entry.get("note"))
        # A written note is required for the *user's* long exclusions, which is
        # what SKILL.md, the template and the shipped example all say. It used
        # to be required for every long entry, model instincts included, and
        # that was invisible in a product brief and unavoidable outside one: a
        # product instinct is a three-word noun phrase and becomes a matchable
        # ban, while a story, ritual or mechanic instinct is naturally a clause
        # and became a manual check. The shipped product example carries zero
        # of them; a narrative brief produced twelve, so a user on such a brief
        # met twelve mandatory notes no document had told them about. The rule
        # was the thing that disagreed with every instruction, so the rule
        # changed. The model's long instincts are still carried in the
        # contract, still replayed, and now listed as a warning to reread the
        # spec against - what the skeleton check and a reader are for.
        unanswered_model: list[str] = []
        for m in manual:
            mid = text_of(m.get("id"))
            note = cleared_map.get(mid, "")
            check_padding(f"manual_checks_cleared[{mid}]", note, thresholds["min_distinct_ratio"], failures)
            if text_units(note) >= mins["manual_check_note"]:
                continue
            if text_of(m.get("source")) == "model":
                unanswered_model.append(f"{mid} ({text_of(m.get('statement'))[:50]})")
                continue
            failures.append(
                f"banlist_contract.manual_checks_cleared: exclusion '{mid}' "
                f"({text_of(m.get('statement'))[:60]}...) has no note saying how the concept avoids it. "
                "Long exclusions cannot be matched mechanically, so they are answered here or not at all."
            )
        if unanswered_model:
            warnings.append(
                f"{len(unanswered_model)} of your own long instincts are too long to match literally and "
                f"carry no written answer ({'; '.join(unanswered_model[:3])}...). Only the user's "
                "exclusions require one, so this is a reread rather than a failure: check the concept "
                "against them yourself, because nothing mechanical is checking them"
            )

    markers = schema["placeholder_markers"]
    for path, value in walk_strings(concept):
        norm = normalize(value)
        for marker in markers:
            if re.search(rf"(?<![\w]){re.escape(marker)}(?![\w])", norm):
                failures.append(f"{path}: contains the placeholder '{marker}'")
                break

    return {"failures": failures, "warnings": warnings}



BIND = re.compile(r"<!--\s*bind:\s*([A-Za-z0-9_.\[\]]+)\s*-->(.*?)<!--\s*/bind\s*-->", re.S)
_QUOTED = re.compile(r"^\s*(?:>|```|~~)", re.M)


def canonical(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).split())


def bound_blocks(markdown: str) -> dict[str, list[tuple[str, int]]]:
    """Marked assertions, with where each one starts.

    The offset matters: a binding satisfied by text sitting in the ban list or
    the decision log is not the spec asserting it.
    """
    out: dict[str, list[tuple[str, int]]] = {}
    for match in BIND.finditer(markdown):
        out.setdefault(match.group(1), []).append((match.group(2), match.start()))
    return out


def _is_quoted(body: str) -> bool:
    return bool(_QUOTED.search(body))


def _inside_section(markdown: str, offset: int, section: str) -> bool:
    marks = [(m.start(), m.group(1).lower()) for m in SECTION_MARKER.finditer(markdown)]
    current = None
    for start, name in marks:
        if start <= offset:
            current = name
        else:
            break
    return current == section


def check_markdown(markdown: str, schema: dict[str, Any], concept: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    thresholds = schema["thresholds"]
    required = [s["id"] for s in schema["required_markdown_sections"]]
    notes = {s["id"]: s["note"] for s in schema["required_markdown_sections"]}
    found = split_sections(markdown)
    found_ids = [name for name, _ in found]

    for anchor in required:
        if anchor not in found_ids:
            failures.append(f"markdown: missing section marker <!-- section: {anchor} --> ({notes[anchor]})")

    if schema.get("sections_must_be_in_order"):
        ordered = [name for name in found_ids if name in required]
        expected = [name for name in required if name in ordered]
        if ordered != expected:
            failures.append(
                "markdown: sections are out of order - the ban contract in particular must sit where the "
                f"template puts it (expected {' → '.join(expected)}, got {' → '.join(ordered)})"
            )

    minimum = schema["min_units"]["section_body"]
    for name, body in found:
        if name not in required:
            continue
        shown = visible_text(body).strip()
        if text_units(shown) < minimum:
            failures.append(
                f"markdown: section '{name}' has {text_units(shown)} units a reader can see, needs {minimum} "
                "(HTML comments and fenced blocks do not count)"
            )
        elif distinct_ratio(shown) < schema["thresholds"]["min_distinct_ratio"]:
            failures.append(f"markdown: section '{name}' is repeated filler rather than content")

    # The document must actually contain the concept it is the spec for, and
    # "contain" cannot be a similarity score. A fuzzy match cannot tell the
    # difference between a proposition being asserted and the same words being
    # quoted inside a sentence that rejects them - "we considered 'X' but
    # ultimately allow it" scored a perfect match against X. So the assertions
    # are marked, and compared exactly.
    spans = bound_blocks(markdown)
    section_of = {name: body for name, body in found}
    chosen = concept.get("chosen") if isinstance(concept.get("chosen"), dict) else {}
    bindings = [
        ("chosen.forbids", text_of(chosen.get("forbids")), "concept"),
        ("chosen.impossible_now", text_of(chosen.get("impossible_now")), "concept"),
        ("first_use_scene", text_of(concept.get("first_use_scene")), "first-use"),
    ]
    questions = concept.get("open_questions")
    for i, q in enumerate(questions if isinstance(questions, list) else []):
        bindings.append((f"open_questions[{i}]", text_of(q), "open-questions"))

    for label, value, section in bindings:
        if not value:
            continue
        blocks = spans.get(label)
        if not blocks:
            failures.append(
                f"markdown: no <!-- bind: {label} --> block. The spec has to assert this in its own "
                "body, marked, so the gate is reading an assertion rather than guessing from word overlap")
            continue
        if len(blocks) > 1:
            failures.append(f"markdown: <!-- bind: {label} --> appears {len(blocks)} times; it must appear once")
            continue
        body, offset = blocks[0]
        if canonical(visible_text(body)) != canonical(value):
            failures.append(
                f"markdown: the <!-- bind: {label} --> block is not what concept.json says. If the wording "
                "was revised or translated, update the sidecar to the delivered wording and re-gate")
        if not _inside_section(markdown, offset, section):
            failures.append(
                f"markdown: <!-- bind: {label} --> is not inside the '{section}' section - a refusal "
                "quoted in the ban list or logged as rejected is not the same as one the spec makes")
        if _is_quoted(body):
            failures.append(
                f"markdown: the <!-- bind: {label} --> block is a quotation or a struck-through line. "
                "A bound assertion must be plain prose the spec is making in its own voice")

    unknown = sorted(k for k in spans if k not in {b[0] for b in bindings})
    if unknown:
        failures.append(f"markdown: bind blocks for fields that are not bindable: {', '.join(unknown)}")

    for marker in schema["placeholder_markers"]:
        if re.search(rf"(?<![\w]){re.escape(marker)}(?![\w])", normalize(markdown)):
            failures.append(f"markdown: contains the placeholder '{marker}'")
    return failures


def check_mentions(mentions: list[tuple[str, set[str]]], entries: list[dict[str, Any]],
                   patterns: list[dict[str, Any]]) -> list[str]:
    """A mention marker has to name a rule that exists, and name one.

    The marker is the author asserting that a banned word appears here quoted
    or denied rather than used. The gate cannot check that assertion - a regex
    cannot tell an assertion from a quotation, which is the whole reason the
    marker exists. What it can check is that the release is specific: a real id,
    per span, and printed in the verdict so a reviewer sees every one.
    """
    failures: list[str] = []
    known = {str(e.get("id")) for e in entries} | {str(p.get("id")) for p in patterns}
    for body, ids in mentions:
        if not ids:
            failures.append(
                f"markdown: a mention block names no rule id ({body.strip()[:60]}...) - a release that "
                "names nothing releases everything, so name the id the span is quoting or denying"
            )
            continue
        unknown = sorted(i for i in ids if i not in known)
        if unknown:
            failures.append(
                f"markdown: mention block releases unknown rule id(s) {', '.join(unknown)} - the id must be "
                "one this session lints against, as printed by cliche_lint.py in square brackets"
            )
    return failures


def describe_mentions(mentions: list[tuple[str, set[str]]]) -> list[str]:
    return [
        f"the spec marks '{body.strip()[:60]}' as mentioning rather than using {', '.join(sorted(ids))}; "
        "the gate cannot verify that, it only records that you claimed it here and nowhere else"
        for body, ids in mentions if ids
    ]


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        # No --schema flag: a caller-supplied schema could set every floor to
        # zero and leave a gate that reports success without checking anything.
        schema = load_deck("spec-schema")

        concept = require_mapping(read_json_arg(args.concept), "concept")
        banlist = load_banlist(args.banlist)
        frames = load_deck("frames")
        cliches = load_deck("cliches")
        try:
            markdown = Path(args.markdown).read_text(encoding="utf-8")
        except OSError as exc:
            raise EngineError(f"cannot read {args.markdown}: {exc}") from exc

        result = check_concept(concept, schema, frames, banlist, cliches)
        result["failures"].extend(check_markdown(markdown, schema, concept))

        entries = lint_entries(banlist, cliches)
        patterns = lint_patterns(banlist, cliches)
        mentions = extract_mentions(markdown)
        result["failures"].extend(check_mentions(mentions, entries, patterns))
        result["warnings"].extend(describe_mentions(mentions))
        blob = "\n".join(
            v for path, v in walk_strings(concept) if not path.startswith("banlist_contract")
        ) + "\n" + strip_mention_markers(lintable_markdown(markdown))
        findings = lint_text(blob, entries, patterns, set(), mentions)
        banned = [f for f in findings if f["tier"] == "ban"]
        if banned:
            result["failures"].append(
                f"{len(banned)} banned phrase(s) in the spec: " + ", ".join(sorted({f['match'] for f in banned}))
            )
        verdict = {
            "engine_version": VERSION,
            "passed": not result["failures"],
            "failures": result["failures"],
            "warnings": result["warnings"],
            "lint_findings": findings,
        }
    except EngineError as exc:
        die(str(exc), 1)
        return 1

    if args.json:
        print(json.dumps(verdict, ensure_ascii=False, indent=2))
    else:
        for w in verdict["warnings"]:
            print(f"WARN  {w}")
        for f in verdict["failures"]:
            print(f"FAIL  {f}")
        print("PASSED - the required work is present. Now ask the user to review the spec."
              if verdict["passed"]
              else "GATE FAILED - do not put this in front of the user; fix the spec first.")
    return 0 if verdict["passed"] else GATE_FAIL


if __name__ == "__main__":
    raise SystemExit(main())
