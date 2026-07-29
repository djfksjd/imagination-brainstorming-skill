# Imagination Brainstorming

Imagination Brainstorming v0.4.1 is a small experimental **concept workshop**. It
starts after a direction has been chosen and helps that idea survive its
assumptions, trade-offs, ordinary operation, and native failure mode.

## Recommended combined plugin

Most users should install [`djfksjd/imagination`](https://github.com/djfksjd/imagination)
and invoke `$imagination`. It generates a portfolio with
`imagination-engine`, waits for the user to choose, then routes the selected
direction into this workshop on the next turn.

Install this standalone repository when you already have a selected direction
or need to evaluate the workshop independently.

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

## Standalone install

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

After adding the constraint preflight, a fresh 2026-07-29 `gpt-5.4`
confirmation preferred the skill 25 to 5 (83.3%, 95% Wilson interval
66.4–92.7%). Treatment-minus-control differences were `+0.59` decision fit,
`+0.59` causal clarity, `+0.53` robustness, and `+1.37` actionability at
`1.15x` tokens. Configuration and limitations are recorded in
[`evals/results/2026-07-29-gpt-5.4-confirmation-v2.json`](evals/results/2026-07-29-gpt-5.4-confirmation-v2.json).

The blind judges were independent calls to the same model family, not human
domain users. Implicit invocation therefore remains off pending a separate
trigger-precision evaluation.

## Legacy

`legacy/v0.3.0/` preserves the previous runtime, examples, scripts, translated
documentation, and 570 regression tests. Those tests establish artefact
consistency, not concept quality.
