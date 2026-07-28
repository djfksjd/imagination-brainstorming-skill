# Concept spec template

Write to `docs/concepts/YYYY-MM-DD-<topic>-concept.md` unless the project has
its own convention. Headings may be translated into the user's language; the
HTML section markers may not - `spec_gate.py` looks for them, and they are what
lets the gate tell a missing section from a differently-worded one.

Sections must appear **in this order** and each needs real content: the gate
checks both, because a document whose sections are markers with nothing under
them is not a spec.

Keep the machine-readable sidecar `concept.json` next to the working files. The
markdown is for people; the sidecar is what the gate reads and what lets a long
session survive a context reset. A complete pair of both files is shipped as
`example-concept.md` and `example-concept.json`.

---

```markdown
# <Concept name>

<!-- section: brief -->
## What was asked for

The request in the user's own words, then what the session established it
actually is. If those two differ, say so plainly - that difference is usually
the most valuable line in the document.

<!-- section: premises -->
## Premises

| Premise | Verdict | Why |
|---|---|---|
| The thing everyone assumed | deleted / inverted / kept | What testing it revealed |

At least one must be deleted or inverted. If only one falls, add a short note
saying why the others held - that is an honest result. If everything was kept,
the session refined the brief instead of testing it.

<!-- section: banlist -->
## What is off the table

The shared ban contract, confirmed with the user: the answers that came
cheapest, the skeleton they share, and the user's own exclusions. This section
is quoted material - it is the only section the gate does not lint.

The user's longer exclusions cannot be matched mechanically, so each one gets a
written answer in the sidecar's `banlist_contract.manual_checks_cleared`: one
line saying how the concept avoids it. The gate fails while any is unanswered.

<!-- section: approaches -->
## Approaches considered

Three, in comparable detail, each with its frame, its mechanism, and how it
would actually fail here. Mark which one sat in the unsafe seat and which was
chosen. A reader must be able to disagree with the choice on the evidence given.

<!-- section: concept -->
## The concept

The chosen direction: how it works, what it refuses to do and at what cost,
what it makes impossible that the ordinary version allows, and the boring half -
the recurring task, the sign-off, the queue, the reconciliation.

<!-- section: first-use -->
## First contact

One concrete scene: a person, a place, a time, what they see and do, where they
hesitate. Not a description of the concept - a moment of it happening.

<!-- section: neighbours -->
## Nearest existing things

What already exists near this, named, and how this differs. If nothing close was
found, say what was checked. Never claim nobody has thought of it.

<!-- section: open-questions -->
## Open questions

At least two, written so someone could actually answer them. Decoration does not
count: "how will users respond?" is not a question, "will the trust accept this
as the legal record without a countersignature?" is.

<!-- section: decisions -->
## Decision log

| Decision | Why | When |
|---|---|---|

Including the ones that closed off options. A reader six months from now needs
to know what was already ruled out and on what grounds.

<!-- section: handoff -->
## Handoff

What this spec does not cover, and what happens next: `writing-plans`,
`imagination-engine`, or stop.
```

## Bound assertions

Four kinds of statement are marked so the gate reads an assertion rather than
guessing from word overlap:

```markdown
**What it forbids:**

<!-- bind: chosen.forbids -->
The refusal, word for word as it appears in concept.json.
<!-- /bind -->
```

`chosen.forbids` and `chosen.impossible_now` belong in the concept section,
`first_use_scene` in the first-use section, and every `open_questions[i]` in the
open-questions section. Each appears exactly once, inside its own section, as
plain prose - not inside a blockquote, a code fence, or a struck-through line.
The comparison is exact after Unicode normalization and whitespace collapse, so
revising or translating the wording means updating `concept.json` to the
delivered wording before gating. See `references/example-concept.md`.

