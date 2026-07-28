# Worked example

One complete session. The machine-readable result is
`references/example-concept.json`, which the test suite gates against - if the
pipeline ever stops accepting it, the tests fail.

**Request.** "We need a better way to hand over shifts on the ward. Everyone
hates the current handover."

---

## Stage 0 - recon and triage

One ward, one boundary, one artefact: in scope for a single session. The fit
check matters here though - handover is a solved genre with real standards
(SBAR, ISBAR) and a legal dimension. So this was said out loud before anything
else:

> "There is a conventional answer here - a structured handover form built on
> ISBAR - and for a lot of wards that is the right thing to build. Do you want
> me to help you do that well, or do you want to test whether the whole shape
> is wrong first?"

They wanted the second. That is consent to spend the session on premises.

## Stage 1 - premise excavation

```bash
deal.py --brief "a way for a hospital ward to hand over shifts" --run 1 --out ./work
```

Dealt families: `prior-attempts`, `forbidden-zone`, `non-user`, `terminal-state`,
`unstated-premise`. Four questions were asked, one per message. The two that
moved everything:

**`prior-attempts` — "What has been tried here, and what specifically killed
it?"** Two previous attempts. A paper form died because it was filled in at
19:15 from memory. A digital form died because it was filled in at 19:15 from
memory, on a screen. *Cause of death: composition at the boundary, not the
medium.* That single answer is what made the chosen approach possible.

**`non-user` — "Who is affected by this without ever choosing to use it?"** The
patient, and the nurse three shifts later. Neither is in the room when the
handover is written. This deleted the premise that the incoming nurse is the
audience.

Verdicts recorded: five premises, three inverted or deleted, one kept - the
legal record, which is non-negotiable and later kills an option outright. A
premise that survives testing is worth as much as one that falls; it just has to
be tested.

## Stage 2 - the ban contract

Twelve instincts written down first, then the skeleton named:

> *A capture tool that turns a spoken conversation into a structured record,
> with completeness enforced by a form and a signature at the end.*

Six of the twelve were shown to the user, framed as exclusions:

> "These are the answers that come cheapest here, so I'm taking them off the
> table - a structured handover form, a voice-to-text summary, a status board, a
> checklist with sign-off, a per-patient chat channel, a quality score. What
> they all share is that skeleton. Which of these were you already picturing,
> and what would you add?"

They had been picturing two of them, said so, and added three exclusions of
their own: no extra screen time at the bedside, no scoring of nurses, and
nothing that has to be filled in at 19:15. That third one is a restatement of
the cause of death from stage 1, arrived at independently - which is the signal
that the premise work landed.

```bash
# before showing them anything - nothing has been confirmed yet
banlist.py --brief "..." --instincts instincts.txt --skeleton "..." --out ./work

# after they answered, with their three exclusions added
banlist.py --brief "..." --instincts instincts.txt --skeleton "..." \
  --user user-exclusions.txt --confirmed --out ./work
```

Their two longer exclusions cannot be matched mechanically, so the gate later
required a written answer for each in `manual_checks_cleared`: the correction
pass happens at the station rather than the bedside, and nothing is composed at
19:15 because the draft already exists.

## Stage 3 - divergence

Three frames were dealt, from three categories. Each approach had to occupy its
frame and state how it would really fail:

| Frame | Approach | Its own failure |
|---|---|---|
| `conversation-only` *(unsafe seat)* | Nothing written; one fixed spoken sentence per patient, at the bedside, patient present | No durable record, and spoken discipline is the first thing a short-staffed ward drops at 03:00 |
| `hundred-times` | Abolish pairing; one ward-wide ledger of duties with owners and expiry, shift change is a bulk reassignment | An owner-less pool becomes a landfill; responsibility diffuses |
| `instant-version` | The handover assembles itself all shift; the nurse only corrects or refuses it in the last ten minutes | A draft that is 90% right teaches people to skim |

```bash
divergence_check.py --approaches ./work/approaches.json --banlist ./work/banlist.json
# overlap  spoken-form vs ward-ledger:  summary 0.04, failure 0.00
# overlap  spoken-form vs pre-written:  summary 0.04, failure 0.04
# overlap  ward-ledger vs pre-written:  summary 0.06, failure 0.00
# PASSED - these are alternatives, not variants.
```

The unsafe seat did its job. The spoken-only option was never going to be
chosen - the legal record premise kills it - but writing it properly is what
produced *duty plus owner plus deadline* as a sentence grammar, which then
became the format of every line in the option that did win. A strawman in that
seat would have produced nothing.

## Stage 4 - convergence

Chosen: the pre-written handover. What it forbids was written before anything
else:

> Composing a handover from scratch is forbidden, and "nothing to report" cannot
> be expressed without a name and a timestamp against it. Bulk acceptance of the
> draft is refused by design - which costs real minutes every shift and will be
> the first thing anyone asks to remove.

The boring half, extracted deliberately: eleven lines per shift, each either an
outstanding duty with an owner and a deadline or a stamped statement that
nothing is outstanding; the ten minutes at the station; the escalation when a
duty passes its deadline twice.

## Stage 5-6 - spec, gate, review

```bash
spec_gate.py --concept ./work/concept.json \
  --markdown docs/concepts/2026-07-28-ward-handover-concept.md --banlist ./work/banlist.json
```

All three inputs are required - the sidecar, the written spec and the contract -
because gating the sidecar alone would pass a session that never wrote the
document.

First run failed on two counts: `open_questions` had one entry, and
`chosen.forbids` was 40 characters of "it won't be a burden on staff". Neither
was fixed by rewording. The missing open questions existed - the legal record
question and the silent-error-rate question had both come up and been quietly
dropped because they were uncomfortable. Writing them down is what the gate is
for.

Then the user reviewed the file itself, changed one line about who owns an
unassigned duty, and approved.

## Stage 7 - handoff

Handed to `writing-plans` with the record question flagged as a blocker for the
plan. No code was written in this session, and no implementation skill was
invoked.

---

## What to copy from this example

- **The fit check is not a formality.** Saying "there is a conventional answer
  and it might be right" before spending the session is what makes the rest of
  it honest.
- **A cause of death beats a requirement.** "Composition at the boundary" came
  from one question about prior attempts and decided the whole design.
- **The kept premise did real work.** It killed an option cleanly. Premises are
  tested, not just deleted.
- **The unsafe option paid for itself without being chosen.** That is the
  argument for describing it at full strength.
- **The gate found hidden unknowns, not typos.** Both failures were questions
  the session had avoided. That is the failure mode it exists to catch.
