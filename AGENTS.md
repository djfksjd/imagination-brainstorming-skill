# AGENTS.md — imagination-brainstorming

> Shared agent guide, loaded as context by Claude Code and Codex.

## Role

This plugin ships one skill: a collaborative idea-development pipeline that
refuses to converge on the obvious. The authoritative document is
`skills/imagination-brainstorming/SKILL.md` — process, hard gates, hard rules
and the spec contract all live there. Follow it when the user wants to think an
idea through before building it, or says their options feel generic, safe, or
interchangeable.

Do **not** route implementation planning, factual questions, naming, or copy
work here. And when the conventional answer is the correct answer for a brief,
the skill's own rule is to say so in one sentence and do the ordinary work
rather than manufacture strangeness.

## Two hard gates

1. **No implementation.** No code, no scaffolding, no implementation skill. The
   terminal state is a gated, user-approved concept spec plus a handoff.
2. **No unguarded output.** Approaches are not shown until
   `divergence_check.py` exits 0; the spec is not put up for review until
   `spec_gate.py` exits 0. `spec_gate.py` requires the sidecar, the written
   markdown and the ban contract together, and checks that the three agree with
   each other — the contract must be confirmed and must record the sidecar's
   skeleton, brief and instincts, and the document must assert the concept it
   specifies. That is consistency between three files one author writes; it is
   not proof that they came from one session, which nothing here establishes.

The one exit from gate 1 is the fit check: if the conventional answer is
correct for this brief, say so, leave the skill, and do the ordinary work
outside it.

## Dependencies

Python 3 standard library only. No installation, no API keys, no network access.

## Script paths

Scripts live in `skills/imagination-brainstorming/scripts/`.

- Claude Code → `${CLAUDE_PLUGIN_ROOT}/skills/imagination-brainstorming/scripts/`
- Codex → substitute Codex's plugin root. If the variable is unknown, resolve
  the directory containing `SKILL.md` and use absolute paths. For a standalone
  clone that is `<clone>/skills/imagination-brainstorming/scripts/`.
- Each script resolves its decks from its own parent directory
  (`references/decks/`), so it can be invoked from any working directory.
- Write working files (`deal.json`, `banlist.json`, `concept.json`, drafts) into
  a scratch directory. Never into the skill folder. The written spec belongs in
  the user's project, at `docs/concepts/` unless the project says otherwise.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | ok |
| 1 | usage, deck, or malformed-input error (including argument mistakes) |
| 2 | gate failed — `banlist.py` (too few instincts, or no skeleton) or `spec_gate.py` (spec) |
| 3 | `divergence_check.py` (approaches are variants) or `cliche_lint.py` (banned material) |

A non-zero exit is never treated as success, and a failed gate means rework,
never resubmission with the numbers rounded.

## Conduct (summary — full text in SKILL.md)

- One question per message, phrased for this brief, in the user's language.
  Never paste a deck prompt verbatim.
- The ban contract is shown to the user **as exclusions, not as suggestions**.
  Presented any other way it anchors them to the most obvious ideas available.
  `--confirmed` records consent that already happened; never set it before the
  user has seen the list.
- Their long exclusions get a written answer each in
  `banlist_contract.manual_checks_cleared`; nothing else enforces them.
- Exactly one approach sits in the unsafe seat and is argued at full strength. A
  strawman there turns the other two into decoys.
- Every concept states what it forbids. A design that rules nothing out is a
  wish list.
- At least two open questions, real ones. A spec with none has hidden its
  unknowns.
- Never claim nobody has thought of this. Name the nearest existing things and
  state the difference.
- When a second reader is available, have them attack the concept before the
  user reviews it. The gates cannot catch an inverted justification or a
  mechanism that is attackable on its own terms; an adversarial read can.
- Do not soften the user's request to make it easier to spec.
