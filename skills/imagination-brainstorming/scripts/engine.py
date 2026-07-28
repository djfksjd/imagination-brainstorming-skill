#!/usr/bin/env python3
"""Shared helpers for the imagination-brainstorming scripts.

Python 3 standard library only. Every choice made by these scripts is derived
from a hash of the caller's inputs, so a given (brief, salt, run) always deals
the same hand. A brainstorming session that cannot be replayed cannot be
audited, and "the model happened to suggest something else this time" is not a
defence when a session converges on the obvious.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

VERSION = "0.1.1"

SKILL_DIR = Path(__file__).resolve().parent.parent
DECK_DIR = SKILL_DIR / "references" / "decks"

DECK_NAMES = ("question-families", "frames", "cliches", "spec-schema")

# Words that carry no information in a comparison of two ideas. Removed before
# measuring overlap so that "the user" appearing in both does not make two
# genuinely different approaches look alike.
STOPWORDS = frozenset("""
a an the and or but if then than that this these those of to in on at by for with without from into over under
is are was were be been being it its it's as not no nor so such very more most much many few some any each
we you they he she i our your their his her them us me my mine ours yours theirs who whom whose which what
when where why how all both either neither can could may might must shall should will would do does did done
have has had having there here also just only own same too own again further once about against between during
""".split())


class EngineError(Exception):
    """Fatal, user-facing error. Callers exit non-zero with the message."""


def die(message: str, code: int = 1) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


class UsageParser(argparse.ArgumentParser):
    """argparse exits 2 on a usage error, which is this package's "gate failed"
    code. A mistyped flag must not be readable as a failed gate, so usage errors
    exit 1 like every other caller mistake."""

    def error(self, message: str):  # pragma: no cover - argparse internals
        self.print_usage(sys.stderr)
        die(f"{self.prog}: {message}", 1)


def load_deck(name: str, deck_dir: Path | None = None) -> dict[str, Any]:
    if name not in DECK_NAMES:
        raise EngineError(f"unknown deck '{name}' (known: {', '.join(DECK_NAMES)})")
    path = (deck_dir or DECK_DIR) / f"{name}.json"
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise EngineError(f"cannot read deck {path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise EngineError(f"deck {path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict) or data.get("deck") != name:
        raise EngineError(f"deck {path} is missing or has a mismatched 'deck' field")
    return data


def load_all_decks(deck_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    return {name: load_deck(name, deck_dir) for name in DECK_NAMES}


def normalize(text: str) -> str:
    """Lowercase, NFKC-fold, collapse whitespace and dash/quote variants, and
    drop invisible formatting characters.

    Zero-width joiners between every letter render identically and used to make
    a sentence tokenize to nothing, which defeated every similarity check in
    this package - a banned skeleton could be reproduced verbatim and score
    zero overlap.
    """
    text = unicodedata.normalize("NFKC", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) not in {"Cf", "Cc"} or ch in "\n\t")
    for src, dst in (("‐", "-"), ("‑", "-"), ("–", "-"), ("—", "-"),
                     ("‘", "'"), ("’", "'")):
        text = text.replace(src, dst)
    text = text.lower()
    return re.sub(r"\s+", " ", text).strip()


def seed_int(*parts: Any) -> int:
    joined = "\x1f".join(normalize(str(p)) for p in parts)
    digest = hashlib.blake2b(joined.encode("utf-8"), digest_size=16).digest()
    return int.from_bytes(digest, "big")


def rng_for(*parts: Any) -> random.Random:
    return random.Random(seed_int(*parts))


def stable_shuffle(items: list[Any], *seed_parts: Any) -> list[Any]:
    out = list(items)
    rng_for(*seed_parts).shuffle(out)
    return out


def round_robin(groups: list[list[Any]]) -> list[Any]:
    """Interleave groups so that any k consecutive items come from k distinct
    groups whenever k <= len(groups). This is what lets a later run draw fresh
    material that is still guaranteed to be mutually distant."""
    out: list[Any] = []
    if not groups:
        return out
    depth = max(len(g) for g in groups)
    for i in range(depth):
        for g in groups:
            if i < len(g):
                out.append(g[i])
    return out


def slice_by_run(ordered: list[Any], run: int, count: int) -> tuple[list[Any], bool]:
    """Take `count` items starting at (run-1)*count, wrapping if the deck runs
    out. Returns (items, wrapped)."""
    if count <= 0:
        raise EngineError("count must be positive")
    if not ordered:
        raise EngineError("empty deck")
    start = (run - 1) * count
    wrapped = start + count > len(ordered)
    return [ordered[(start + i) % len(ordered)] for i in range(count)], wrapped


CJK_RANGES = (
    (0x1100, 0x11FF), (0x3040, 0x30FF), (0x3130, 0x318F), (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF), (0xA960, 0xA97F), (0xAC00, 0xD7FF), (0xF900, 0xFAFF),
)


def is_cjk(ch: str) -> bool:
    code = ord(ch)
    return any(lo <= code <= hi for lo, hi in CJK_RANGES)


def has_cjk(text: str) -> bool:
    return any(is_cjk(ch) for ch in text)


def content_tokens(text: str) -> set[str]:
    """Meaningful units of a text, for overlap comparison.

    Latin-script words are taken whole. Scripts that do not put spaces between
    words - Chinese, Japanese, Korean - would otherwise tokenize into one giant
    token per clause and compare as completely different, so those runs are cut
    into character bigrams as well. Without this, two identical Korean
    paragraphs score zero overlap, which is the opposite of the truth.
    """
    tokens: set[str] = set()
    for word in re.findall(r"[\w']+", normalize(text), flags=re.UNICODE):
        if has_cjk(word):
            run = "".join(ch for ch in word if not ch.isspace())
            tokens.update(run[i:i + 2] for i in range(max(len(run) - 1, 1)))
            if len(run) == 1:
                tokens.add(run)
        elif len(word) > 2 and word not in STOPWORDS:
            tokens.add(word)
    return tokens


def jaccard(a: str, b: str) -> float:
    """Overlap of two texts in [0, 1]. Used to catch two 'different' texts that
    are the same idea in different words. Crude on purpose: it is a floor
    check, not a semantic judgement, and it never decides on its own that
    something is fine - only that it is too similar to pass. Identical strings
    always score 1.0, whatever the script."""
    na, nb = normalize(a), normalize(b)
    if na and na == nb:
        return 1.0
    ta, tb = content_tokens(a), content_tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def coverage(needle: str, haystack: str) -> float:
    """How much of `needle` reappears in `haystack`, in [0, 1].

    Jaccard is the wrong tool for asking "did the concept restate the banned
    skeleton": a short skeleton buried in a long passage scores low on overlap
    while being reproduced word for word. Containment answers the question that
    is actually being asked.
    """
    tn, th = content_tokens(needle), content_tokens(haystack)
    if not tn or not th:
        return 0.0
    return len(tn & th) / len(tn)


def distinct_ratio(text: str) -> float:
    """Share of distinct tokens in a text. Padding a field to its character
    minimum with a repeated word or a run of the same letter scores near zero;
    ordinary prose scores well above 0.3."""
    tokens = [w for w in re.findall(r"[\w']+", normalize(text), flags=re.UNICODE)]
    if not tokens:
        return 0.0
    if len(tokens) == 1:
        # One long token: measure repetition at character level, because
        # "abcabcabc..." has three distinct characters and is still padding.
        word = tokens[0]
        if len(word) < 4:
            return 1.0
        bigrams = [word[i:i + 2] for i in range(len(word) - 1)]
        return len(set(bigrams)) / len(bigrams)
    ratio = len(set(tokens)) / len(tokens)
    # A repeated multi-word phrase scores well on token variety; compare the
    # first half of the text with the second to catch it.
    if len(tokens) >= 8:
        half = len(tokens) // 2
        if normalize(" ".join(tokens[:half])) == normalize(" ".join(tokens[half:half * 2])):
            return 0.0
    return ratio


def require_mapping(value: Any, label: str, keys: tuple[str, ...] = ()) -> dict[str, Any]:
    """Validate the *shape* of parsed JSON, not just that it parsed. A list or a
    stripped-down object supplied where a document is expected must be a
    controlled error, never a traceback and never a silently disabled check."""
    if not isinstance(value, dict):
        raise EngineError(f"{label} must be a JSON object, got {type(value).__name__}")
    missing = [k for k in keys if k not in value]
    if missing:
        raise EngineError(f"{label} is missing required key(s): {', '.join(missing)}")
    return value


def read_text_arg(value: str) -> str:
    """Read a file path, or stdin when the value is '-'."""
    if value == "-":
        return sys.stdin.read()
    try:
        return Path(value).read_text(encoding="utf-8")
    except OSError as exc:
        raise EngineError(f"cannot read {value}: {exc}") from exc


def read_json_arg(value: str) -> Any:
    raw = read_text_arg(value)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise EngineError(f"{value} is not valid JSON: {exc}") from exc


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def csv_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def phrase_regex(phrase: str) -> re.Pattern[str]:
    """Match a phrase tolerantly: spaces and hyphens interchange, an optional
    plural suffix is allowed on the final Latin word, and Latin matches fall on
    word boundaries so that 'badge' does not fire inside 'badgering'.

    Agglutinative scripts get no trailing boundary: Korean attaches particles
    directly to the noun, so requiring one would mean a ban on 대시보드 never
    fires on 대시보드는 - the ban list would be decorative for most of the
    languages this skill claims to work in.
    """
    words = [w for w in re.split(r"[\s\-_]+", normalize(phrase)) if w]
    if not words:
        raise EngineError(f"empty phrase: {phrase!r}")
    escaped = [re.escape(w) for w in words]
    if not has_cjk(words[-1]):
        escaped[-1] = escaped[-1] + r"(?:e?s)?"
    body = r"[\s\-_]*".join(escaped) if has_cjk(phrase) else r"[\s\-_]+".join(escaped)
    lead = "" if has_cjk(words[0]) else r"(?<![\w])"
    trail = "" if has_cjk(words[-1]) else r"(?![\w])"
    return re.compile(rf"{lead}{body}{trail}", re.IGNORECASE)


def load_banlist(path: str) -> dict[str, Any]:
    """Read and validate a ban contract.

    An empty or wrongly-shaped file must be an error, never a lint that
    silently passes everything: `--banlist {}` used to disable the check while
    still looking like it ran.
    """
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EngineError(f"cannot read ban list {path}: {exc}") from exc
    payload = require_mapping(payload, f"ban list {path}", ("entries",))
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise EngineError(f"ban list {path} has no entries - build it with banlist.py")
    for i, e in enumerate(entries):
        if not isinstance(e, dict):
            raise EngineError(f"ban list {path}: entry {i} is not an object")
        if not isinstance(e.get("id"), str) or not e["id"].strip():
            raise EngineError(f"ban list {path}: entry {i} has no id")
        if not isinstance(e.get("phrase"), str) or not e["phrase"].strip():
            raise EngineError(f"ban list {path}: entry {i} has no phrase")
        if e.get("tier") not in {"ban", "warn", "manual"}:
            raise EngineError(f"ban list {path}: entry {i} has tier {e.get('tier')!r}")
    patterns = payload.get("structural_patterns", [])
    if not isinstance(patterns, list):
        raise EngineError(f"ban list {path}: structural_patterns must be a list")
    for i, pattern in enumerate(patterns):
        if not isinstance(pattern, dict) or not isinstance(pattern.get("id"), str):
            raise EngineError(f"ban list {path}: structural_patterns[{i}] has no id")
        if not isinstance(pattern.get("regex"), str):
            raise EngineError(f"ban list {path}: structural_patterns[{i}] has no regex")
    manual = payload.get("manual_checks", [])
    if not isinstance(manual, list):
        raise EngineError(f"ban list {path}: manual_checks must be a list")
    for i, m in enumerate(manual):
        if not isinstance(m, dict) or not isinstance(m.get("id"), str) or not m["id"].strip():
            raise EngineError(f"ban list {path}: manual_checks[{i}] has no id")
        if not isinstance(m.get("statement"), str) or not m["statement"].strip():
            raise EngineError(f"ban list {path}: manual_checks[{i}] has no statement")
    return payload


def deck_lint_entries(cliches: dict[str, Any]) -> list[dict[str, Any]]:
    entries = [
        {"id": p["id"], "phrase": p["phrase"], "tier": p["tier"], "group": p["group"], "source": "deck"}
        for p in cliches["phrases"]
    ]
    for tier in ("ban", "warn"):
        for word in cliches["hollow_adjectives"][tier]:
            entries.append({
                "id": f"hollow-{normalize(word).replace(' ', '-')}",
                "phrase": word,
                "tier": tier,
                "group": "hollow-adjective",
                "source": "deck",
            })
    return entries


def lint_text(text: str, entries: list[dict[str, Any]], patterns: list[dict[str, Any]],
              allow: set[str] | None = None) -> list[dict[str, Any]]:
    """Find banned phrases and pitch-shaped sentences, with line numbers."""
    allow = allow or set()
    findings: list[dict[str, Any]] = []
    compiled = []
    for e in entries:
        if e["id"] in allow or e.get("tier") == "manual":
            continue
        try:
            compiled.append((e, phrase_regex(e["phrase"])))
        except EngineError:
            continue
    compiled_patterns = []
    for p in patterns:
        if p["id"] in allow:
            continue
        try:
            compiled_patterns.append((p, re.compile(p["regex"], re.IGNORECASE)))
        except re.error as exc:
            raise EngineError(f"pattern {p['id']} is not a valid regex: {exc}") from exc

    for lineno, line in enumerate(text.splitlines(), start=1):
        norm = normalize(line)
        if not norm:
            continue
        for e, rx in compiled:
            m = rx.search(norm)
            if m:
                findings.append({
                    "id": e["id"], "kind": "phrase", "tier": e["tier"],
                    "group": e.get("group", ""), "source": e.get("source", ""),
                    "line": lineno, "match": m.group(0), "excerpt": line.strip()[:160],
                })
        for p, rx in compiled_patterns:
            m = rx.search(line)
            if m:
                findings.append({
                    "id": p["id"], "kind": "pattern", "tier": p["tier"],
                    "group": "structural", "source": "deck",
                    "line": lineno, "match": m.group(0), "excerpt": line.strip()[:160],
                    "why": p.get("why", ""),
                })
    return findings
