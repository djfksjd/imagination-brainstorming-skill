<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/imagination-octo-brainstorming-logo-dark.png" />
  <img src="assets/brand/imagination-octo-brainstorming-logo.png" alt="IMAGINATION OCTO BRAINSTORMING — Faça uma se sustentar" width="380" />
</picture>

# IMAGINATION OCTO BRAINSTORMING

**MAKE ONE HOLD**

### A metade convergente do Imagination Octo —<br/>uma direção escolhida, testada sob pressão até virar um conceito que você pode levar ao planejamento

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

[![Tests](https://img.shields.io/github/actions/workflow/status/djfksjd/imagination-octo-brainstorming/tests.yml?style=flat-square&label=tests)](https://github.com/djfksjd/imagination-octo-brainstorming/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-1f2937?style=flat-square)](LICENSE)
![Version](https://img.shields.io/badge/version-0.4.3-d69526?style=flat-square)
[![Family](https://img.shields.io/badge/part%20of-Imagination%20Octo-6d5ef5?style=flat-square)](https://github.com/djfksjd/imagination-octo)
![Hosts](https://img.shields.io/badge/hosts-Claude%20Code%20%C2%B7%20Codex-0ea5b7?style=flat-square)

</div>

O Imagination Octo Brainstorming começa depois que uma direção foi escolhida. Ele testa essa única ideia contra seu objetivo, suas restrições, sua alternativa convencional mais forte, a operação do dia a dia e seu próprio modo de falha, e devolve um memorando de conceito curto. Se a direção viola o brief ou perde para algo mais simples, ele diz isso em vez de poli-la.

> [!TIP]
> **A maioria das pessoas deve instalar o [Imagination Octo](https://github.com/djfksjd/imagination-octo).** Ele gera direções com o motor, espera a sua escolha e passa essa escolha para esta oficina.

**Esta é a `v0.4.3`, uma versão que apenas renomeia o runtime avaliado como v0.4.2.** As medições abaixo vêm de uma única comparação pequena julgada por IA e não afirmam que todo conceito melhora. A invocação implícita continua desligada: chame a skill pelo nome.

## O que ele faz

| | |
|---|---|
| **Verificação prévia de restrições** | Um mecanismo excluído está voltando com outro nome, responsável, lugar ou escala? |
| **Premissa de sustentação** | Que crença única derrubaria a ideia se fosse falsa? |
| **Concorrente convencional** | Por que ela merece a complexidade extra em relação à resposta comum? |
| **Mecanismo central** | Que causa observável muda o resultado? |
| **A metade entediante** | Quem cuida do trabalho recorrente, das filas, das exceções e da manutenção? |
| **Falha própria** | Como o mecanismo que define a ideia falha em seus próprios termos? |
| **Falseador** | Que resultado deveria fazer a equipe parar ou mudar de direção? |

## Como funciona

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

- A verificação prévia é proporcional. Uma violação pequena recebe o menor reparo, mantido como provisório, e não uma reescrita da ideia.
- Nada é implementado. O resultado é um memorando de conceito, não código, estrutura inicial ou plano de implementação.
- Em tempo de execução só um arquivo Markdown é carregado: sem quadros distribuídos, contratos de proibição, arquivos JSON auxiliares ou portões de qualidade.

## Experimente

```text
Use $imagination-octo-brainstorming para desenvolver esta direção escolhida. Mostre
o primeiro uso real, a carga operacional recorrente, o modo de falha próprio,
o falseador e a próxima decisão que precisamos tomar.
```

A resposta é um memorando de conceito que termina na próxima decisão e então para.

## Medições

v0.4.2 contra um prompt simples forte, pré-registrado e às cegas: 10 briefs novos em inglês e coreano com uma direção já escolhida, 5 execuções cada, 5 juízes (2026-07-30).

| Métrica | Oficina menos prompt simples |
|---|---:|
| Preferido para planejar | **45–5 (90%)** |
| Acionabilidade | **+1,37** |
| Aderência à decisão | **+0,95** |
| Robustez | **+0,82** |
| Clareza causal | **+0,71** |
| Tokens | `1,14×` |

Leia com honestidade:

- **Um único modelo gerou e julgou.** Apenas `gpt-5.4`, com juízes da mesma família. O intervalo de Wilson de 95% para a preferência é 78,6–95,7%, então o limite inferior não comprova uma taxa de 90%.
- **Ela pode perder.** Nove briefs foram para a oficina por unanimidade, e um foi para o prompt simples por unanimidade.
- **Não foi medida com o Claude nem por pessoas.** Os experimentos entre modelos do repositório do Octo ([A](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-a.md), [B](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-b.md)) testaram apenas o motor. Nada aqui diz como a oficina se comporta com outros modelos.
- **Um desenho anterior foi substituído.** O fluxo de baralho e portões (v0.3.0), com quadros distribuídos, contratos de proibição e portões de qualidade mecânicos, fica em [`legacy/v0.3.0/`](legacy/v0.3.0/) como registro e nunca é carregado.

Protocolo, regra de decisão e resultados congelados: [`evals/`](evals/README.md).

## Quando usar e quando não usar

**Use** quando já existe uma direção, uma favorita da lista curta ou um conceito bruto e você precisa saber se ele se sustenta antes de planejar.

**Use outra coisa** para as primeiras ideias ou para implementar. Para as primeiras ideias use o [Imagination Octo Engine](https://github.com/djfksjd/imagination-octo-engine). A oficina para de propósito antes da implementação.

## Renomeado de `imagination-brainstorming`

Até a v0.4.2 este repositório era `imagination-brainstorming-skill` e a skill era `$imagination-brainstorming`. O GitHub redireciona a URL antiga, mas o plugin, o id do marketplace e o comando mudaram: instale `imagination-octo-brainstorming@imagination-octo-brainstorming` e chame `$imagination-octo-brainstorming`. No restante, as instruções do runtime não mudaram.

## Instalação independente

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-octo-brainstorming/main/install.sh | bash
```

Para atualizar, execute o mesmo comando de novo. Se ele avisar sobre cópias antigas dessas skills instaladas separadamente, termine o comando com `| bash -s -- --clean-legacy` para movê-las; nada é apagado.

```bash
# Claude Code
claude plugin marketplace add djfksjd/imagination-octo-brainstorming
claude plugin install imagination-octo-brainstorming@imagination-octo-brainstorming

# Codex
codex plugin marketplace add djfksjd/imagination-octo-brainstorming
codex plugin add imagination-octo-brainstorming@imagination-octo-brainstorming
```

## Desenvolvimento

```bash
python3 -m pytest tests/ -q
python3 evals/harness.py --help
bash -n install.sh
```

## Licença

[MIT](LICENSE).
