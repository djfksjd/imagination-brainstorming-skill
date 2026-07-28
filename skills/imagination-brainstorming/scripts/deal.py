#!/usr/bin/env python3
"""deal.py - deal the session hand for one brainstorming session.

Two things a model does badly when left to itself: it asks premise-preserving
questions (who is the user, what are the constraints), and it proposes three
approaches that are variants of one idea. This script deals both from decks
instead: a set of question families that attack the brief's assumptions, and
three reframing lenses guaranteed to come from different categories, one of
which is marked as the seat for the approach the user will probably reject.

The deal is hash-seeded from the brief, so a session is reproducible, and
`--run 2` deals fresh lenses when a round of divergence has been exhausted.

Usage:
  deal.py --brief "a way for a team to hand over shifts" --out ./work
  deal.py --brief "..." --run 2 --questions 6 --json

Exit codes: 0 ok, 1 usage or deck error.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from engine import (  # type: ignore
        VERSION, UsageParser, EngineError, die, load_all_decks, round_robin, slice_by_run,
        stable_shuffle, write_json,
    )
except ImportError:  # executed from another cwd via absolute path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from engine import (  # type: ignore
        VERSION, UsageParser, EngineError, die, load_all_decks, round_robin, slice_by_run,
        stable_shuffle, write_json,
    )

DEFAULT_QUESTIONS = 5
DEFAULT_APPROACHES = 3


def build_parser() -> argparse.ArgumentParser:
    p = UsageParser(description="Deal the question families and reframing lenses for a session.")
    p.add_argument("--brief", help="the idea as the user stated it")
    p.add_argument("--run", type=int, default=1, help="round index; later rounds deal fresh lenses (default 1)")
    p.add_argument("--questions", type=int, default=DEFAULT_QUESTIONS, help=f"question families to deal (default {DEFAULT_QUESTIONS})")
    p.add_argument("--approaches", type=int, default=DEFAULT_APPROACHES,
                   help=f"reframing lenses to deal (default and minimum {DEFAULT_APPROACHES})")
    p.add_argument("--salt", default="", help="extra seed material; change it to redeal the same round")
    p.add_argument("--out", default=None, help="directory to write deal.json into")
    p.add_argument("--json", action="store_true", help="print the deal as JSON only")
    p.add_argument("--list-frames", action="store_true", help="list frame categories and exit")
    return p


def list_frames(decks: dict[str, Any]) -> None:
    frames = decks["frames"]
    by_cat: dict[str, list[dict[str, Any]]] = {}
    for f in frames["frames"]:
        by_cat.setdefault(f["category"], []).append(f)
    for cat in frames["categories"]:
        print(f"{cat['id']:<16} {cat['label']}")
        for f in by_cat.get(cat["id"], []):
            print(f"    {f['id']:<24} {f['label']}")


def deal_frames(decks: dict[str, Any], brief: str, salt: str, run: int, count: int) -> tuple[list[dict[str, Any]], bool]:
    deck = decks["frames"]
    categories = [c["id"] for c in deck["categories"]]
    if count > len(categories):
        raise EngineError(
            f"--approaches {count} exceeds the {len(categories)} frame categories; "
            "approaches drawn from one category are variants, not alternatives"
        )
    by_cat: dict[str, list[dict[str, Any]]] = {c: [] for c in categories}
    for f in deck["frames"]:
        if f["category"] not in by_cat:
            raise EngineError(f"frame {f['id']} has unknown category {f['category']}")
        by_cat[f["category"]].append(f)
    for cat in categories:
        if not by_cat[cat]:
            raise EngineError(f"frame category {cat} is empty")

    ordered_cats = stable_shuffle(categories, brief, salt, "categories")
    groups = [stable_shuffle(by_cat[c], brief, salt, "frame", c) for c in ordered_cats]
    return slice_by_run(round_robin(groups), run, count)


def build_deal(args: argparse.Namespace, decks: dict[str, Any]) -> dict[str, Any]:
    if args.run < 1:
        raise EngineError("--run must be 1 or greater")
    if args.approaches < DEFAULT_APPROACHES:
        raise EngineError(
            f"--approaches cannot be lower than {DEFAULT_APPROACHES}; with fewer, the divergence check has "
            "nothing to compare and every pairwise test passes vacuously"
        )
    if args.questions < 1:
        raise EngineError("--questions must be at least 1")

    families = decks["question-families"]["families"]
    if args.questions > len(families):
        raise EngineError(f"--questions {args.questions} exceeds the {len(families)} available families")
    ordered_families = stable_shuffle(families, args.brief, args.salt, "questions")
    picked_families, wrapped_q = slice_by_run(ordered_families, args.run, args.questions)

    frames, wrapped_f = deal_frames(decks, args.brief, args.salt, args.run, args.approaches)

    # The unsafe seat rotates with the run so that the same category does not
    # always carry the uncomfortable option.
    unsafe_index = (args.run - 1) % len(frames)
    approaches = []
    for i, frame in enumerate(frames):
        approaches.append({
            "slot": i + 1,
            "frame_id": frame["id"],
            "category": frame["category"],
            "label": frame["label"],
            "move": frame["move"],
            "must_contain": frame["must_contain"],
            "characteristic_failure": frame["characteristic_failure"],
            "unsafe_seat": i == unsafe_index,
        })

    payload: dict[str, Any] = {
        "engine_version": VERSION,
        "brief": args.brief,
        "run": args.run,
        "salt": args.salt,
        "question_families": [
            {
                "id": f["id"], "label": f["label"], "purpose": f["purpose"],
                "prompts": f["prompts"], "listens_for": f["listens_for"], "anti_pattern": f["anti_pattern"],
            }
            for f in picked_families
        ],
        "approaches": approaches,
        "rules": [
            "Ask one question per message, phrased for this brief in the user's language. Never paste a deck prompt verbatim.",
            "After roughly three questions, write the twelve most likely answers to this brief, name the skeleton they share, and put the compressed list to the user as a list of exclusions - not as suggestions.",
            "Each approach must occupy its dealt frame, contain what that frame requires, and state how it would actually fail here.",
            "Exactly one approach sits in the unsafe seat: the one the user will probably reject. Argue for it honestly; a strawman in this seat makes the other two decoys.",
            "Describe all approaches in comparable detail, then give your recommendation and the reason.",
            "The chosen concept must state what it forbids. A design that forbids nothing is a wish list.",
        ],
        "deck_wrapped": wrapped_q or wrapped_f,
        "notes": [],
    }
    if payload["deck_wrapped"]:
        payload["notes"].append(
            "A deck wrapped to material already used at this run depth. Change --salt for genuinely fresh cards."
        )
    if len({a["category"] for a in approaches}) != len(approaches):
        payload["notes"].append("Two approaches share a frame category; they will be variants rather than alternatives.")
    return payload


def render_human(payload: dict[str, Any]) -> str:
    lines = [
        f"IMAGINATION BRAINSTORMING - deal for: {payload['brief']}",
        f"round {payload['run']}",
        "",
        "QUESTION FAMILIES (one per message, phrased for this brief):",
    ]
    for f in payload["question_families"]:
        lines.append(f"  - [{f['id']}] {f['label']}")
        lines.append(f"      purpose:  {f['purpose']}")
        lines.append(f"      example:  {f['prompts'][0]}")
        lines.append(f"      listen:   {f['listens_for']}")
        lines.append(f"      avoid:    {f['anti_pattern']}")
    lines.append("")
    lines.append("APPROACH FRAMES (must come out mutually incompatible):")
    for a in payload["approaches"]:
        seat = "  <- unsafe seat" if a["unsafe_seat"] else ""
        lines.append(f"  {a['slot']}. [{a['category']}] {a['label']}{seat}")
        lines.append(f"      move:     {a['move']}")
        lines.append(f"      include:  {a['must_contain']}")
        lines.append(f"      watch:    {a['characteristic_failure']}")
    lines.append("")
    lines.append("RULES:")
    for rule in payload["rules"]:
        lines.append(f"  - {rule}")
    if payload["notes"]:
        lines.append("")
        for note in payload["notes"]:
            lines.append(f"  ! {note}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        decks = load_all_decks()
        if args.list_frames:
            list_frames(decks)
            return 0
        if not args.brief or not args.brief.strip():
            raise EngineError("--brief is required")
        payload = build_deal(args, decks)
    except EngineError as exc:
        die(str(exc), 1)
        return 1
    if args.out:
        out_path = Path(args.out) / "deal.json"
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
