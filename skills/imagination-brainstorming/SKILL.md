---
name: imagination-brainstorming
description: "Collaborative idea development that refuses to converge on the obvious. Use when the user wants to think an idea through before building it - a product, feature, service, game mechanic, story, world, ritual, campaign, format - or says their options all feel generic, safe, or interchangeable, or asks to brainstorm, explore approaches, or turn a rough idea into a concept spec. Interrogates the premises rather than collecting requirements, burns the obvious answers into a ban contract with the user, deals mutually incompatible approaches from a seeded deck, and gates the written concept spec before review. Produces a spec and hands off; never implements. Works in any language. Not for implementation planning, factual questions, or work where the conventional answer is the correct one."
---

# Imagination Brainstorming

Ordinary brainstorming converges too early, and not because there were too few
questions. The failure is that the questions come from the same distribution as
the answers: *who is the user, what are the constraints, what does success look
like* all refine the idea the person already has. They never touch what the
brief takes for granted. Then three options get proposed, two of which exist to
make the third look reasonable.

This skill keeps the collaborative shape - one question at a time, options with
trade-offs, a written spec, approval gates - and replaces the parts that
converge: the questions attack premises, the obvious answers are burned into a
contract *with* the user, the alternatives are dealt from a deck so they cannot
be variants of each other, and nothing reaches the user until it passes a gate.

**Working language.** Reason and run the scripts in English; talk to the user
and write the spec in whatever language they use.

<HARD-GATE>
While this skill is running, do NOT write code, scaffold anything, invoke an
implementation skill, or take any implementation action. Its terminal state is
a written, gated, user-approved concept spec plus a handoff. That applies to
every brief no matter how simple it looks.

The one exit is stage 0: if the conventional answer is the right answer here,
say so, stop running this skill, and then do the ordinary work outside it. That
is leaving the skill, not implementing inside it - the gates below apply only
while you are in it.
</HARD-GATE>

<HARD-GATE>
Do NOT put the concept spec in front of the user for review until
`scripts/spec_gate.py` exits 0, and do NOT put a set of approaches in front of
them until `scripts/divergence_check.py` exits 0.
</HARD-GATE>

## Hard rules

1. **One question per message.** Multiple choice when it fits. Never paste a
   deck prompt verbatim - rephrase it for this brief, in their language.
2. **The internal search stays internal.** Everything except what the process
   below explicitly says to show is working material.
3. **No unverifiable novelty claims.** Never write that nobody has thought of
   this. Name the nearest existing things and state the difference - required
   in the spec, every time.
4. **Every concept forbids something.** If the chosen direction rules nothing
   out, it is a wish list, and the gate will say so.
5. **Open questions are mandatory.** A spec with none has hidden its unknowns.
   Two minimum, written as questions someone could actually answer.
6. **YAGNI, but not by shrinking the ask.** Cut unrequested features. Do not
   soften the user's actual request to make it easier to spec.
7. **Never let enthusiasm end the divergence.** If the user gets excited at
   question two, finish the premise pass anyway, then show them the excitement
   alongside its alternatives.
8. **A non-zero exit is never success.** A failed gate means rework, not
   resubmission with the numbers rounded.

## When not to use this

Implementation planning (hand off instead), factual questions, copy edits,
naming, and any brief where the conventional answer is the correct answer - a
login form, a CRUD endpoint, a standard invoice flow. In that last case say so
in one sentence, leave this skill, and do the ordinary work outside it. The
skill's own hard rule is that it must not manufacture strangeness where none is
wanted - and its gates do not follow you out.

## Scripts

Paths are relative to this file's directory. In Claude Code that is
`${CLAUDE_PLUGIN_ROOT}/skills/imagination-brainstorming/`; in Codex, resolve the
directory containing this SKILL.md and use absolute paths. Python 3, standard
library only, no installation. Write working files to a scratch directory, never
into the skill folder.

| Script | Role | Non-zero exit |
|---|---|---|
| `scripts/deal.py` | Deals the question families and three mutually incompatible reframing lenses, one marked as the unsafe seat | 1 usage/deck error |
| `scripts/banlist.py` | Builds the shared ban contract: model instincts + shared skeleton + the user's own exclusions | 2 too few instincts, or no skeleton |
| `scripts/divergence_check.py` | Proves the three approaches are alternatives rather than one proposal and two decoys | 3 does not diverge |
| `scripts/spec_gate.py` | Validates `concept.json`, the written spec and the contract together, fail-closed | 2 gate failed |
| `scripts/cliche_lint.py` | Lints any draft mid-session against the contract | 3 banned material |

## Process

### 0. Recon and triage

Read the room before asking anything: existing files, docs, recent commits, any
prior spec. Then two checks, both cheap and both worth doing every time:

- **Scope.** If the brief contains several independent subsystems, say so
  immediately and help decompose it. Each piece gets its own session and its own
  spec. Do not spend premise questions on a brief that needs splitting first.
- **Fit.** If the predictable answer is the right answer here, say that in one
  sentence and offer to just do the ordinary thing.

### 1. Premise excavation

```bash
scripts/deal.py --brief "<the idea in the user's words>" --run 1 --out <work>
```

Ask the dealt families **one question per message**, rephrased for this brief.
Each family names what to listen for and the premise-preserving question to
avoid. Two or three families is often enough; stop when the answers stop
changing your picture of what this is.

Record what you learn as premises with a verdict - `deleted`, `inverted`, or
`kept` - and a reason. At least one must end up deleted or inverted; a session
where every premise survived refined the brief instead of testing it. If only
one falls, that is allowed - write `premises_note` saying why the others held.
**Do not invent a second inversion to satisfy a count.** A premise that survives
testing is a result, and manufacturing disagreement with the user to hit a quota
is exactly the dishonesty the gates exist to prevent.

### 2. The ban contract (shown to the user)

After about three questions, write the twelve answers most likely to be given to
this brief - your own first instincts, as short noun phrases - and name the
**skeleton** they share (the structure underneath: an apparatus, a feed, a
marketplace, a dashboard). The skeleton is the real target; banning twelve
phrasings while accepting the thirteenth version of the same shape achieves
nothing.

Write at least twelve; at least eight distinct entries must survive into the
contract, which is what the gate checks.

```bash
# 1. build it - no --confirmed yet, because nothing has been confirmed
scripts/banlist.py --brief "<brief>" --instincts instincts.txt \
  --skeleton "<one sentence>" --out <work>
```

Then show the user a compressed version - six or so entries plus the skeleton -
framed **as exclusions, not as suggestions**:

> "These are the answers that come cheapest here, so I'm taking them off the
> table. Which of them were you already picturing, and what would you add?"

That framing matters. The list is being retired in front of them; presented any
other way it becomes an anchor and you have just seeded the session with the
most obvious ideas available.

Only after they answer:

```bash
# 2. record what they added and that they signed it
scripts/banlist.py --brief "<brief>" --instincts instincts.txt \
  --skeleton "<one sentence>" --user user-exclusions.txt --confirmed --out <work>
```

`--confirmed` is a record of consent that already happened. Setting it before
they have seen the list is a lie the rest of the pipeline then relies on.

Their longer exclusions ("nothing that adds screen time at the bedside") cannot
be matched mechanically, so `banlist.py` files them as manual checks and the
gate requires a written answer for each one in
`banlist_contract.manual_checks_cleared` - one line per exclusion saying how the
concept avoids it.

### 3. Divergence

Build one approach per dealt frame. Each must occupy its frame's move, contain
what that frame requires, and state **how it would actually fail in this brief**
- not the generic hint from the deck.

One approach sits in the **unsafe seat**: the one you expect the user to reject.
Argue for it honestly and in the same detail as the others. A strawman in that
seat turns the other two into decoys, which is the exact failure this stage
exists to prevent.

```bash
scripts/divergence_check.py --approaches <work>/approaches.json --banlist <work>/banlist.json
```

Exit 3 means they are variants: same category, restated or identical summaries,
two that die of the same cause, or one written thin enough to be a decoy.
Rewrite, or redeal with `--run 2` and build again.

The check is structural. It cannot tell whether an approach actually occupies
its frame, and two frames from different categories can still overlap in
practice - `no-interface` and `inside-existing` are close cousins. That part is
yours: if two approaches would collapse into one under a single sentence, they
are one approach whatever the script says. Only then present all three in
comparable detail, with your recommendation and the reason for it.

### 4. Convergence

Once the user picks a direction, work it into a concept. The chosen approach
must state:

- **what it forbids** - what this design rules out on purpose, and the cost of
  that refusal;
- **what is now impossible** that the ordinary version allows;
- **the boring half** - the recurring task, the sign-off, the queue, the monthly
  reconciliation. This is where a concept becomes real, and it is usually the
  most useful material in the session.

Present the design in sections, scaled to their complexity, and ask after each
whether it holds. Go back when something does not.

### 5. Write the spec

Write `concept.json` (the sidecar that the gate reads, and the session state
that survives a long conversation) and the spec itself to
`docs/concepts/YYYY-MM-DD-<topic>-concept.md`, following
`references/concept-template.md`. Its section markers are what the gate checks.
Honour any project convention for spec location over this default.

### 6. Gate, then review

```bash
scripts/spec_gate.py --concept <work>/concept.json \
  --markdown docs/concepts/<file>.md --banlist <work>/banlist.json
```

All three arguments are required, and they must belong to the same session: the
gate checks that the ban list you pass is confirmed, carries the same skeleton
as `concept.json`, and contains the instincts the sidecar claims. Passing a
different or unconfirmed contract fails. It also checks that the written spec
actually asserts the concept. The refusal, what becomes impossible, the
first-use scene and every open question are marked with
`<!-- bind: <field> -->` ... `<!-- /bind -->` and compared to the sidecar
exactly - each exactly once, inside its own section, as plain prose. A
similarity score was tried first and could not separate a proposition being
asserted from the same words quoted inside a sentence that rejects them.

There is no `--allow` on this gate or on `divergence_check.py`. An exception
granted at verdict time is granted by the party the verdict is about; a real
one is made once while the contract is being built, recorded there with a
reason, shown to the user before they confirm it, and inherited from then on.

Then read it once yourself with fresh eyes: placeholders, contradictions between
sections, requirements that could be read two ways, scope that should have been
split. Fix inline; no second pass needed.

**If a second reader is available - another model, a colleague - have them
attack the concept before the user sees it.** Ask them to argue that it loses,
not that it could be improved. This is not ceremony: the gate proves the work
was not skipped and the lint proves specific familiar moves are absent, and
neither can catch the two failures that actually sink a concept - a
justification that inverts its own evidence ("the reader is a machine, so the
internal record matters" when that fact argues for the opposite), and a
mechanism that is attackable on its own terms (a number that changes depending
on the order it was computed in). Both survived every gate in this skill during
its own trial run and were caught by an adversarial read in minutes. Record what
you accepted and what you rejected in the decision log; a correction you refused
is as informative as one you took.

**Run a direction-of-evidence audit, second reader or not.** "Attack it" is too
vague to execute alone, and the inverted justification is the failure most
likely to survive everything else in this skill. So: pull out every load-bearing
*because*, *so*, and *therefore* in the concept, and for each one write down

1. the premise or evidence it rests on;
2. the conclusion it claims;
3. the strongest **opposite** conclusion the same premise supports;
4. the bridge - the assumption or observation that picks (2) over (3);
5. whose decision is supposed to change, and what that person or system can
   actually observe.

A justification fails if the premise supports (3) at least as well as (2), or if
the mechanism sits outside the observable boundary named in (5). Rewrite it or
cut it, and record the verdict. The trial-run example fails at step 5 in one
line: an automatic first-round scorer sees only the returned set, so it cannot
observe the internal record that was being offered as the differentiator - which
means that premise argues for accuracy, not for the record.

Do the same for any number the concept displays as evidence: recompute it with
the inputs in a different order. If it changes, it is a diagnostic of one
particular run and may be shown as that, but it cannot be presented as an
intrinsic property of anything.

Only then ask the user to review:

> "Spec written to `<path>`. Please read it and tell me what to change before we
> go any further."

Wait. If they want changes, make them, rerun the gate, ask again.

### 7. Handoff (terminal)

State plainly what this spec does not cover, then hand off:

- **`writing-plans`** - for software work that is ready to be planned.
- **`imagination-engine`** - if one object, creature, mechanism, or world
  inside the concept needs to be pushed much further than a spec can go.
  Optional: skip this line if that skill is not installed.
- **`stop`** - the spec was the deliverable.

Do not invoke an implementation skill. Handing off is the end of this skill's
job.

## Regeneration protocol

When the user says the options still feel safe, do not add adjectives or raise
the volume. Do exactly this: redeal with `--run <n+1>`, add every element of the
previous round to the contract via `--extra`, and delete one more premise from
stage 1. Tell them which premise you deleted - it is usually the one they were
unknowingly protecting.

## Self-interrogation before showing anything

Any yes sends it back a stage.

- Could two of the approaches be described by the same sentence?
- Is the unsafe option written weakly enough that nobody could choose it?
- Does the concept still contain the skeleton from the ban contract?
- Would this spec let a stranger build the obvious thing and claim they followed it?
- Did the user's excitement, rather than the premise work, decide this?
- Are the open questions real, or are they decoration?
- Is there anything here I would be unable to defend if the user asked "why
  this and not the ordinary version?"

## References

- `references/concept-template.md` - the spec structure and its section markers
- `references/worked-example.md` - one complete session, including what was cut
- `references/example-concept.json` - a sidecar that passes both gates
- `references/decks/` - question families, frames, clichés, spec schema
