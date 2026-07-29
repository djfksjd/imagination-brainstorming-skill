# Repository guide

The runtime skill is `skills/imagination-brainstorming/SKILL.md`. It begins
after a user has selected a direction; initial ideation belongs elsewhere.

- Keep the runtime high-freedom and concise.
- Do not restore dealt frames, ban contracts, JSON sidecars, or mechanical
  quality gates.
- Put blind comparisons and scoring tools under `evals/`.
- Keep implicit invocation disabled until a preregistered holdout evaluation
  passes.
- Treat `legacy/v0.3.0/` as a read-only research record, not runtime context.
- Keep plugin versions and descriptions synchronized across all manifests.
- Run `python3 -m pytest tests/ -q` before committing.
