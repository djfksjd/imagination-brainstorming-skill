#!/usr/bin/env python3
"""cliche_lint.py - lint any draft against the ban contract mid-session.

spec_gate.py lints the finished spec. This is the same check pointed at
whatever you are writing right now: a message you are about to send, an
approach description, a draft section. Useful because a pitch reflex is much
cheaper to remove before the sentence is load-bearing.

It catches the mechanical half only. A draft can pass this and still be
ordinary; the lint proves that specific known-familiar moves are absent, never
that anything good is present.

Usage:
  cliche_lint.py --banlist ./work/banlist.json --draft ./work/draft.md
  cliche_lint.py --deck-only --draft -

Exit codes: 0 clean, 1 usage error, 3 banned material present.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from engine import (  # type: ignore
        VERSION, UsageParser, EngineError, csv_list, deck_lint_entries, die, extract_mentions,
        load_banlist, load_deck, lint_text, read_text_arg, strip_mention_markers,
    )
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from engine import (  # type: ignore
        VERSION, UsageParser, EngineError, csv_list, deck_lint_entries, die, extract_mentions,
        load_banlist, load_deck, lint_text, read_text_arg, strip_mention_markers,
    )

FAIL_CODE = 3


def build_parser() -> argparse.ArgumentParser:
    p = UsageParser(description="Lint a draft against the ban contract and the cliche deck.")
    p.add_argument("--draft", required=True, help="draft file, or '-' for stdin")
    p.add_argument("--banlist", default=None, help="banlist.json from banlist.py")
    p.add_argument("--deck-only", action="store_true", help="lint against deck defaults without a contract")
    p.add_argument("--allow", default=None,
                   help="entry ids to ignore for this run. This is a drafting aid: spec_gate.py has "
                        "no such flag, so anything released here still has to clear the real gate")
    p.add_argument("--strict", action="store_true", help="treat warnings as failures too")
    p.add_argument("--json", action="store_true", help="emit findings as JSON")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if not args.banlist and not args.deck_only:
            raise EngineError("pass --banlist, or --deck-only to lint against deck defaults")
        cliches = load_deck("cliches")
        patterns = cliches["structural_patterns"]
        manual: list[dict[str, Any]] = []
        if args.banlist:
            payload = load_banlist(args.banlist)
            entries = payload["entries"]
            patterns = payload.get("structural_patterns") or patterns
            manual = payload.get("manual_checks", [])
        else:
            entries = deck_lint_entries(cliches)
        draft = read_text_arg(args.draft)
        mentions = extract_mentions(draft)
        known = {str(e.get("id")) for e in entries} | {str(p.get("id")) for p in patterns}
        for body, ids in mentions:
            unknown = sorted(i for i in ids if i not in known)
            if not ids or unknown:
                raise EngineError(
                    f"a mention block names {'no rule id' if not ids else 'unknown rule id(s) ' + ', '.join(unknown)} "
                    f"({body.strip()[:60]}...). Mark the span with the id printed in square brackets by this lint"
                )
        findings = lint_text(strip_mention_markers(draft), entries, patterns,
                             set(csv_list(args.allow)), mentions)
    except EngineError as exc:
        die(str(exc), 1)
        return 1

    bans = [f for f in findings if f["tier"] == "ban"]
    warns = [f for f in findings if f["tier"] == "warn"]
    failed = bool(bans) or (args.strict and bool(warns))

    if args.json:
        print(json.dumps({
            "engine_version": VERSION,
            "failed": failed,
            "counts": {"ban": len(bans), "warn": len(warns), "manual": len(manual)},
            "findings": findings,
            "manual_checks": manual,
        }, ensure_ascii=False, indent=2))
    else:
        for f in bans:
            print(f"BAN   line {f['line']}: {f['match']!r} [{f['id']}] - {f['excerpt']}")
        for f in warns:
            print(f"WARN  line {f['line']}: {f['match']!r} [{f['id']}] - {f['excerpt']}")
        if manual:
            print("\nMANUAL CHECKS (not machine-checkable - reread the draft against these):")
            for m in manual:
                print(f"  - [{m.get('source', '?')}] {m.get('statement', '')}")
        print(f"\n{len(bans)} banned, {len(warns)} warnings, {len(manual)} manual checks.")
        if failed:
            print("FAILED: rewrite the flagged lines. Deleting the word is not a fix - "
                  "the thought underneath it has to change.")
        else:
            print("PASSED the mechanical check. This says nothing about whether the thinking is any good.")
    return FAIL_CODE if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
