<div align="center">

# ◇ Imagination Brainstorming

**Transforme uma ideia escolhida em um conceito capaz de enfrentar a realidade.**

[![Tests](https://github.com/djfksjd/imagination-brainstorming-skill/actions/workflows/tests.yml/badge.svg)](https://github.com/djfksjd/imagination-brainstorming-skill/actions/workflows/tests.yml)
![Versão](https://img.shields.io/badge/version-0.4.1-db2777)
![Preferência](https://img.shields.io/badge/blind_preference-83.3%25-16a34a)
![Licença](https://img.shields.io/badge/license-MIT-0f766e)

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

</div>

---

> [!TIP]
> Para a maioria dos usuários, recomendamos
> [Imagination](https://github.com/djfksjd/imagination): ele gera direções,
> espera sua escolha e encaminha a selecionada para este workshop.

Imagination Brainstorming começa **depois da escolha de uma direção**. Antes da
implementação, testa a ideia contra objetivo, restrições, melhor alternativa,
operação cotidiana e falha própria do mecanismo.

```text
Ideia escolhida → pré-teste de restrições → teste de pressão → conceito decisório
```

## Exemplo

```text
Use $imagination-brainstorming para desenvolver esta opção com primeiro uso
real, trabalho recorrente, falha própria, falseador e próxima decisão.
```

## Resultado medido

| Métrica | Contra um prompt forte |
|---|---:|
| Preferência para planejamento | **25–5 (83,3%)** |
| Aplicabilidade | **+1,37** |
| Aderência à decisão | **+0,59** |
| Clareza causal | **+0,59** |
| Robustez | **+0,53** |

É um resultado de juízes-modelo em teste cego pré-registrado, não uma garantia
universal.

## Instalação independente

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-brainstorming-skill/main/install.sh | bash
```

Para divergência inicial, use
[Imagination Engine](https://github.com/djfksjd/imagination-engine-skill).
O fluxo anterior existe apenas em `legacy/v0.3.0/`. Licença MIT.
