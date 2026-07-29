# Blind A/B evaluation

This harness tests whether the concept workshop improves a direction the user
has already selected. It does not test initial idea generation.

## Conditions

- **Control:** use `prompts/control.md` in a clean context without this skill.
- **Treatment:** use `prompts/treatment.md` in a clean context that can load
  only the current `imagination-brainstorming` skill.
- Pin model, model version, temperature, reasoning setting, output budget, and
  run count before generation.
- Run both conditions on the same brief and selected direction.
- Use five independent runs per brief for confirmation.

Use `briefs.dev.jsonl` for iteration. Keep the real confirmation set outside
the repository until the design and rule are frozen.

## Output rows

```json
{"brief_id":"ward-handover","condition":"control","run":1,"text":"...","input_tokens":800,"output_tokens":900,"wall_seconds":15.2}
```

## Build a blind packet

```bash
python3 evals/harness.py packet \
  --briefs evals/briefs.dev.jsonl \
  --outputs /path/to/outputs.jsonl \
  --packet /path/to/packet.jsonl \
  --key /path/to/answer-key.jsonl \
  --seed preregistered-seed \
  --expected-runs 5
```

Give judges the packet and `prompts/judge.md`, never the key. A vote row is:

```json
{
  "comparison_id": "0123456789abcdef",
  "judge_id": "judge-1",
  "ratings": {
    "left": {"decision_fit": 6, "causal_clarity": 5, "robustness": 6, "actionability": 5},
    "right": {"decision_fit": 5, "causal_clarity": 4, "robustness": 4, "actionability": 5}
  },
  "want": "left"
}
```

`want` means: which memo would the judge rather take into planning?

## Score

```bash
python3 evals/harness.py score \
  --votes /path/to/votes.jsonl \
  --key /path/to/answer-key.jsonl \
  --outputs /path/to/outputs.jsonl \
  --report /path/to/report.json \
  --diagnostics /path/to/diagnostics.jsonl \
  --expected-judges 5
```

Use at least three blind judges per brief in development and five in
confirmation. Repeated model runs are collapsed to one majority WANT decision
per brief × judge before the Wilson interval is computed. Apply
`PREREGISTRATION.md` without changing thresholds after the answer key is opened.
The diagnostics file records each collapsed cell's run preferences, metric
deltas, and weakest metrics. Use the control-win cells to select one workshop
intervention at a time instead of tuning from the pooled mean alone.

After unblinding, archive the briefs, outputs, packet, answer key, votes, report,
and diagnostics together with hashes. A revealed confirmation set is retired;
never tune on it or reuse it as a holdout.

Change only one workshop intervention per development experiment. Keep it only
when it improves the result without breaking fit, actionability, or cost.
