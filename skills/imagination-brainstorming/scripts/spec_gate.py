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
from pathlib import Path
from typing import Any

try:
    from engine import (  # type: ignore
        VERSION, UsageParser, EngineError, content_tokens, coverage, csv_list, die, distinct_ratio, jaccard,
        load_banlist, load_deck, lint_text, normalize, passage_coverage, read_json_arg, require_mapping,
    )
    from divergence_check import check as divergence_check  # type: ignore
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from engine import (  # type: ignore
        VERSION, UsageParser, EngineError, content_tokens, coverage, csv_list, die, distinct_ratio, jaccard,
        load_banlist, load_deck, lint_text, normalize, passage_coverage, read_json_arg, require_mapping,
    )
    from divergence_check import check as divergence_check  # type: ignore

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
    p.add_argument("--allow", default=None, help="comma-separated lint entry ids to ignore")
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


def check_concept(concept: dict[str, Any], schema: dict[str, Any], frames: dict[str, Any],
                  banlist: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    counts = schema["counts"]
    mins = schema["min_chars"]
    thresholds = schema["thresholds"]

    brief = text_of(concept.get("brief"))
    if len(brief) < mins["brief"]:
        failures.append(f"brief: needs at least {mins['brief']} chars - state what was asked and what you learned it actually is")
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
            if len(why) < mins["premise_why"]:
                failures.append(f"premises[{i}].why: needs at least {mins['premise_why']} chars")
            check_padding(f"premises[{i}].why", why, thresholds["min_distinct_ratio"], failures)
        check_padding("premises_note", text_of(concept.get("premises_note")),
                      thresholds["min_distinct_ratio"], failures)
        if broken < counts["min_premises_broken"]:
            failures.append(
                f"no premise was deleted or inverted - a session that kept every premise refined the brief "
                "instead of testing it"
            )
        elif broken < counts["premises_broken_without_note"] and len(text_of(concept.get("premises_note"))) < mins["premises_note"]:
            # Honest sessions do sometimes overturn only one premise. That is
            # allowed, but it has to be argued rather than passed over - and
            # inventing a second inversion to hit a quota is worse than saying
            # the others held.
            failures.append(
                f"only {broken} premise was overturned; add premises_note ({mins['premises_note']}+ chars) "
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
        if len(skeleton) < mins["skeleton"]:
            failures.append(f"banlist_contract.skeleton: needs at least {mins['skeleton']} chars naming the shared structure")
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
            if len(value) < mins[key]:
                hint = {
                    "why": ", argued against the alternatives",
                    "forbids": " - a design that forbids nothing is a wish list",
                    "impossible_now": " - name what this makes impossible that was possible before",
                }[field]
                failures.append(f"chosen.{field}: needs at least {mins[key]} chars{hint}")
            check_padding(f"chosen.{field}", value, thresholds["min_distinct_ratio"], failures)
        forbids = text_of(chosen.get("forbids"))
        if SELF_NEGATING_FORBID.search(forbids):
            warnings.append(
                "chosen.forbids reads as a denial that anything is forbidden; if that is accurate, "
                "the concept is a wish list and the direction needs rework rather than rewording"
            )
        chosen_text = " ".join(text_of(chosen.get(f)) for f in ("why", "forbids", "impossible_now"))

    scene = text_of(concept.get("first_use_scene"))
    if len(scene) < mins["first_use_scene"]:
        failures.append(
            f"first_use_scene: needs at least {mins['first_use_scene']} chars - one concrete scene, "
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
            if len(differs) < mins["how_it_differs"]:
                failures.append(f"nearest_existing[{i}].how_it_differs: needs at least {mins['how_it_differs']} chars")
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
            if len(value) < mins["open_question"]:
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
            if len(text_of(d.get("why"))) < mins["decision_why"]:
                failures.append(f"decisions[{i}].why: needs at least {mins['decision_why']} chars")
            check_padding(f"decisions[{i}].why", text_of(d.get("why")), thresholds["min_distinct_ratio"], failures)

    handoff = concept.get("handoff")
    if not isinstance(handoff, dict):
        failures.append("handoff: missing - state what happens next and what this spec does not cover")
    else:
        target = text_of(handoff.get("next"))
        if target not in schema["handoff_targets"]:
            failures.append(f"handoff.next: must be one of {', '.join(schema['handoff_targets'])}")
        if len(text_of(handoff.get("why"))) < mins["handoff_why"]:
            failures.append(f"handoff.why: needs at least {mins['handoff_why']} chars")
        check_padding("handoff.why", text_of(handoff.get("why")), thresholds["min_distinct_ratio"], failures)

    # --- the supplied contract must be this session's contract --------------
    if banlist.get("user_confirmed") is not True:
        failures.append(
            "the supplied ban list is unconfirmed - present it to the user as exclusions and rerun "
            "banlist.py with --confirmed; a sidecar claiming consent proves nothing on its own"
        )
    contract_skeleton = text_of(contract.get("skeleton")) if isinstance(contract, dict) else ""
    banlist_skeleton = text_of(banlist.get("skeleton"))
    if contract_skeleton and banlist_skeleton and normalize(contract_skeleton) != normalize(banlist_skeleton):
        failures.append(
            "the skeleton in concept.json and the one in the ban list differ - the gate would be checking "
            "one contract and linting another"
        )
    sidecar_instincts = {normalize(v) for v in (contract.get("model_instincts") or []) if isinstance(v, str)}
    banlist_instincts = {normalize(v) for v in banlist.get("model_instincts", []) if isinstance(v, str)}
    if sidecar_instincts and banlist_instincts and not sidecar_instincts <= banlist_instincts:
        missing = sorted(sidecar_instincts - banlist_instincts)[:3]
        failures.append(
            f"instincts in concept.json are absent from the ban list ({', '.join(missing)}...) - "
            "the two were built from different sessions"
        )

    # --- the user's own long exclusions ------------------------------------
    manual = [m for m in banlist.get("manual_checks", []) if isinstance(m, dict)]
    if manual:
        cleared = contract.get("manual_checks_cleared") if isinstance(contract, dict) else None
        cleared_map: dict[str, str] = {}
        if isinstance(cleared, list):
            for entry in cleared:
                if isinstance(entry, dict) and text_of(entry.get("id")):
                    cleared_map[text_of(entry.get("id"))] = text_of(entry.get("note"))
        for m in manual:
            mid = text_of(m.get("id"))
            note = cleared_map.get(mid, "")
            check_padding(f"manual_checks_cleared[{mid}]", note, thresholds["min_distinct_ratio"], failures)
            if len(note) < mins["manual_check_note"]:
                failures.append(
                    f"banlist_contract.manual_checks_cleared: exclusion '{mid}' "
                    f"({text_of(m.get('statement'))[:60]}...) has no note saying how the concept avoids it. "
                    "Long exclusions cannot be matched mechanically, so they are answered here or not at all."
                )

    markers = schema["placeholder_markers"]
    for path, value in walk_strings(concept):
        norm = normalize(value)
        for marker in markers:
            if re.search(rf"(?<![\w]){re.escape(marker)}(?![\w])", norm):
                failures.append(f"{path}: contains the placeholder '{marker}'")
                break

    return {"failures": failures, "warnings": warnings}


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

    minimum = schema["min_chars"]["section_body"]
    for name, body in found:
        if name not in required:
            continue
        shown = visible_text(body).strip()
        if len(shown) < minimum:
            failures.append(
                f"markdown: section '{name}' has {len(shown)} chars a reader can see, needs {minimum} "
                "(HTML comments and fenced blocks do not count)"
            )
        elif distinct_ratio(shown) < schema["thresholds"]["min_distinct_ratio"]:
            failures.append(f"markdown: section '{name}' is repeated filler rather than content")

    # The document must actually contain the concept it is the spec for.
    # Requiring the file to exist proved nothing while any ten paragraphs
    # carrying the right markers would pass.
    shown_all = visible_text(markdown)
    chosen = concept.get("chosen") if isinstance(concept.get("chosen"), dict) else {}
    bindings = [
        ("chosen.forbids", text_of(chosen.get("forbids"))),
        ("first_use_scene", text_of(concept.get("first_use_scene"))),
    ]
    for i, q in enumerate(concept.get("open_questions", [])[:2]):
        bindings.append((f"open_questions[{i}]", text_of(q)))
    for label, value in bindings:
        if value and passage_coverage(value, shown_all) < thresholds["min_passage_coverage"]:
            failures.append(
                f"markdown: does not contain {label} from the sidecar - the written spec and concept.json "
                "must be the same piece of work. Token overlap is not enough here: the passage itself has "
                "to appear, because in a long spec the words of any paragraph are scattered through the rest."
            )

    for marker in schema["placeholder_markers"]:
        if re.search(rf"(?<![\w]){re.escape(marker)}(?![\w])", normalize(markdown)):
            failures.append(f"markdown: contains the placeholder '{marker}'")
    return failures


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        # No --schema flag: a caller-supplied schema could set every floor to
        # zero and leave a gate that reports success without checking anything.
        schema = load_deck("spec-schema")

        concept = require_mapping(read_json_arg(args.concept), "concept")
        banlist = load_banlist(args.banlist)
        frames = load_deck("frames")
        try:
            markdown = Path(args.markdown).read_text(encoding="utf-8")
        except OSError as exc:
            raise EngineError(f"cannot read {args.markdown}: {exc}") from exc

        result = check_concept(concept, schema, frames, banlist)
        result["failures"].extend(check_markdown(markdown, schema, concept))

        blob = "\n".join(
            v for path, v in walk_strings(concept) if not path.startswith("banlist_contract")
        ) + "\n" + lintable_markdown(markdown)
        findings = lint_text(
            blob, banlist.get("entries", []), banlist.get("structural_patterns", []),
            set(csv_list(args.allow)),
        )
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
