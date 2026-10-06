<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/imagination-octo-brainstorming-logo-dark.png" />
  <img src="assets/brand/imagination-octo-brainstorming-logo.png" alt="IMAGINATION OCTO BRAINSTORMING — Faire tenir une idée" width="380" />
</picture>

# IMAGINATION OCTO BRAINSTORMING

**MAKE ONE HOLD**

### La moitié convergente d'Imagination Octo —<br/>une direction choisie, mise à l'épreuve jusqu'à devenir un concept prêt pour la planification

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

[![Tests](https://img.shields.io/github/actions/workflow/status/djfksjd/imagination-octo-brainstorming/tests.yml?style=flat-square&label=tests)](https://github.com/djfksjd/imagination-octo-brainstorming/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-1f2937?style=flat-square)](LICENSE)
![Version](https://img.shields.io/badge/version-0.4.3-d69526?style=flat-square)
[![Family](https://img.shields.io/badge/part%20of-Imagination%20Octo-6d5ef5?style=flat-square)](https://github.com/djfksjd/imagination-octo)
![Hosts](https://img.shields.io/badge/hosts-Claude%20Code%20%C2%B7%20Codex-0ea5b7?style=flat-square)

</div>

Imagination Octo Brainstorming commence une fois la direction choisie. Il confronte cette seule idée à son objectif, à ses contraintes, à sa meilleure alternative classique, à l'exploitation quotidienne et à son propre mode de défaillance, puis renvoie un court mémo de concept. Si la direction enfreint le brief ou perd face à plus simple, il le dit au lieu de la polir.

> [!TIP]
> **La plupart des utilisateurs devraient installer [Imagination Octo](https://github.com/djfksjd/imagination-octo).** Il génère des directions avec le moteur, attend votre choix, puis transmet ce choix à cet atelier.

**Ceci est la `v0.4.3`, une version qui ne fait que renommer le runtime évalué en v0.4.2.** Les mesures ci-dessous proviennent d'une seule petite comparaison jugée par IA et ne prétendent pas que tout concept s'améliore. L'invocation implicite reste désactivée : appelez la skill par son nom.

## Ce qu'il fait

| | |
|---|---|
| **Contrôle préalable des contraintes** | Un mécanisme exclu revient-il sous un autre nom, un autre responsable, un autre lieu ou une autre échelle ? |
| **Hypothèse porteuse** | Quelle croyance unique ferait s'effondrer l'idée si elle était fausse ? |
| **Concurrent classique** | Pourquoi mérite-t-elle sa complexité supplémentaire face à la réponse ordinaire ? |
| **Mécanisme central** | Quelle cause observable change le résultat ? |
| **La moitié ennuyeuse** | Qui prend en charge le travail récurrent, les files d'attente, les exceptions et la maintenance ? |
| **Défaillance propre** | Comment le mécanisme qui définit l'idée échoue-t-il selon ses propres termes ? |
| **Réfutateur** | Quel résultat devrait amener l'équipe à s'arrêter ou à changer de direction ? |

## Fonctionnement

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

- Le contrôle préalable est proportionné. Une petite infraction reçoit la plus petite réparation, gardée provisoire, et non une réécriture de l'idée.
- Rien n'est implémenté. Le résultat est un mémo de concept, pas du code, un échafaudage ni un plan d'implémentation.
- À l'exécution, un seul fichier Markdown est chargé : ni cadres distribués, ni contrats d'interdiction, ni fichiers JSON annexes, ni barrières de qualité.

## Essayer

```text
Utilise $imagination-octo-brainstorming pour développer cette direction choisie. Montre
le premier usage réel, la charge opérationnelle récurrente, le mode de défaillance propre,
le réfutateur et la prochaine décision que nous devons prendre.
```

La réponse est un mémo de concept qui se termine sur la prochaine décision, puis s'arrête.

## Mesures

v0.4.2 face à un prompt simple solide, préenregistré et à l'aveugle : 10 briefs inédits en anglais et en coréen avec une direction déjà choisie, 5 exécutions chacun, 5 juges (2026-07-30).

| Mesure | Atelier moins prompt simple |
|---|---:|
| Préféré pour planifier | **45–5 (90%)** |
| Caractère actionnable | **+1,37** |
| Adéquation à la décision | **+0,95** |
| Robustesse | **+0,82** |
| Clarté causale | **+0,71** |
| Tokens | `1,14×` |

À lire honnêtement :

- **Un seul modèle a généré et jugé.** Uniquement `gpt-5.4`, avec des juges de la même famille. L'intervalle de Wilson à 95 % pour la préférence est de 78,6–95,7 % ; la borne inférieure n'établit donc pas un taux de 90 %.
- **Il peut perdre.** Neuf briefs sont allés à l'atelier à l'unanimité, et un est allé au prompt simple à l'unanimité.
- **Non mesuré avec Claude ni par des personnes.** Les expériences entre modèles du dépôt Octo ([A](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-a.md), [B](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-b.md)) n'ont testé que le moteur. Rien ici ne dit comment l'atelier se comporte avec d'autres modèles.
- **Une conception antérieure a été remplacée.** Le flux à cartes et barrières (v0.3.0), avec cadres distribués, contrats d'interdiction et barrières de qualité mécaniques, est conservé dans [`legacy/v0.3.0/`](legacy/v0.3.0/) à titre d'archive et n'est jamais chargé.

Protocole, règle de décision et résultats figés : [`evals/`](evals/README.md).

## Quand l'utiliser, et quand s'en passer

**À utiliser** quand une direction, une favorite de la liste restreinte ou un concept brut existe déjà et que vous devez savoir s'il tient avant de planifier.

**Utilisez autre chose** pour les premières idées ou pour l'implémentation. Pour les premières idées, utilisez [Imagination Octo Engine](https://github.com/djfksjd/imagination-octo-engine). L'atelier s'arrête volontairement avant l'implémentation.

## Anciennement `imagination-brainstorming`

Jusqu'à la v0.4.2, ce dépôt s'appelait `imagination-brainstorming-skill` et la skill `$imagination-brainstorming`. GitHub redirige l'ancienne URL, mais le plugin, l'identifiant du marketplace et la commande ont changé : installez `imagination-octo-brainstorming@imagination-octo-brainstorming` et appelez `$imagination-octo-brainstorming`. Les instructions du runtime sont par ailleurs inchangées.

## Installation autonome

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-octo-brainstorming/main/install.sh | bash
```

Pour mettre à jour, relancez la même commande. Si elle signale d'anciennes copies de ces skills installées séparément, terminez la commande par `| bash -s -- --clean-legacy` pour les mettre de côté ; rien n'est supprimé.

```bash
# Claude Code
claude plugin marketplace add djfksjd/imagination-octo-brainstorming
claude plugin install imagination-octo-brainstorming@imagination-octo-brainstorming

# Codex
codex plugin marketplace add djfksjd/imagination-octo-brainstorming
codex plugin add imagination-octo-brainstorming@imagination-octo-brainstorming
```

## Développement

```bash
python3 -m pytest tests/ -q
python3 evals/harness.py --help
bash -n install.sh
```

## Licence

[MIT](LICENSE).
