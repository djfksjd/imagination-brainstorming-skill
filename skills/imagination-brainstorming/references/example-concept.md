# Flat-Line Handover

<!-- section: brief -->
## What was asked for

"We need a better way to hand over shifts on the ward. Everyone hates the current handover."

What the session established it actually is: the ward's problem is not that information fails to be recorded — the chart holds that on its own. It is that **unfinished obligations die at the boundary between two people**. Two previous attempts failed for the same reason, and it was not the medium.

<!-- section: premises -->
## Premises

| Premise | Verdict | Why |
|---|---|---|
| Handover transfers information from the outgoing nurse to the incoming one | **inverted** | What actually transfers is a set of unfinished duties with owners. Facts survive in the chart; duties evaporate. |
| Handover happens at shift change | **inverted** | Duties accrue all shift. Shift change is only when they are settled, which is why writing the summary at 19:15 is the worst possible moment to remember anything. |
| The patient is the subject of the handover, never a participant | **deleted** | The patient is present at every handover about them and is the only one who notices when a duty is dropped twice. |
| The handover must produce a legally admissible record | **kept** | Non-negotiable for the trust. This is what later kills the spoken-only option outright. |
| The incoming nurse is the audience | **deleted** | The party harmed by a bad handover is the patient and the nurse three shifts later, neither of whom is in the room when it is written. |

<!-- section: banlist -->
## What is off the table

Confirmed with the charge nurse before any approach was built.

**Skeleton:** a capture tool that turns a spoken conversation into a structured record, with completeness enforced by a form and a signature at the end.

**Model instincts, retired:** handover app with structured form · digitised SBAR template · voice-to-text shift summary · AI summary of the shift · ward status board · checklist with sign-off · chat channel per patient · task board with cards · wearable that records rounds · auto-transcribed nurse notes · handover quality score · smart whiteboard at the station.

**Added by the ward:** nothing that adds screen time at the bedside · no scoring or ranking of nurses · not another form to fill in at 19:15.

<!-- section: approaches -->
## Approaches considered

**A. Spoken form only** *(unsafe seat — frame: `conversation-only`)*. No artefact at all. The ward adopts one fixed spoken sentence per patient, said at the bedside with the patient awake and present: what is outstanding, who it now falls to, by when. The incoming nurse repeats it back; the patient can correct it; nothing is typed. *Fails because:* nothing durable is produced, so the trust still needs its written record made separately, and spoken discipline is the first thing a short-staffed ward abandons at 03:00.

**B. Ward ledger** *(frame: `hundred-times`)*. Stop pairing nurses. Every outstanding duty on the ward enters one visible ledger with an owner and an expiry, and shift change becomes a bulk reassignment event. *Fails because:* an owner-less pool becomes a landfill — items age, the oldest are quietly ignored, and responsibility spreads thin enough that no individual feels the weight of any particular duty.

**C. Pre-written handover** *(chosen — frame: `instant-version`)*. The handover is finished before the shift ends, assembling itself continuously from what already happened. The nurse's only act is to correct or refuse it. *Fails because:* a draft that is ninety per cent right trains people to skim, and the tenth that is wrong is exactly the unusual thing that mattered.

<!-- section: concept -->
## The concept

The handover assembles itself all shift from orders placed, medication given, calls made and results still pending. By 19:00 a complete draft exists that nobody composed. In the last ten minutes at the station the outgoing nurse corrects or refuses it, line by line.

Each line must carry **either** an outstanding duty with a named owner and a deadline, **or** an explicit statement that nothing is outstanding, stamped with who checked and when.

**What it forbids:**

<!-- bind: chosen.forbids -->
It forbids composing a handover from scratch, and it forbids the state 'nothing to report' from being expressible without a name and a timestamp attached. Bulk acceptance of the draft is refused by design, which costs the ward real minutes on every shift and will be the first thing anyone asks to remove.
<!-- /bind -->

**What becomes impossible:**

<!-- bind: chosen.impossible_now -->
Passing a patient to the next shift with no statement about them at all becomes impossible; silence is no longer a valid handover state.
<!-- /bind -->

**How it survives its own failure mode:** the approach's stated death is presumption - a draft that is ninety per cent right trains people to skim. Skimming is the death this approach wrote down for itself, so the design has to make bulk acceptance impossible rather than discouraged: every line is accepted or amended one at a time by the nurse taking it on, and a line nobody touches stays open and appears on the next handover with its age showing. The bet is narrower than 'friction survives a busy ward' - it only has to survive eleven lines, and an untouched line costs the outgoing nurse a second conversation rather than nothing. What would falsify it: if the ageing lines are routinely cleared in a batch at the end of the week, the mechanism has failed and the ward should go back to the ledger.

**The boring half:** eleven lines a shift; the ten minutes at the station; the escalation path when a duty passes its deadline twice; the monthly reconciliation of duties that were inherited but never closed.

<!-- section: first-use -->
## First contact

<!-- bind: first_use_scene -->
19:12, station desk, the ward still loud from a late admission. The screen already holds tonight's handover: eleven patients, each one line, none of them written by her. She reads down and the fourth line says an ultrasound request is still unacknowledged since 14:40, which she had forgotten entirely. The seventh line says nothing is outstanding for bed 7, and it will not let her move past it until she puts her name and the time against that claim, so she walks over and actually looks at bed 7 before coming back and stamping it. At 19:20 the incoming nurse sits down beside her and they go through the four lines that changed, not the eleven that did not. The patient in bed 3, awake, hears her own line read out and says the pain relief was an hour ago, not two, and the line is corrected in front of her.
<!-- /bind -->

<!-- section: neighbours -->
## Nearest existing things

- **SBAR and ISBAR structured verbal handover.** Those shape what a person composes at the end of a shift. Here nothing is composed at all; the draft exists already and the nurse's work is refusal and correction.
- **Electronic handover modules in hospital record systems.** Those collect free text into a form and require a signature at the end. This one forbids the empty state, attaches a named owner and a deadline to every duty, and cannot be accepted in bulk.
- **Aviation read-back procedure.** Read-back verifies that a message was received correctly. This verifies that an obligation has an owner after the boundary — a different failure to catch.

<!-- section: open-questions -->
## Open questions

1. <!-- bind: open_questions[0] -->Will the trust accept a corrected auto-assembled draft as the legal record without a separate countersignature, or does that force a second artefact?<!-- /bind -->
2. <!-- bind: open_questions[1] -->What is the silent error rate - how often is a wrong line accepted unchanged - and can it be measured without scoring individual nurses, which the ward has ruled out?<!-- /bind -->
3. <!-- bind: open_questions[2] -->Who inherits a duty when the next shift is short-staffed and nobody can be named as its owner?<!-- /bind -->

<!-- section: decisions -->
## Decision log

| Decision | Why | When |
|---|---|---|
| Rejected the spoken-only option as the primary design | The kept premise about the legal record kills it; a ward cannot run a second written process alongside it | 2026-07-28, after the premise pass |
| Adopted its sentence grammar anyway — duty, owner, deadline | Strongest thing produced in the session, and it survives being written down | 2026-07-28, convergence |
| Bulk acceptance refused, at a known cost in minutes | Skimming is the stated failure mode of this approach; removing the friction removes the design | 2026-07-28, convergence |

<!-- section: handoff -->
## Handoff

**Not covered here:** the record-keeping question above is a blocker, the integration surface with the existing record system, and anything about rollout or training beyond the ten-minute ritual at the station.

**Next:** `writing-plans`, once the trust has answered the legal-record question. No code was written in this session.
