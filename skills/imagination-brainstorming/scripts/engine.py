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

VERSION = "0.3.0"

SKILL_DIR = Path(__file__).resolve().parent.parent
DECK_DIR = SKILL_DIR / "references" / "decks"

DECK_NAMES = ("question-families", "frames", "cliches", "spec-schema", "approaches-schema")

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



PLACEHOLDER_NAMES = {
    "tbd", "todo", "tba", "n/a", "na", "none", "null", "untitled", "unnamed",
    "placeholder", "name", "?", "??", "???", "xxx", "test", "foo", "bar",
}


MAX_MARKS_PER_BASE = 2


def text_units(text: str) -> int:
    """Length in units rather than code points.

    Every minimum in this skill is asking for an amount of *argument*, not an
    amount of Unicode. Three rules, each of which was a defect first, and each
    of which is now stated identically in the sibling skill so the two
    measurements cannot drift apart again.

    A wide letter or digit counts as two units. Counting code points makes a
    Korean, Japanese or Chinese section roughly twice as hard to satisfy as an
    English one carrying the same content, because one Han character or Hangul
    syllable does the work of about two Latin letters. Only letters and digits
    are widened; wide punctuation, box drawing and emoji stay at one.
    Compatibility-normalizing first stops fullwidth Latin inflating the count.

    Punctuation and whitespace never count. They used to count one unit per
    run, which was enough to make `'Nurse' + 120 x (dot + two accents) +
    'waits'` measure 251 units against a 250-unit floor: the run rule reset the
    mark cap on every dot, so each dot bought two more marks. Nothing that is
    not a letter, a digit or a mark on one pays anything now.

    Combining marks count, up to two per base letter or digit, and the cap is
    *not* reset by punctuation or whitespace. Stripping marks entirely was
    right for stray zero-width joiners and wrong for every script that writes
    its vowels and tones as marks: 282 characters of Thai prose measured 209
    units and were refused. Two per base is what ordinary Thai, Devanagari,
    Arabic and Hebrew orthography uses; past that the marks are decoration
    stacked on one letter, and they stop paying. A mark that follows no base at
    all pays nothing.

    This narrows padding rather than eliminating it. An author willing to type
    a hundred distinct words still clears a hundred units with a hundred words
    of nothing; that is what `distinct_ratio` and a human reader are for.
    """
    if not isinstance(text, str):
        return 0
    total = 0
    # Starts at the cap: a mark before any base character has nothing to
    # attach to, so it buys nothing.
    marks_on_base = MAX_MARKS_PER_BASE
    for ch in unicodedata.normalize("NFKC", text):
        category = unicodedata.category(ch)
        if category in ("Cc", "Cf"):
            continue
        if category in ("Mn", "Me", "Mc"):
            if marks_on_base < MAX_MARKS_PER_BASE:
                marks_on_base += 1
                total += 1
            continue
        if category[0] in ("L", "N"):
            marks_on_base = 0
            total += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
        # Punctuation and whitespace: no unit, and deliberately no reset of the
        # mark cap. Resetting here is exactly what reopened the padding hole.
    return total


def is_placeholder(text: str) -> bool:
    """Whether a name is a stand-in rather than a name.

    A length floor cannot answer this: it rejects a complete two-character name
    and accepts 'TBD - fill this in later'. So the check asks what it actually
    wants to know - is there a name here at all.
    """
    stripped = normalize(text).strip(" .-_·")
    if not stripped:
        return True
    if not any(unicodedata.category(ch)[0] in ("L", "N") for ch in stripped):
        return True
    return stripped in PLACEHOLDER_NAMES


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


def word_tokens(text: str) -> list[str]:
    """Words, where a combining mark belongs to the word it sits on.

    `\\w` does not match a combining mark, so every niqqud, harakat, matra or
    Thai vowel sign split its word into single consonants: vocalized Hebrew
    tokenized into twenty one-letter tokens and scored 0.30 on `distinct_ratio`
    - repeated filler, said the gate, about ordinary prose. The scripts whose
    orthography `text_units` was fixed for were still being measured as if the
    marks were punctuation.
    """
    tokens: list[str] = []
    current: list[str] = []
    for ch in normalize(text):
        if ch.isalnum() or ch == "'" or unicodedata.category(ch)[0] == "M":
            current.append(ch)
        elif current:
            tokens.append("".join(current))
            current = []
    if current:
        tokens.append("".join(current))
    return tokens


def content_tokens(text: str) -> set[str]:
    """Meaningful units of a text, for overlap comparison.

    Latin-script words are taken whole. Scripts that do not put spaces between
    words - Chinese, Japanese, Korean - would otherwise tokenize into one giant
    token per clause and compare as completely different, so those runs are cut
    into character bigrams as well. Without this, two identical Korean
    paragraphs score zero overlap, which is the opposite of the truth.
    """
    tokens: set[str] = set()
    for word in word_tokens(text):
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


def passage_coverage(needle: str, haystack: str, window: int = 24, step: int = 12) -> float:
    """How much of `needle` appears in `haystack` as contiguous passages.

    No longer used by a gate. It was the second attempt at binding the written
    spec to its sidecar - better than token overlap, which passed a section that
    had been replaced wholesale - but still a similarity score, and a similarity
    score cannot tell a proposition being asserted from the same words quoted
    inside a sentence that rejects them. Marked assertions replaced it. Kept
    because it is a reasonable "is this passage actually in there" measure for
    drafting, and because the tests that pin its two known holes are worth
    keeping.

    Token containment is not enough to ask "does this document contain this
    passage": in a long, thorough spec the words of any one paragraph are
    scattered through the others, so a bag-of-tokens score passes even when the
    paragraph was replaced wholesale. Overlapping character windows ask the
    question that was meant - is this text actually in there - and work the same
    way in every script.
    """
    a, b = normalize(needle), normalize(haystack)
    if not a or not b:
        return 0.0
    if len(a) <= window:
        return 1.0 if a in b else 0.0
    windows = [a[i:i + window] for i in range(0, len(a) - window + 1, step)]
    # The stepped range stops early whenever the length is not a multiple of the
    # step, leaving up to window-1 characters at the end unchecked. That tail is
    # where a sentence puts its conclusion and its negation, so it is exactly
    # the span an author could reverse while still scoring 1.0.
    tail = a[-window:]
    if tail != windows[-1]:
        windows.append(tail)
    return sum(1 for w in windows if w in b) / len(windows)


def distinct_ratio(text: str) -> float:
    """Share of distinct tokens in a text. Padding a field to its character
    minimum with a repeated word or a run of the same letter scores near zero;
    ordinary prose scores well above 0.3."""
    tokens = word_tokens(text)
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

    Agglutinative scripts get no trailing boundary. Korean attaches its
    particles directly to the noun with no space and no punctuation between
    them: the noun romanized as "daesibodeu" (dashboard) appears in a sentence
    as "daesibodeu-neun", "daesibodeu-reul", "daesibodeu-eseo", one written
    word each time. Requiring a word boundary after the phrase would mean a ban
    on the noun never fires on any of its inflected forms, which is most of its
    occurrences - the ban list would be decorative for most of the languages
    this skill claims to work in. Han and kana run together the same way.
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


MENTION = re.compile(r"<!--\s*mention:\s*([^<>]*?)\s*-->(.*?)<!--\s*/mention\s*-->", re.S)
MENTION_MARKER = re.compile(r"<!--\s*/?mention(?::[^<>]*?)?\s*-->")


def extract_mentions(text: str) -> list[tuple[str, set[str]]]:
    """The spans marked as mentioning a banned phrase rather than using it.

    `<!-- mention: hollow-magical -->The region is not magical<!-- /mention -->`
    releases `hollow-magical` inside that span and nowhere else.
    """
    out: list[tuple[str, set[str]]] = []
    for match in MENTION.finditer(text):
        ids = {i.strip() for i in match.group(1).replace(";", ",").split(",") if i.strip()}
        body = match.group(2)
        if body.strip():
            out.append((body, ids))
    return out


# A marked span is an unverifiable claim by the party being judged, so what it
# can reach is bounded here rather than left to the author's restraint. One
# marker naming every id and wrapping the whole document released all 55 rules
# of a shipped contract, including the twelve burnt instincts and the user's own
# exclusions, and exited 0.
MENTION_MAX_IDS = 1
MENTION_MAX_UNITS = 200
MENTION_MAX_MARKERS = 5

# Evidence that the span denies or quotes the word rather than using it. This is
# a narrowing, not a proof: a regex cannot tell an assertion from a quotation,
# which is why the marker exists at all. The cue list covers the eight languages
# this repository ships documentation in and the double-quotation marks in
# common use; in any other language, quote the phrase. The plain apostrophe is
# deliberately not a cue - "don't" is not a quotation.
NEGATION_CUE = re.compile(
    r"\b(?:not|no|never|nor|without|neither|cannot|rather\s+than|instead\s+of"
    r"|nicht|kein\w*|nie|niemals|ohne"
    r"|ni|sin|nunca|tampoco"
    r"|ne|pas|aucun\w*|jamais|sans"
    r"|nao|nem|sem)\b"
    r"|(?:is|are|does|do|did|was|were|ca|wo|could|should|would)n['’]t\b"
    r"|n[aã]o"
    r"|[\"“”„‟«»‹›「」『』`]"
    r"|아니|않|없|말고"
    r"|ない|ません|なく|ではな|じゃな"
    r"|不|沒|没|無|无|非",
    re.IGNORECASE,
)


def mention_bound_failures(mentions: list[tuple[str, set[str]]], known_ids: set[str]) -> list[str]:
    """What a mention marker may not do, checked before any release is honoured.

    Each bound closes a way one marker becomes a general release:

    * one id per marker - a list of ids in one marker is a release of the whole
      contract wearing the syntax of a single quotation;
    * a span of at most `MENTION_MAX_UNITS` units and no blank line - a marker
      that wraps the whole document releases everything the document says;
    * a cue that the span denies or quotes - a span that negates nothing is a
      use of the word, whatever the marker asserts;
    * at most `MENTION_MAX_MARKERS` markers in one document - the bounds above
      are per span, and enough spans reassemble the general release; a spec that
      needs to quote more banned words than that has the wrong ban list;
    * an id no marker may name at all, checked by the caller against
      `releasable_ids()` - the instincts and the user's exclusions.

    None of this checks the author's claim. It bounds what the claim can reach.
    """
    failures: list[str] = []
    if len(mentions) > MENTION_MAX_MARKERS:
        failures.append(
            f"{len(mentions)} mention markers, at most {MENTION_MAX_MARKERS} are allowed - each one is a "
            "release the gate cannot verify, and enough of them are a release of the whole contract"
        )
    releasable = releasable_ids()
    for body, ids in mentions:
        excerpt = body.strip()[:60]
        if len(ids) > MENTION_MAX_IDS:
            failures.append(
                f"a mention block names {len(ids)} rule ids ({', '.join(sorted(ids)[:4])}...) - one marker "
                f"releases one id, so mark each quoted phrase in its own span ({excerpt}...)"
            )
        blocked = sorted(i for i in ids if i in known_ids and i not in releasable)
        if blocked:
            failures.append(
                f"a mention block names {', '.join(blocked)}, which nothing the spec says can release - a "
                "first instinct and one of the user's own exclusions are exempted by the user, not by the "
                f"document under judgement ({excerpt}...)"
            )
        units = text_units(body)
        if units > MENTION_MAX_UNITS:
            failures.append(
                f"a mention span is {units} units long, the limit is {MENTION_MAX_UNITS} - mark the phrase "
                f"being quoted, not the passage around it ({excerpt}...)"
            )
        if re.search(r"\n[ \t]*\n", body):
            failures.append(
                f"a mention span crosses a blank line - one span is one paragraph, so that a marker cannot "
                f"be opened at the top of a document and closed at the bottom ({excerpt}...)"
            )
        if not NEGATION_CUE.search(body):
            failures.append(
                f"a mention span contains no denial or quotation ({excerpt}...) - the marker claims the word "
                "is mentioned rather than used, so the span has to show that: deny it, or put it in double "
                "quotation marks"
            )
    return failures


_RELEASABLE: frozenset[str] | None = None


def releasable_ids() -> frozenset[str]:
    """The only ids any release may name: the bundled deck's, and nothing else.

    Deliberately not a parameter. Every release route so far - the ban list's
    `allowed` field, and then mention markers - was a way for the artefact under
    judgement to name what it wanted exempted, and each was closed one at a time
    after it shipped. What the artefact contributes to the lint (the session's
    instincts, the user's exclusions, `--extra` phrases) is therefore not
    releasable by anything the artefact says, and no caller can widen this set,
    because there is nothing to pass. Changing a bundled cliche means changing
    the deck in the repository, where the change is reviewed outside the session
    that wants it.
    """
    global _RELEASABLE
    if _RELEASABLE is None:
        deck = load_deck("cliches")
        _RELEASABLE = frozenset(
            {e["id"] for e in deck_lint_entries(deck)}
            | {str(p.get("id")) for p in deck.get("structural_patterns", [])}
        )
    return _RELEASABLE


def strip_mention_markers(text: str) -> str:
    """Remove the marker comments, keep what they wrap.

    The marker names a ban id, and several ids contain the banned word - the
    comment `<!-- mention: hollow-magical -->` would otherwise be flagged for
    saying 'magical'.
    """
    return MENTION_MARKER.sub("", text)


def _released_spans(line: str, mentions: list[tuple[str, set[str]]], norm: bool) -> list[tuple[int, int, set[str]]]:
    """Where in this line a mention span sits, and which ids it releases.

    Matched line by line, so a span covering several lines releases each of its
    lines separately and a marker never has to sit on the line it opens.
    """
    hay = normalize(line) if norm else line
    spans: list[tuple[int, int, set[str]]] = []
    if not hay:
        return spans
    for body, ids in mentions:
        for piece in body.splitlines():
            needle = normalize(piece) if norm else piece.strip()
            if len(needle) < 3:
                continue
            start = 0
            while True:
                found = hay.find(needle, start)
                if found < 0:
                    break
                spans.append((found, found + len(needle), ids))
                start = found + 1
    return spans


def _is_released(spans: list[tuple[int, int, set[str]]], start: int, end: int, rule_id: str) -> bool:
    return any(s <= start and end <= t and rule_id in ids for s, t, ids in spans)


def lint_text(text: str, entries: list[dict[str, Any]], patterns: list[dict[str, Any]],
              allow: set[str] | None = None,
              mentions: list[tuple[str, set[str]]] | None = None) -> list[dict[str, Any]]:
    """Find banned phrases and pitch-shaped sentences, with line numbers.

    `mentions` releases named ids inside named spans only. A regex cannot tell
    a word being used from the same word being quoted or denied - "the region
    is not magical" was refused for saying so - and this is the same blindness
    a similarity score had when it could not separate an assertion from a
    quotation, which is why bind markers replaced it here. The fix is the same
    shape: the author marks the span, names the id, and the mark is visible in
    the source and reported at the gate. What it does not do is decide anything
    for itself. It cannot verify that the word really is mentioned rather than
    used; it makes the claim explicit, local to one span, and reviewable,
    instead of leaving the only escape a blanket release of the whole rule.
    """
    # One place where every release, present or future, is narrowed to the
    # bundled deck. `allow` and `mentions` are the two routes that exist today
    # and each of them was a general release before it was bounded; a third
    # route added later arrives here too, and cannot exempt a burnt instinct or
    # one of the user's exclusions without editing this function.
    releasable = releasable_ids()
    allow = {i for i in (allow or set()) if i in releasable}
    mentions = [(body, ids & releasable) for body, ids in (mentions or [])]
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
        norm_spans = _released_spans(line, mentions, norm=True)
        raw_spans = _released_spans(line, mentions, norm=False)
        for e, rx in compiled:
            for m in rx.finditer(norm):
                if _is_released(norm_spans, m.start(), m.end(), e["id"]):
                    continue
                findings.append({
                    "id": e["id"], "kind": "phrase", "tier": e["tier"],
                    "group": e.get("group", ""), "source": e.get("source", ""),
                    "line": lineno, "match": m.group(0), "excerpt": line.strip()[:160],
                })
                break
        for p, rx in compiled_patterns:
            for m in rx.finditer(line):
                if _is_released(raw_spans, m.start(), m.end(), p["id"]):
                    continue
                findings.append({
                    "id": p["id"], "kind": "pattern", "tier": p["tier"],
                    "group": "structural", "source": "deck",
                    "line": lineno, "match": m.group(0), "excerpt": line.strip()[:160],
                    "why": p.get("why", ""),
                })
                break
    return findings
