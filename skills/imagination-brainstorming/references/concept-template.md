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

Your own long instincts land in the same list - which of them do depends on the
subject, since a product instinct is a short noun phrase and a story or ritual
instinct is a clause. Those are a reread, not a written answer: the gate names
them in a warning and does not fail on them.

<!-- section: approaches -->
## Approaches considered

Three, in comparable detail, each with its frame, its mechanism, and how it
would actually fail here. Mark which one sat in the unsafe seat and which was
chosen. A reader must be able to disagree with the choice on the evidence given.

<!-- section: concept -->
## The concept

The chosen direction: how it works, the boring half - the recurring task, the
sign-off, the queue, the reconciliation - and the two assertions below, each
inside its own `<!-- bind: field --> ... <!-- /bind -->` block, word for word
as they appear in `concept.json`. Both are required; the gate fails if either
block is missing, even if the surrounding prose says the same thing.

**What it forbids:**

<!-- bind: chosen.forbids -->
What this design rules out on purpose, and the cost of that refusal.
<!-- /bind -->

**How it survives its own failure mode:** the approach you chose stated how it
fails in this brief. Say what the design does about that, in
`chosen.answers_failure_mode` and here. The gate refuses a spec that never
wrote one and refuses an answer that is the failure restated; it cannot judge
whether the failure is fatal or whether your answer works, so it prints the
declared failure next to your answer for whoever reads the verdict.

**What is now impossible:**

<!-- bind: chosen.impossible_now -->
What the ordinary version allows that this one does not.
<!-- /bind -->

<!-- section: first-use -->
## First contact

One concrete scene: a person, a place, a time, what they see and do, where they
hesitate. Not a description of the concept - a moment of it happening. Wrap the
whole scene in its own bind block, matching `concept.json`'s `first_use_scene`
word for word:

<!-- bind: first_use_scene -->
The scene itself, as plain prose - not a quotation, not a code fence.
<!-- /bind -->

<!-- section: neighbours -->
## Nearest existing things

What already exists near this, named, and how this differs. If nothing close was
found, say what was checked. Never claim nobody has thought of it.

<!-- section: open-questions -->
## Open questions

At least two, written so someone could actually answer them. Decoration does not
count: "how will users respond?" is not a question, "will the trust accept this
as the legal record without a countersignature?" is. Wrap each one in its own
bind block, numbered to match `concept.json`'s `open_questions` array in order
- the first question is `open_questions[0]`, the second `open_questions[1]`,
and so on for however many the session produced:

1. <!-- bind: open_questions[0] -->The first open question, word for word as it appears in concept.json.<!-- /bind -->
2. <!-- bind: open_questions[1] -->The second open question, word for word as it appears in concept.json.<!-- /bind -->

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

Four kinds of statement are marked, in place, above - `chosen.forbids` and
`chosen.impossible_now` in the concept section, `first_use_scene` in the
first-use section, every `open_questions[i]` in the open-questions section -
so the gate reads an assertion rather than guessing from word overlap. This is
not optional decoration: `spec_gate.py` fails once per missing block, so a spec
written from this template with a bind block deleted, or left empty, or
replaced with a plain paragraph, fails on that field alone even if every other
section is complete.

Each block appears exactly once, inside its own section, as plain prose - not
inside a blockquote, a code fence, or a struck-through line. The comparison is
exact after Unicode normalization and whitespace collapse, so revising or
translating the wording means updating `concept.json` to the delivered wording
before gating. See `references/example-concept.md` for a complete pair that
passes.

