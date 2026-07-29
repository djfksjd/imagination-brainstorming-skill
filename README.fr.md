<div align="center">

# ◇ Imagination Brainstorming

**Transformer une idée choisie en concept capable d’affronter le réel.**

[![Tests](https://github.com/djfksjd/imagination-brainstorming-skill/actions/workflows/tests.yml/badge.svg)](https://github.com/djfksjd/imagination-brainstorming-skill/actions/workflows/tests.yml)
![Version](https://img.shields.io/badge/version-0.4.2-db2777)
![Préférence](https://img.shields.io/badge/blind_preference-90.0%25-16a34a)
![Licence](https://img.shields.io/badge/license-MIT-0f766e)

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

</div>

---

> [!TIP]
> Pour la plupart des usages, installez
> [Imagination](https://github.com/djfksjd/imagination) : il génère les options,
> attend votre choix, puis transmet l’idée retenue à cet atelier.

Imagination Brainstorming commence **après le choix d’une direction**. Avant
l’implémentation, il confronte l’idée à son objectif, ses contraintes, sa
meilleure alternative, son fonctionnement courant et son échec propre.

```text
Idée choisie → contrôle des contraintes → mise à l’épreuve → concept décisionnel
```

## Exemple

```text
Utilise $imagination-brainstorming pour développer cette option avec le premier
usage réel, le travail récurrent, l’échec propre, le falsificateur et la prochaine décision.
```

## Résultat mesuré

| Mesure | Face à un prompt fort |
|---|---:|
| Préférence pour la planification | **45–5 (90,0 %)** |
| Applicabilité | **+1,37** |
| Adéquation décisionnelle | **+0,95** |
| Clarté causale | **+0,71** |
| Robustesse | **+0,82** |

Résultat de juges modèles dans un test aveugle préenregistré, sans garantie
universelle.

## Installation autonome

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-brainstorming-skill/main/install.sh | bash
```

Pour la divergence initiale, utilisez
[Imagination Engine](https://github.com/djfksjd/imagination-engine-skill).
L’ancien flux reste uniquement dans `legacy/v0.3.0/`. Licence MIT.
