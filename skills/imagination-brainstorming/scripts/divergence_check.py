#!/usr/bin/env python3
"""divergence_check.py - refuse a set of approaches that is really one approach.

The standard "here are three options" move usually ships one real proposal and
two decoys: same premise, same failure, different wrapper. This check makes
that visible before the user is asked to choose.

It verifies that the approaches sit in different frame categories, that their
summaries do not restate each other, that they fail in different ways, and that
exactly one occupies the unsafe seat and is described in comparable detail to
the rest. Overlap is measured with a crude token score - it is a floor, not a
semantic judgement. Passing it does not mean the approaches are good; failing
it means they are not alternatives.

Input: approaches JSON - either a list, or an object with an "approaches" key
(so concept.json and deal.py output both work).

Usage:
  divergence_check.py --approaches ./work/concept.json --banlist ./work/banlist.json

Exit codes: 0 ok, 1 usage error, 3 the set does not diverge.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from engine import (  # type: ignore
        VERSION, UsageParser, EngineError, csv_list, die, distinct_ratio, jaccard, load_banlist, load_deck,
        lint_text, normalize, read_json_arg, text_units,
    )
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from engine import (  # type: ignore
        VERSION, UsageParser, EngineError, csv_list, die, distinct_ratio, jaccard, load_banlist, load_deck,
        lint_text, normalize, read_json_arg, text_units,
    )

FAIL_CODE = 3
DEFAULT_COUNT = 3
SUMMARY_MAX_OVERLAP = 0.55
FAILURE_MAX_OVERLAP = 0.50
MIN_SUMMARY_UNITS = 120
MIN_FAILURE_UNITS = 60
DETAIL_RATIO = 0.4  # shortest summary must be at least this fraction of the longest
MIN_DISTINCT_RATIO = 0.3


def build_parser() -> argparse.ArgumentParser:
    p = UsageParser(description="Check that a set of approaches genuinely diverges.")
    p.add_argument("--approaches", required=True, help="JSON list or object with an 'approaches' key, or '-'")
    p.add_argument("--banlist", default=None, help="banlist.json; approaches are linted against it when given")
    p.add_argument("--count", type=int, default=DEFAULT_COUNT,
                   help=f"how many approaches are expected (default and minimum {DEFAULT_COUNT})")
    # No --allow here. An exception granted at verdict time is granted by the
    # same party the verdict is about, which is the identical bypass as a
    # threshold override. A legitimate exception is made once, while the ban
    # contract is being built (banlist.py --allow), recorded there with an id
    # and a reason, shown to the user before they confirm it, and inherited by
    # every later gate.
    p.add_argument("--json", action="store_true", help="emit the verdict as JSON")
    return p


def load_approaches(value: str) -> list[dict[str, Any]]:
    data = read_json_arg(value)
    if isinstance(data, dict):
        data = data.get("approaches")
    if not isinstance(data, list):
        raise EngineError("expected a JSON list of approaches, or an object with an 'approaches' key")
    for item in data:
        if not isinstance(item, dict):
            raise EngineError("every approach must be a JSON object")
    return data


def text_of(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def check(approaches: list[dict[str, Any]], frames: dict[str, Any], count: int) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []

    if count < DEFAULT_COUNT:
        # Lowering the count would turn the check into a formality: with one or
        # two approaches there is nothing to compare, and every pairwise test
        # below silently passes.
        raise EngineError(f"--count cannot be lower than {DEFAULT_COUNT}; fewer approaches is not a choice")

    if len(approaches) != count:
        failures.append(f"{len(approaches)} approaches supplied, {count} expected")

    frame_table = {f["id"]: f for f in frames["frames"]}
    ids, categories, unsafe = [], [], []
    seen_ids: dict[str, int] = {}
    for i, a in enumerate(approaches):
        label = text_of(a.get("id")) or text_of(a.get("frame_id")) or f"#{i + 1}"
        ids.append(label)
        explicit = text_of(a.get("id"))
        if explicit:
            if explicit in seen_ids:
                failures.append(f"two approaches share the id '{explicit}'; downstream nothing can tell them apart")
            seen_ids[explicit] = i
        frame_id = text_of(a.get("frame_id"))
        if not frame_id:
            failures.append(f"{label}: no frame_id - an approach that came from nowhere cannot be shown to differ")
        elif frame_id not in frame_table:
            failures.append(f"{label}: unknown frame_id '{frame_id}'")
        else:
            categories.append(frame_table[frame_id]["category"])
        if text_units(text_of(a.get("summary"))) < MIN_SUMMARY_UNITS:
            failures.append(f"{label}: summary under {MIN_SUMMARY_UNITS} units - too thin to be judged against the others")
        if text_units(text_of(a.get("failure_mode"))) < MIN_FAILURE_UNITS:
            failures.append(f"{label}: failure_mode under {MIN_FAILURE_UNITS} units - state how this one actually fails here")
        if "unsafe" in a:
            # One field, one meaning. The alias let an approach be seated in the
            # check while every documented unsafe_seat field said false.
            failures.append(f"{label}: use 'unsafe_seat'; the 'unsafe' alias is not read")
        if "unsafe_seat" in a and not isinstance(a["unsafe_seat"], bool):
            failures.append(f"{label}.unsafe_seat: must be true or false, not {a['unsafe_seat']!r}")
        if a.get("unsafe_seat") is True:
            unsafe.append(label)
        failure_mode = text_of(a.get("failure_mode"))
        if failure_mode and distinct_ratio(failure_mode) < MIN_DISTINCT_RATIO:
            failures.append(f"{label}.failure_mode: repeated filler rather than content")
        summary = text_of(a.get("summary"))
        if summary and distinct_ratio(summary) < MIN_DISTINCT_RATIO:
            failures.append(f"{label}.summary: repeated filler rather than content")

    if len(set(categories)) != len(categories):
        failures.append("two approaches share a frame category, so they are variants rather than alternatives")

    if len(unsafe) != 1:
        failures.append(
            f"{len(unsafe)} approaches marked as the unsafe seat, exactly 1 required - "
            "without it the set collapses into one proposal and two decoys"
        )

    summaries = [text_of(a.get("summary")) for a in approaches]
    failure_modes = [text_of(a.get("failure_mode")) for a in approaches]
    for field, values in (("summary", summaries), ("failure_mode", failure_modes)):
        seen: dict[str, str] = {}
        for label, value in zip(ids, values):
            key = normalize(value)
            if not key:
                continue
            if key in seen:
                failures.append(f"{seen[key]} and {label} have an identical {field}")
            else:
                seen[key] = label
    lengths = [len(s) for s in summaries if s]
    if lengths and min(lengths) < DETAIL_RATIO * max(lengths):
        failures.append(
            "one approach is described in far less detail than another; unequal detail is how a decoy is built"
        )

    pairs: list[dict[str, Any]] = []
    for i in range(len(approaches)):
        for j in range(i + 1, len(approaches)):
            s = jaccard(summaries[i], summaries[j])
            f = jaccard(failure_modes[i], failure_modes[j])
            pairs.append({"a": ids[i], "b": ids[j], "summary_overlap": round(s, 2), "failure_overlap": round(f, 2)})
            if s > SUMMARY_MAX_OVERLAP:
                failures.append(f"{ids[i]} and {ids[j]} restate each other (summary overlap {s:.2f})")
            elif s > SUMMARY_MAX_OVERLAP - 0.2:
                warnings.append(
                    f"{ids[i]} and {ids[j]} are close (summary overlap {s:.2f}); read them again as one sentence each"
                )
            if f > FAILURE_MAX_OVERLAP:
                failures.append(
                    f"{ids[i]} and {ids[j]} fail the same way (failure overlap {f:.2f}) - "
                    "two ideas that die of the same cause are one idea"
                )
            elif f > FAILURE_MAX_OVERLAP - 0.15:
                warnings.append(f"{ids[i]} and {ids[j]} fail in similar ways (overlap {f:.2f}); worth rewriting one")

    # Synonyms defeat token overlap: three descriptions of one idea, written in
    # different words, score low and pass. Nothing in the standard library can
    # tell them apart, so the honest move is to say so where it will be read.
    warnings.append(
        "This check is a floor: it catches restatement, shared failure modes and unequal detail. "
        "It cannot tell whether three descriptions are one idea in three vocabularies - "
        "read them as one sentence each and decide that yourself."
    )

    return {
        "engine_version": VERSION,
        "passed": not failures,
        "count": len(approaches),
        "categories": categories,
        "unsafe_seat": unsafe,
        "pairs": pairs,
        "failures": failures,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        frames = load_deck("frames")
        approaches = load_approaches(args.approaches)
        verdict = check(approaches, frames, args.count)
        lint_findings: list[dict[str, Any]] = []
        if args.banlist:
            banlist = load_banlist(args.banlist)
            blob = "\n".join(
                f"{a.get('summary', '')}\n{a.get('failure_mode', '')}" for a in approaches
            )
            lint_findings = lint_text(
                blob, banlist.get("entries", []), banlist.get("structural_patterns", []),
                set(),
            )
            banned = [f for f in lint_findings if f["tier"] == "ban"]
            if banned:
                verdict["failures"].append(
                    f"{len(banned)} banned phrase(s) in the approaches: "
                    + ", ".join(sorted({f['match'] for f in banned}))
                )
                verdict["passed"] = False
        verdict["lint_findings"] = lint_findings
    except EngineError as exc:
        die(str(exc), 1)
        return 1

    if args.json:
        print(json.dumps(verdict, ensure_ascii=False, indent=2))
    else:
        for p in verdict["pairs"]:
            print(f"overlap  {p['a']} vs {p['b']}: summary {p['summary_overlap']}, failure {p['failure_overlap']}")
        for w in verdict["warnings"]:
            print(f"WARN  {w}")
        for f in verdict["failures"]:
            print(f"FAIL  {f}")
        print("PASSED - these are alternatives, not variants." if verdict["passed"]
              else "DIVERGENCE FAILED - redraw or rewrite before showing the user a choice.")
    return 0 if verdict["passed"] else FAIL_CODE


if __name__ == "__main__":
    raise SystemExit(main())
