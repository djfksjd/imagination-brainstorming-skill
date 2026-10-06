<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/imagination-octo-brainstorming-logo-dark.png" />
  <img src="assets/brand/imagination-octo-brainstorming-logo.png" alt="IMAGINATION OCTO BRAINSTORMING — Make one hold" width="380" />
</picture>

# IMAGINATION OCTO BRAINSTORMING

**MAKE ONE HOLD**

### The convergence half of Imagination Octo —<br/>one chosen direction, pressure-tested into a concept you can take to planning

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

[![Tests](https://img.shields.io/github/actions/workflow/status/djfksjd/imagination-octo-brainstorming/tests.yml?style=flat-square&label=tests)](https://github.com/djfksjd/imagination-octo-brainstorming/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-1f2937?style=flat-square)](LICENSE)
![Version](https://img.shields.io/badge/version-0.4.3-d69526?style=flat-square)
[![Family](https://img.shields.io/badge/part%20of-Imagination%20Octo-6d5ef5?style=flat-square)](https://github.com/djfksjd/imagination-octo)
![Hosts](https://img.shields.io/badge/hosts-Claude%20Code%20%C2%B7%20Codex-0ea5b7?style=flat-square)

</div>

Imagination Octo Brainstorming starts after a direction has been chosen. It tests that one idea against its goal, its constraints, its strongest ordinary alternative, daily operation, and its own failure mode, then returns a short concept memo. If the direction breaks the brief or loses to something simpler, it says so instead of polishing it.

> [!TIP]
> **Most users should install [Imagination Octo](https://github.com/djfksjd/imagination-octo).** It generates directions with the engine, waits for your choice, and passes that choice to this workshop.

**This is `v0.4.3`, a rename-only release of the runtime evaluated as v0.4.2.** The measurements below come from one small AI-judged comparison and are not a claim that every concept improves. Implicit invocation stays off: call the skill by name.

## What it does

| | |
|---|---|
| **Constraint preflight** | Is an excluded mechanism returning under another name, owner, location, or scale? |
| **Load-bearing assumption** | Which single belief would collapse the idea if it were false? |
| **Conventional competitor** | Why does this earn its added complexity over the ordinary answer? |
| **Core mechanism** | What observable cause changes the outcome? |
| **Boring half** | Who owns the recurring work, queues, exceptions, and maintenance? |
| **Native failure** | How does the defining mechanism fail on its own terms? |
| **Falsifier** | What result should make the team stop or change direction? |

## How it works

```text
 your chosen direction ──► ┌─────────────── constraint preflight ───────────────┐
                           │ is an excluded mechanism back under another name?  │
                           └──────────────────────────┬─────────────────────────┘
                                                      ▼
                           ┌────────────────── pressure test ───────────────────┐
                           │ load-bearing assumption · conventional competitor  │
                           │      boring half · native failure · falsifier      │
                           └──────────────────────────┬─────────────────────────┘
                                                      ▼
                                         decision-ready concept memo
                                                      ▼
                                           ◆ YOUR NEXT DECISION ◆        nothing is implemented
```

- The preflight is proportionate. A small violation gets the smallest repair, kept provisional, not a rewrite of the idea.
- Nothing is implemented. The output is a concept memo, not code, scaffolding, or an implementation plan.
- Nothing but one Markdown file is loaded at run time: no dealt frames, ban contracts, JSON sidecars, or quality gates.

## Try it

```text
Use $imagination-octo-brainstorming to develop this selected direction. Show the
first real use, the recurring operational burden, the native failure mode,
the falsifier, and the next decision we must make.
```

The reply is a concept memo that ends on the next decision, then stops.

## Measured

v0.4.2 against a strong plain prompt, preregistered and blind: 10 fresh English and Korean briefs with a direction already selected, 5 runs each, 5 judges (2026-07-30).

| Metric | Workshop minus plain prompt |
|---|---:|
| Preferred for planning | **45–5 (90%)** |
| Actionability | **+1.37** |
| Decision fit | **+0.95** |
| Robustness | **+0.82** |
| Causal clarity | **+0.71** |
| Tokens | `1.14×` |

Read these honestly:

- **One model generated and judged.** `gpt-5.4` only, with judges from the same family. The 95% Wilson interval for preference is 78.6–95.7%, so the lower bound does not establish a 90% rate.
- **It can lose.** Nine briefs went to the workshop unanimously, and one went to the plain prompt unanimously.
- **Not measured on Claude or by people.** The cross-model experiments in the Octo repository ([A](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-a.md), [B](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-b.md)) tested the engine only. Nothing here says how the workshop behaves on other models.
- **An earlier design was replaced.** The deck-and-gate workflow (v0.3.0), with dealt frames, ban contracts, and mechanical quality gates, is kept under [`legacy/v0.3.0/`](legacy/v0.3.0/) as a record and is never loaded.

Protocol, decision rule, and frozen results: [`evals/`](evals/README.md).

## When to use it, and when not

**Use it** when a direction, a shortlist winner, or a rough concept already exists and you need to know whether it holds before planning.

**Use something else** for first ideas or for implementation. For first ideas use [Imagination Octo Engine](https://github.com/djfksjd/imagination-octo-engine). The workshop deliberately stops before implementation.

## Renamed from `imagination-brainstorming`

Up to v0.4.2 this repository was `imagination-brainstorming-skill` and the skill was `$imagination-brainstorming`. GitHub redirects the old URL, but the plugin, the marketplace id, and the command changed: install `imagination-octo-brainstorming@imagination-octo-brainstorming` and call `$imagination-octo-brainstorming`. The runtime instructions are otherwise unchanged.

## Standalone install

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-octo-brainstorming/main/install.sh | bash
```

Run the same command again to update. If it reports older standalone copies of these skills, end the command with `| bash -s -- --clean-legacy` to move them aside; nothing is deleted.

```bash
# Claude Code
claude plugin marketplace add djfksjd/imagination-octo-brainstorming
claude plugin install imagination-octo-brainstorming@imagination-octo-brainstorming

# Codex
codex plugin marketplace add djfksjd/imagination-octo-brainstorming
codex plugin add imagination-octo-brainstorming@imagination-octo-brainstorming
```

## Development

```bash
python3 -m pytest tests/ -q
python3 evals/harness.py --help
bash -n install.sh
```

## License

[MIT](LICENSE).
