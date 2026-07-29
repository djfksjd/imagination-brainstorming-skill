# Imagination Brainstorming

Imagination Brainstorming v0.4 is a small experimental **concept workshop**. It
starts after a direction has been chosen and helps that idea survive its
assumptions, trade-offs, ordinary operation, and native failure mode.

It no longer tries to generate the initial idea. For divergent ideation, use
`imagination-engine`; use this skill to deepen the selected direction before
implementation.

The former question decks, ban contract, dealt frames, JSON sidecars, and
fail-closed gates are preserved under
[`legacy/v0.3.0/`](legacy/v0.3.0/) and are not loaded at runtime.

## What it does

- identifies the idea's load-bearing assumption;
- compares it with the strongest conventional alternative;
- explains the core mechanism and one concrete use;
- states what the concept refuses and who pays for that choice;
- develops the recurring operational work;
- names the native failure mode, response, and falsifier;
- records nearest existing approaches and real open decisions.

It uses no runtime scripts and no absolute self-score. If the selected idea
loses to the conventional alternative, the skill says so.

Implicit invocation is disabled during evaluation. Invoke
`$imagination-brainstorming` explicitly and provide the chosen direction.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-brainstorming-skill/main/install.sh | bash
```

Example:

```text
Use $imagination-brainstorming to develop this chosen direction:
the hospital handover should assemble during the shift, so the nurses correct
and accept outstanding duties instead of composing a report at the end.
```

## Evaluation

`evals/` compares the skill with a strong plain-prompt concept-development
control. Judges rate decision fit, causal clarity, robustness, actionability,
and which memo they would rather take into planning.

In the 2026-07-29 `gpt-5.4` confirmation, the skill was preferred 29 to 1
(96.7%, 95% Wilson interval 83.3–99.4%). Treatment-minus-control differences
were `+0.71` decision fit, `+0.78` causal clarity, `+1.02` robustness, and
`+1.15` actionability at `1.13x` tokens. Configuration and limitations are
recorded in
[`evals/results/2026-07-29-gpt-5.4-confirmation.json`](evals/results/2026-07-29-gpt-5.4-confirmation.json).

The blind judges were independent calls to the same model family, not human
domain users. Implicit invocation therefore remains off pending a separate
trigger-precision evaluation.

## Legacy

`legacy/v0.3.0/` preserves the previous runtime, examples, scripts, translated
documentation, and 570 regression tests. Those tests establish artefact
consistency, not concept quality.
