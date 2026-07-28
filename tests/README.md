# tests

Offline pytest suite. Run from the repository root:

```bash
python3 -m pytest tests/ -q
```

The scripts use only the Python 3 standard library and make no network calls, so
nothing is stubbed. Each test invokes a script as a subprocess, which means exit
codes — the contract the skill actually depends on — are covered directly rather
than approximated.

| File | Covers |
|---|---|
| `test_decks.py` | Deck integrity: unique ids, populated frame categories, every question family carrying both what to listen for and its anti-pattern, valid cliché regexes, schema ↔ template agreement |
| `test_deal.py` | The deal is deterministic per brief, frames span disjoint categories, exactly one unsafe seat, the seat rotates between rounds, later rounds deal fresh frames, bad arguments fail loudly |
| `test_banlist.py` | The two ways the contract can be faked (too few instincts, no skeleton), bullet stripping, user exclusions labelled and merged, long exclusions becoming manual checks, `--allow`, `--confirmed` |
| `test_divergence_check.py` | Every shape a decoy takes: restated summaries, shared failure modes, same category, missing or duplicated unsafe seat, a thin option, an unknown frame, banned phrases |
| `test_spec_gate.py` | Every way the work can be skipped while the spec still looks finished, plus the markdown contract: required sections, order, section length, and the ban-contract lint exemption |
| `test_hardening.py` | Regressions from the adversarial review — CJK comparison, Korean particle matching, padding detection, string booleans, invented frame ids, skeleton restatement, unanswered user exclusions, lowered counts, malformed ban lists, and the pitch-vs-scene distinction |
| `test_repo.py` | Version sync across manifests and decks, the root `SKILL.md` symlink, referenced files existing, the eight READMEs staying cross-linked and host-accurate, and the shipped spec agreeing with its sidecar |

`conftest.py` holds the subprocess `run` helper, the instinct/user/ban-contract
fixtures built from the shipped example, and the `gate` helper that supplies
`spec_gate.py` with all three of its required inputs.

## Why the fixtures are the shipped example

`references/example-concept.json` and `references/example-concept.md` are both
the documentation and the fixtures. If a change to a deck, a threshold or a gate
stops accepting them, the suite fails — which is the intended coupling: the
example a user is told to imitate cannot quietly stop passing the gates it is
supposed to demonstrate.
