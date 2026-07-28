#!/usr/bin/env python3
"""banlist.py - build the shared ban contract for a session.

The imagination engine burns the model's first instincts privately. In a
brainstorming session that same list is worth more said out loud: the user
almost always recognises two or three of them as what they were already
picturing, and their own "not another X" is the highest-value constraint
available. So the contract has three parts - the model's instincts, the
skeleton those instincts share, and the user's own exclusions - and it is
presented as a list of exclusions, never as a menu of suggestions.

Short entries (<= 6 words) become matchable bans. Longer ones are kept as
manual reminders, because matching a fifteen-word sentence literally would
catch nothing while pretending to protect something.

Usage:
  banlist.py --brief "..." --instincts instincts.txt --skeleton "..." \
             --user user-exclusions.txt --confirmed --out ./work

Exit codes: 0 ok, 1 usage or deck error, 2 the contract is incomplete.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    from engine import (  # type: ignore
        VERSION, UsageParser, EngineError, csv_list, deck_lint_entries, die, load_deck, normalize,
        read_text_arg, text_units, write_json,
    )
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from engine import (  # type: ignore
        VERSION, UsageParser, EngineError, csv_list, deck_lint_entries, die, load_deck, normalize,
        read_text_arg, text_units, write_json,
    )

MIN_INSTINCTS = 8
MIN_SKELETON_UNITS = 40
MATCHABLE_MAX_WORDS = 6
BULLET = re.compile(r"^\s*(?:[-*+•]|\d+[.)])\s*")
GATE_FAIL = 2


def build_parser() -> argparse.ArgumentParser:
    p = UsageParser(description="Build the shared ban contract from model instincts and user exclusions.")
    p.add_argument("--brief", required=True, help="the idea being brainstormed")
    p.add_argument("--instincts", required=True, help="file of the model's most likely answers, one per line, or '-'")
    p.add_argument("--skeleton", required=True, help="the structure the instincts share, in one sentence")
    p.add_argument("--user", default=None, help="file of the user's own exclusions, one per line, or '-'")
    p.add_argument("--extra", default=None, help="comma-separated extra phrases to ban")
    p.add_argument("--allow", default=None, help="comma-separated cliche ids to release (the user asked for that thing)")
    p.add_argument("--confirmed", action="store_true", help="record that the user has seen the contract and agreed to it")
    p.add_argument("--min-instincts", type=int, default=MIN_INSTINCTS,
                   help=f"raise the minimum above the floor of {MIN_INSTINCTS}; it cannot be lowered")
    p.add_argument("--out", default=None, help="directory to write banlist.json into")
    p.add_argument("--json", action="store_true", help="print the contract as JSON only")
    return p


def parse_lines(raw: str) -> list[str]:
    lines: list[str] = []
    seen: set[str] = set()
    for line in raw.splitlines():
        cleaned = BULLET.sub("", line).strip().strip('"').strip()
        if len(cleaned) < 3 or cleaned.startswith("#"):
            continue
        key = normalize(cleaned)
        if key in seen:
            continue
        seen.add(key)
        lines.append(cleaned)
    return lines


def classify(items: list[str], prefix: str, group: str, source: str,
             entries: list[dict[str, Any]], manual: list[dict[str, str]]) -> None:
    for i, item in enumerate(items, start=1):
        words = [w for w in re.split(r"\s+", item.strip()) if w]
        if len(words) <= MATCHABLE_MAX_WORDS:
            entries.append({
                "id": f"{prefix}-{i:02d}", "phrase": item, "tier": "ban",
                "group": group, "source": source,
            })
        else:
            manual.append({
                "id": f"{prefix}-{i:02d}", "statement": item, "source": source,
                "note": "too long to match literally - check this one by reading, not by grep",
            })


def build_contract(args: argparse.Namespace, cliches: dict[str, Any]) -> dict[str, Any]:
    # The floor is a floor. Allowing --min-instincts 0 would let the one stage
    # that makes the rest of the session possible be skipped with a flag.
    minimum = max(args.min_instincts, MIN_INSTINCTS)
    instincts = parse_lines(read_text_arg(args.instincts))
    if len(instincts) < minimum:
        raise EngineError(
            f"the instinct list has {len(instincts)} usable entries but {minimum} are required. "
            "Writing down what you would have said is what makes it unavailable; a short list means the "
            "familiar answers are still on the table.",
        )
    if text_units(args.skeleton.strip()) < MIN_SKELETON_UNITS:
        raise EngineError(
            "--skeleton must name the structure the instincts share, in a sentence "
            f"(at least {MIN_SKELETON_UNITS} units). The skeleton is the real target: without it you "
            "ban twelve phrasings and accept the thirteenth version of the same idea."
        )

    user_items = parse_lines(read_text_arg(args.user)) if args.user else []

    allow = set(csv_list(args.allow))
    known_ids = {p["id"] for p in cliches["phrases"]} | {
        e["id"] for e in deck_lint_entries(cliches) if e["group"] == "hollow-adjective"
    }
    unknown = allow - known_ids
    if unknown:
        raise EngineError(f"--allow references unknown cliche id(s): {', '.join(sorted(unknown))}")

    entries: list[dict[str, Any]] = [e for e in deck_lint_entries(cliches) if e["id"] not in allow]
    manual: list[dict[str, str]] = []
    classify(instincts, "instinct", "first-instinct", "model", entries, manual)
    classify(user_items, "user", "user-exclusion", "user", entries, manual)
    for i, item in enumerate(csv_list(args.extra), start=1):
        entries.append({
            "id": f"extra-{i:02d}", "phrase": item, "tier": "ban",
            "group": "user-specified", "source": "--extra",
        })

    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for e in entries:
        key = normalize(e["phrase"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(e)

    return {
        "engine_version": VERSION,
        "brief": args.brief,
        "skeleton": args.skeleton.strip(),
        "user_confirmed": bool(args.confirmed),
        "counts": {
            "model_instincts": len(instincts),
            "user_exclusions": len(user_items),
            "matchable": sum(1 for e in deduped if e["tier"] == "ban"),
            "warn": sum(1 for e in deduped if e["tier"] == "warn"),
            "manual": len(manual),
        },
        "model_instincts": instincts,
        "user_exclusions": user_items,
        "allowed": sorted(allow),
        "entries": deduped,
        "manual_checks": manual,
        "structural_patterns": cliches["structural_patterns"],
        "forbidden_moves": cliches["moves"],
    }


def render_human(payload: dict[str, Any]) -> str:
    c = payload["counts"]
    lines = [
        f"BAN CONTRACT for: {payload['brief']}",
        f"  skeleton: {payload['skeleton']}",
        f"  {c['model_instincts']} model instincts, {c['user_exclusions']} user exclusions, "
        f"{c['matchable']} matchable bans, {c['manual']} manual checks",
        f"  user confirmed: {'yes' if payload['user_confirmed'] else 'NO'}",
    ]
    if payload["allowed"]:
        lines.append(f"  released on request: {', '.join(payload['allowed'])}")
    if not payload["user_confirmed"]:
        lines.append("")
        lines.append("NEXT: show these to the user as exclusions - not as suggestions - ask what they would add,")
        lines.append("      then rerun with their additions in --user and with --confirmed. spec_gate.py fails")
        lines.append("      while user_confirmed is false, so an unsigned contract cannot reach a spec.")
    if payload["manual_checks"]:
        lines.append("")
        lines.append("MANUAL CHECKS (grep cannot help here - reread the spec against these):")
        for m in payload["manual_checks"]:
            lines.append(f"  - [{m['source']}] {m['statement']}")
    lines.append("")
    lines.append("FORBIDDEN MOVES:")
    for m in payload["forbidden_moves"]:
        lines.append(f"  - {m}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        cliches = load_deck("cliches")
        payload = build_contract(args, cliches)
    except EngineError as exc:
        message = str(exc)
        code = GATE_FAIL if ("instinct list" in message or "--skeleton" in message) else 1
        die(message, code)
        return code
    if args.out:
        out_path = Path(args.out) / "banlist.json"
        write_json(out_path, payload)
        if not args.json:
            print(f"wrote {out_path}")
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_human(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
