<div align="center">

# Imagination Brainstorming

**Desenvolvimento de ideias que se recusa a convergir para o óbvio.**

Uma skill de agente que mantém o formato de um bom brainstorming — uma pergunta por vez, alternativas de verdade,<br>uma especificação escrita — e substitui as partes que puxam tudo, em silêncio, de volta para a resposta segura.

[![tests](https://github.com/djfksjd/imagination-brainstorming-skill/actions/workflows/tests.yml/badge.svg)](https://github.com/djfksjd/imagination-brainstorming-skill/actions/workflows/tests.yml)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-D97757)](#instalação)
[![Codex](https://img.shields.io/badge/Codex-plugin-1f2328)](#instalação)
[![Python](https://img.shields.io/badge/python-3.11%2B_só_stdlib-3776AB)](#por-dentro)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · **Português**

</div>

---

> O brainstorming converge cedo demais — e não por falta de perguntas. A falha é que as perguntas saem da mesma distribuição das respostas: *quem é o usuário, quais são as restrições, como é o sucesso* apenas lapidam a ideia que você já tem. Nenhuma delas toca no que o briefing dá como certo.
>
> Aí surgem três opções — duas das quais existem para fazer a terceira parecer razoável.

## Como funciona

```mermaid
flowchart LR
    A["Sua ideia crua"] --> B["<b>1 · Escavar</b><br/>perguntas que atacam<br/>premissas, uma por mensagem"]
    B --> C["<b>2 · Contrato</b><br/>as 12 respostas mais baratas<br/>+ o esqueleto que compartilham,<br/>assinado <i>com você</i>"]
    C --> D["<b>3 · Divergir</b><br/>3 abordagens de molduras<br/>disjuntas, uma na<br/>cadeira incômoda"]
    D --> E{"checagem de<br/>divergência"}
    E -- "variantes" --> D
    E -- "alternativas" --> F["<b>4 · Convergir</b><br/>o que proíbe ·<br/>a metade chata"]
    F --> G{"portão da<br/>spec"}
    G -- "trabalho pulado" --> F
    G -- "passa" --> H["Spec de conceito<br/>→ sua revisão<br/>→ repasse"]
```

|  | O que acontece | Por que funciona |
|---|---|---|
| **1** | **Perguntas que atacam premissas.** Distribuídas de um baralho de doze famílias — a premissa não dita, a versão que você odiaria, para quem isto *não* é, como termina, em que escala quebra, a metade administrativa. Cada família diz o que escutar e qual pergunta preservadora de premissas evitar. | Requisitos se apoiam em premissas. Perguntar requisitos confirma a ideia; perguntar premissas a testa. Ao menos uma premissa precisa acabar apagada ou invertida — e se só uma cair, a spec tem de dizer por que as outras seguraram. Inventar uma segunda inversão para bater uma cota é pior do que um honesto "ela sobreviveu". |
| **2** | **Um contrato de vetos que você também assina.** O modelo escreve as doze respostas que mais provavelmente daria, nomeia o *esqueleto* que elas compartilham e te mostra uma versão comprimida — como exclusões, nunca como sugestões. Você acrescenta o seu "outro X não". | Suas exclusões são a restrição mais valiosa da sala, e nomear o esqueleto impede que a décima terceira versão do mesmo formato passe despercebida. |
| **3** | **Alternativas que não podem ser variantes.** Três abordagens tiradas de categorias de reenquadramento disjuntas, uma delas na **cadeira incômoda** — a opção que você provavelmente vai recusar, defendida com força total. | Um script confere: mesma categoria, resumos idênticos ou que se repetem, duas que morrem da mesma causa, ou uma descrita com bem menos detalhe — tudo falha com exit 3. Ele confere estrutura, não sentido — mas os formatos que um figurante precisa assumir são exatamente esses. |
| **4** | **Um portão antes de te pedirem para ler qualquer coisa.** O conceito precisa dizer o que proíbe, nomear seus vizinhos existentes mais próximos e carregar ao menos duas perguntas em aberto de verdade. | Uma spec sem perguntas em aberto escondeu suas incógnitas. Um design que não proíbe nada é uma lista de desejos. O portão não julga um conceito — ele prova que o trabalho não foi pulado. |

> [!IMPORTANT]
> **Nunca implementa.** Sem código, sem scaffolding, sem "começo a construir?". O estado final é uma spec aprovada por você, mais um repasse.

## Instalação

Roda no **Claude Code** e no **Codex**. Apenas biblioteca padrão do Python 3: nada a instalar, sem chave de API, sem acesso à rede.

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-brainstorming-skill/main/install.sh | bash
```

<details>
<summary><b>Instalação manual</b></summary>

```bash
# Claude Code
claude plugin marketplace add djfksjd/imagination-brainstorming-skill
claude plugin install imagination-brainstorming@djfksjd

# Codex
codex plugin marketplace add djfksjd/imagination-brainstorming-skill
codex plugin add imagination-brainstorming@djfksjd
```

Uma única árvore serve os dois hosts: o corpo da skill fica em `skills/imagination-brainstorming/`, e `AGENTS.md` é carregado como contexto compartilhado.
</details>

## Como usar

Diga o que está remoendo. Ela dispara em pedidos de brainstorming e na reclamação de que todas as opções até agora parecem iguais. Funciona em qualquer idioma; a spec é escrita no seu.

```text
Pensa isso comigo: um jeito de fazer a passagem de plantão na ala.
```

```text
Tenho três ideias para o onboarding e todas parecem a mesma ideia.
Aperta de verdade antes de eu decidir.
```

### O que uma sessão realmente faz

| Etapa | O que você vê | O que impõe |
|---|---|---|
| Reconhecimento | "Existe uma resposta convencional aqui e ela pode ser a certa — você quer essa, ou testamos o formato inteiro primeiro?" | Regra dura: nada de estranheza fabricada |
| Escavação | Uma pergunta por mensagem, reescrita para o seu briefing | 12 famílias de perguntas, cada uma com seu antipadrão |
| Contrato | Seis exclusões + o esqueleto que compartilham, para confirmar e ampliar | `banlist.py`, exit 2 se for fingido |
| Divergência | Três abordagens no mesmo nível de detalhe, uma que você provavelmente odeia | `divergence_check.py`, exit 3 se forem variantes |
| Convergência | Projeto seção a seção, cada uma aprovada antes da seguinte | O que proíbe é escrito primeiro |
| Spec | `docs/concepts/AAAA-MM-DD-<tema>-concept.md` + um sidecar legível por máquina | `spec_gate.py`, exit 2 se pularam trabalho |
| Repasse | O que esta spec *não* cobre e o que vem depois | Nunca uma skill de implementação |

### Os baralhos

| Baralho | Conteúdo |
|---|---|
| **Famílias de perguntas** (12) | premissa não dita · a versão que você odiaria · o sucesso redefinido · a restrição invertida · para quem não é · o que precisa continuar impossível · o cemitério · a que obriga · mundos vizinhos · como termina · a escala em que quebra · a metade administrativa |
| **Molduras** (40, em 10 categorias) | subtração · inversão · troca de ator · troca de escala · troca de tempo · economia · manutenção · troca de meio · ritual · falha primeiro |
| **Clichês** | reflexos de pitch, adjetivos ocos e os padrões estruturais que denunciam um posicionamento em vez de um conceito |

### A sua parte nisso

Esta habilidade é uma conversa, não um comando. Quatro momentos decidem se a sessão vale alguma coisa, e os quatro são seus.

**1 · Responder às perguntas de premissa.** Não vão parecer levantamento de requisitos, porque não são. *"Quem é afetado por isto sem nunca ter escolhido usá-lo?"* não é uma pergunta sobre partes interessadas. As respostas úteis são aquelas em que você precisa pensar; as que começam com *"bem, obviamente…"* são exatamente a premissa que a sessão procura. Diga essa frase óbvia mesmo assim — é ela o material.

**2 · Assinar o contrato de proibições.** Depois de umas três perguntas, você vê cerca de seis respostas e o **esqueleto** que elas compartilham: a estrutura embaixo, não a redação — *um aparelho, um feed, um marketplace, um painel*. E então:

> "Estas são as respostas mais baratas aqui, então vou tirá-las da mesa. Quais delas você já estava imaginando, e o que acrescentaria?"

Responda às duas metades. Nomear a que você já tinha na cabeça não custa nada e costuma ser a frase mais útil da sessão. Acrescente suas exclusões no formato que vier — *"nada que aumente o tempo de tela ao lado do leito"* serve, mesmo que nenhum script consiga casar isso: o portão registra como verificação manual e não libera a especificação enquanto não houver resposta escrita.

**3 · A cadeira desconfortável.** Uma das três abordagens é deliberadamente a que se espera que você rejeite, e é defendida com o mesmo cuidado que as outras. Rejeite se estiver errada — mas diga *por quê*, em uma frase. Essa frase costuma deslocar o conceito mais do que escolher o vencedor.

**4 · O portão de revisão.** A especificação é escrita num arquivo e devolvida com um *"leia e me diga o que mudar"*. Não é formalidade. Os portões verificam se o trabalho foi feito, não se o conceito está certo — veja abaixo.

### As três coisas a dizer

**Quando todas as opções parecem iguais:**

```text
Continua sendo uma ideia com três fantasias. Regenere.
```

Ela redistribui a partir de uma rodada nova, acrescenta *todos os elementos da rodada anterior* ao contrato e apaga mais uma premissa da escavação — e diz qual foi. Essa última linha é o ponto.

**Quando a resposta convencional é de fato a certa:** diga isso. A habilidade é obrigada a concordar em uma frase, sair de si mesma e fazer o trabalho comum do lado de fora. Um formulário de login não precisa de escavação de premissas, e a habilidade está proibida de fingir o contrário.

**Quando o briefing é grande demais:** o reconhecimento deveria pegar isso, mas se não pegar — *"isto são três sistemas, separe"* — cada pedaço ganha a própria sessão e a própria especificação.

### Rodando os scripts à mão

Python 3.11, biblioteca padrão, nada a instalar. Os scripts ficam em `skills/imagination-brainstorming/scripts/`; escreva os arquivos de trabalho num diretório temporário, nunca dentro da pasta da habilidade.

```bash
# 1 · distribua as famílias de perguntas e três enquadramentos incompatíveis
python3 scripts/deal.py --brief "um jeito de passar o plantão na ala" --run 1 --out /tmp/work

# 2 · construa o contrato — duas vezes, e a ordem importa
python3 scripts/banlist.py --brief "<briefing>" --instincts instincts.txt \
    --skeleton "uma lista preenchida no fim do turno" --out /tmp/work
#    …mostre ao usuário, colha a resposta, e só então:
python3 scripts/banlist.py --brief "<briefing>" --instincts instincts.txt \
    --skeleton "uma lista preenchida no fim do turno" \
    --user exclusions.txt --confirmed --out /tmp/work

# 3 · prove que as três abordagens são mesmo três
python3 scripts/divergence_check.py --approaches /tmp/work/approaches.json --banlist /tmp/work/banlist.json

# 4 · leve especificação, sidecar e contrato juntos ao portão — os três são obrigatórios
python3 scripts/spec_gate.py --concept /tmp/work/concept.json \
    --markdown docs/concepts/2026-07-28-handover-concept.md --banlist /tmp/work/banlist.json
```

`--confirmed` registra um consentimento que já aconteceu. Ligá-lo antes de o usuário ter visto a lista é uma mentira da qual todo o resto do pipeline passa a depender, e o portão não tem como detectá-la — por isso são duas chamadas, e não um único sinalizador.

`cliche_lint.py` é para **rascunhos no meio da sessão**. Rodado sobre uma especificação pronta, ele aponta a própria seção de proibições do documento; quem revisa a especificação pronta é o `spec_gate.py`, que recorta esse trecho antes.

### Códigos de saída, e o que fazer com cada um

| Código | Significado | O conserto |
|---|---|---|
| `0` | passou | — |
| `1` | uso, arquivo ausente ou baralho malformado | é erro de digitação, não julgamento |
| `2` | **o contrato ou a especificação está incompleto** — poucos impulsos, sem esqueleto, contrato não assinado, seção faltando, verificação manual sem resposta escrita, ou uma especificação que não contém de verdade o próprio sidecar | faça o trabalho que falta |
| `3` | **as abordagens são variantes**, ou há material proibido | reescreva, ou redistribua com `--run 2` e construa de novo |

### O que os portões não conseguem verificar

> [!IMPORTANT]
> Eles são pisos. Provam que o trabalho foi **feito**, não que estava **certo**. Três coisas passam por todos os portões deste repositório:
>
> - **uma justificativa que inverte a própria evidência** — um argumento cuja premissa, lida com cuidado, sustenta a conclusão oposta;
> - **um mecanismo atacável nos próprios termos** — por exemplo, um número que muda conforme a ordem em que foi calculado, apresentado como a prova de transparência do conceito;
> - **três abordagens que na verdade são uma ideia** em três vocabulários. A checagem pega reformulação e causas de morte compartilhadas; ela não sabe ler.
>
> As três aconteceram durante a própria sessão de teste desta habilidade e as três foram pegas por uma pessoa, não por um script. Então: antes que a especificação chegue até você, peça a um segundo leitor que a ataque — outro modelo, um colega — e que argumente que **ela perde**, não que poderia melhorar. "Como deixar isso melhor" traz polimento. "Por que isso perde" traz a premissa invertida.
>
> A habilidade também roda em si mesma uma **auditoria da direção da evidência**: para cada *porque* que sustenta algo, ela precisa escrever a conclusão oposta que a mesma premissa sustentaria, e nomear o que a parte que decide consegue de fato observar. É esse passo que pega *"o avaliador é uma máquina, portanto nosso registro interno é o diferencial"* — uma máquina não consegue observar o registro interno, então essa premissa argumenta pelo contrário.

## O que ela não vai fazer

> [!IMPORTANT]
> - **Construir qualquer coisa.** Dois portões duros: nunca implementa; e nada chega até você sem checagem — as abordagens esperam a checagem de divergência, a spec espera o portão dela.
> - **Afirmar que ninguém jamais pensou nisso.** Inverificável, então é proibido. Ela nomeia as coisas existentes mais próximas e declara a diferença.
> - **Fabricar estranheza.** Quando a resposta convencional é a correta, a skill precisa dizer isso em uma frase, sair de si mesma e fazer o trabalho comum fora dela.
> - **Encolher seu pedido para facilitar a spec.** O escopo é decomposto abertamente, nunca estreitado em silêncio.
> - **Fingir que passar no portão significa boa ideia.** Prova que o trabalho foi feito, não que o conceito está certo. A skill diz isso na própria saída.

## Por dentro

| Script | Papel | Saída ≠ 0 |
|---|---|---|
| `deal.py` | Distribui famílias de perguntas e três molduras incompatíveis, uma marcada como incômoda | `1` erro de uso ou de baralho |
| `banlist.py` | Constrói o contrato de vetos: instintos + esqueleto + suas exclusões | `2` poucos instintos, ou sem esqueleto |
| `divergence_check.py` | Prova que as abordagens são alternativas, não uma proposta com dois figurantes | `3` não diverge |
| `spec_gate.py` | Valida a spec escrita, seu sidecar e o contrato juntos, fail-closed | `2` portão reprovado |
| `cliche_lint.py` | Confere qualquer rascunho no meio da sessão | `3` material proibido |

**Tudo é reproduzível.** A distribuição é semeada por um hash do briefing, então o mesmo briefing dá a mesma mão e qualquer sessão pode ser reproduzida. `--run 2` distribui molduras novas — ainda de categorias disjuntas — quando uma rodada de divergência se esgota, e a cadeira incômoda gira para que não seja sempre a mesma categoria a carregá-la.

```text
skills/imagination-brainstorming/
├── SKILL.md                    # o fluxo de trabalho autoritativo
├── references/
│   ├── concept-template.md     # a estrutura da spec e seus marcadores de seção
│   ├── worked-example.md       # uma sessão completa, inclusive o que foi cortado
│   ├── example-concept.md      # a spec que essa sessão produziu
│   ├── example-concept.json    # o sidecar dela — ambos passam nos portões e servem de fixture
│   └── decks/                  # famílias de perguntas · molduras · clichês · esquema da spec
└── scripts/                    # deal · banlist · divergence_check · spec_gate · cliche_lint
```

### Companheira

Independente de [**imagination-engine**](https://github.com/djfksjd/imagination-engine-skill), mas feita para ficar ao lado dela: aquela é o gerador de um único objeto estranho, em uma passada só. Esta repassa para lá quando uma criatura, um mecanismo ou um mundo dentro do conceito precisa ir muito além do que uma spec comporta. Nenhuma exige a outra.

## Testes

```bash
python3 -m pytest tests/ -q
```

Offline: integridade dos baralhos, determinismo da distribuição e disjunção de categorias, todos os caminhos de falha dos três portões, e o exemplo incluído passando por eles.

## Contribuindo

Os baralhos são o ponto mais fácil para ajudar — uma família de perguntas com um ângulo de ataque realmente diferente, ou uma moldura que nenhuma categoria existente cobre. Toda entrada precisa ser utilizável: uma família precisa do que escutar *e* da pergunta preservadora de premissas que ela substitui; uma moldura precisa de um movimento, um requisito e sua falha característica. Rode os testes antes de abrir um PR.

<div align="center">
<sub>Licença MIT · construído para <a href="https://claude.com/claude-code">Claude Code</a> e Codex</sub>
</div>
