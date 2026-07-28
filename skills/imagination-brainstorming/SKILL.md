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

## Briefs that are not products

The process, the question families, the frames and the spec contract apply to
any subject. Two parts of the machinery do not, and knowing which is the
difference between trusting the gate and being puzzled by it.

- **The cliché phrase list is pitch-and-product vocabulary** - one-stop shop,
  KPI dashboard, Uber for X, gamification. On a story, world, ritual or
  mechanic brief almost none of it will ever fire. That is expected: on such a
  brief the machine-checkable half of the contract does little, and the
  session's own instincts and skeleton carry the weight. The hollow adjectives
  and the forbidden moves still apply everywhere.
- **A banned adjective can be ordinary vocabulary.** In fiction *magical* and
  *delightful* denote rather than claim. Mark that use with
  `<!-- mention: hollow-magical -->` (see stage 6) rather than editing the deck.

Two consequences worth expecting rather than discovering: more of your first
instincts will be clauses rather than noun phrases, so more of them land in the
manual checks - which are a reread, not twelve notes to write; and a dealt
frame is more likely to be one the brief cannot hold, which is what `frame_fit`
and a redeal are for. `references/example-ritual-concept.md` is a complete
worked example of exactly this shape.

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
| `scripts/divergence_check.py` | Refuses a set of approaches that is one proposal and two decoys: shared frame categories, restated summaries, coinciding failure modes, unequal detail | 3 does not diverge |
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

Your own long instincts land in the same list, and how many depends entirely on
the subject: a product instinct is a three-word noun phrase and becomes a
matchable ban, while a story, world, ritual or mechanic instinct is naturally a
clause and cannot be. Those are a **reread, not a written answer**. The gate
names them in a warning and does not fail on them; only the user's own
exclusions are answered in writing. The rule used to require an answer for
every long entry, which was invisible on a product brief and meant twelve
mandatory notes on a narrative one that no document had mentioned.

### 3. Divergence

Build one approach per dealt frame. Each must occupy its frame's move, contain
what that frame requires, and state **how it would actually fail in this brief**
- not the generic hint from the deck.

One approach sits in the **unsafe seat**: the one you expect the user to reject.
Argue for it honestly and in the same detail as the others. A strawman in that
seat turns the other two into decoys, which is the exact failure this stage
exists to prevent.

Write them to `<work>/approaches.json` yourself - nothing generates that file;
`deal.py` deals the frames and you write one approach per dealt frame. It is a
JSON object with an `approaches` key (a bare list also works), one object per
approach:

```json
{"approaches": [
  {"id": "spoken-form", "frame_id": "conversation-only", "unsafe_seat": true,
   "summary": "what it is, what it asks of whom, and what makes it this frame (96+ units)",
   "failure_mode": "how this one actually fails in this brief (48+ units)",
   "frame_fit": "what in this brief plays the part the frame's must_contain names (40+ units)"}
]}
```

`frame_fit` is where a frame the brief cannot hold becomes visible. Every frame
names one thing its approach must contain - the sentence people will actually
say, the repair procedure and the spare parts, the threshold where the kind of
thing changes - and you write what plays that part here. If nothing can, the
frame is not occupiable by this brief: say so, redeal with `--run 2`, and do
not argue it. `designed-for-repair` was dealt into the unsafe seat for a
one-off closing rite that happens once and has no maker and no spare parts, and
the user was shown a full-length argument for it. The check requires the claim;
it cannot check that the claim is true.

`references/decks/approaches-schema.json` is the full field list with the floors
and thresholds this check applies; `references/example-approaches.json` is a
passing file to copy the shape from. `chosen` is added later, after the user
picks, and is read by `spec_gate.py` rather than here.

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
  most useful material in the session;
- **how it survives its own failure mode** - the approach you chose already
  stated how it fails in this brief. Write what the design does about that in
  `chosen.answers_failure_mode`. The gate refuses a spec that never wrote one
  and refuses an answer that is the failure restated; it cannot judge whether
  the failure is fatal or whether your answer works, so it prints the declared
  failure beside your answer for whoever reads the verdict. A concept that
  declares its own collapse and moves on used to pass here first try.

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

All three arguments are required, and the gate checks that they are consistent
with each other - not that they came from one session, which nothing here can
establish. It rebuilds the contract from what `concept.json` declares - the
same classification `banlist.py` applied - and every resulting ban, every one
of the user's long exclusions and every entry of the bundled cliché deck must
be present in the file you pass. The ban list and `concept.json` must record
the same skeleton and the same brief, string for string, and the ban list's
brief must name a subject rather than a word: that join used to be a word
overlap at 0.5 and it failed in both directions, passing a contract whose brief
was the single word "ward" and refusing an honest rewording of the author's own
brief in synonyms. The free-form `brief` field in `concept.json`, which exists
to restate and expand the ask, is compared only as a warning. A contract
written by hand, trimmed, or carried over from another session fails on the
replay, and the deck is linted against whatever arrives, so a shorter file
cannot mean a shorter lint. The gate also checks that the written spec
actually asserts the concept. The refusal, what becomes impossible, the
first-use scene and every open question are marked with
`<!-- bind: <field> -->` ... `<!-- /bind -->` and compared to the sidecar
exactly - each exactly once, inside its own section, as plain prose. A
similarity score was tried first and could not separate a proposition being
asserted from the same words quoted inside a sentence that rejects them.

A banned word is sometimes being quoted or denied rather than used - "the
region is not magical" was refused for saying so. Mark that span in place:

```markdown
<!-- mention: hollow-magical -->The region is not magical<!-- /mention -->
```

The release covers that span and that rule id only; everything outside it, and
every other rule inside it, is linted as before. An unknown or unnamed id is
refused, and every mention is printed in the verdict. This cannot verify that
the word is really mentioned rather than used - a regex cannot tell an
assertion from a quotation, which is the whole reason the marker exists. It
makes the claim explicit, local and reviewable instead of leaving a blanket
release as the only escape.

There is no `--allow` on this gate or on `divergence_check.py`, and the gate
does not honour the `allowed` field of the ban list either. An exception
granted at verdict time is granted by the party the verdict is about, and a
ban list that can exempt itself is a flag with extra steps: naming two cliché
ids in `allowed` once released both from the verdict. A release made with
`banlist.py --allow` still shortens the drafting lint (`cliche_lint.py`), and
the gate still accepts it as the reason an entry is absent from the file - it
just does not stop that phrase being linted. Releasing a bundled cliché at the
gate means changing `references/decks/cliches.json`, where the change is
reviewed outside the session that wants it. Bundled entries and structural
patterns also win on id: a supplied rule carrying a bundled id is dropped
rather than merged, so the deck cannot be demoted or neutered by the file
under judgement.

Two of the user's long exclusions may not share an id, and neither may two of
the answers to them, because the gate joins answer to exclusion by that id and
one written note used to discharge two checks. The id is still written by the
same caller that writes both files; making a collision a failure costs a
rejected contract rather than closing the join.

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
- Did the chosen approach's stated failure mode get answered, or only acknowledged?
- Could any of the three frames not actually be occupied by this brief?
- Is there anything here I would be unable to defend if the user asked "why
  this and not the ordinary version?"

## References

- `references/concept-template.md` - the spec structure and its section markers
- `references/worked-example.md` - one complete session, including what was cut
- `references/example-concept.json` - a sidecar that passes both gates
- `references/example-concept.md` - the spec that session produced
- `references/example-approaches.json` - stage 3 input in the shape the check reads
- `references/example-banlist.json` - the contract those two were gated against
- `references/example-instincts.txt`, `references/example-exclusions.txt` - what it was built from
- `references/example-ritual-concept.json`, `references/example-ritual-concept.md`,
  `references/example-ritual-approaches.json`, `references/example-ritual-banlist.json`,
  `references/example-ritual-instincts.txt`, `references/example-ritual-exclusions.txt` -
  a second complete example that is not a product or a service: a closing rite for a bakery
- `references/decks/` - question families, frames, clichés, spec schema, approaches schema

Every example is runnable. From this directory:

```bash
scripts/banlist.py --brief "a way for our ward to hand over shifts" \
  --instincts references/example-instincts.txt \
  --user references/example-exclusions.txt \
  --skeleton "A capture tool that turns a spoken conversation into a structured record, with completeness enforced by a form and a signature at the end." \
  --confirmed --out /tmp/work        # reproduces references/example-banlist.json

scripts/divergence_check.py --approaches references/example-approaches.json \
  --banlist references/example-banlist.json

scripts/spec_gate.py --concept references/example-concept.json \
  --markdown references/example-concept.md \
  --banlist references/example-banlist.json

scripts/spec_gate.py --concept references/example-ritual-concept.json \
  --markdown references/example-ritual-concept.md \
  --banlist references/example-ritual-banlist.json
```
