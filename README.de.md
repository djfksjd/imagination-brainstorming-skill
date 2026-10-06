<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/imagination-octo-brainstorming-logo-dark.png" />
  <img src="assets/brand/imagination-octo-brainstorming-logo.png" alt="IMAGINATION OCTO BRAINSTORMING — Eine Idee, die trägt" width="380" />
</picture>

# IMAGINATION OCTO BRAINSTORMING

**MAKE ONE HOLD**

### Die konvergente Hälfte von Imagination Octo —<br/>eine gewählte Richtung, unter Druck geprüft, bis ein planungsreifes Konzept daraus wird

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

[![Tests](https://img.shields.io/github/actions/workflow/status/djfksjd/imagination-octo-brainstorming/tests.yml?style=flat-square&label=tests)](https://github.com/djfksjd/imagination-octo-brainstorming/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-1f2937?style=flat-square)](LICENSE)
![Version](https://img.shields.io/badge/version-0.4.3-d69526?style=flat-square)
[![Family](https://img.shields.io/badge/part%20of-Imagination%20Octo-6d5ef5?style=flat-square)](https://github.com/djfksjd/imagination-octo)
![Hosts](https://img.shields.io/badge/hosts-Claude%20Code%20%C2%B7%20Codex-0ea5b7?style=flat-square)

</div>

Imagination Octo Brainstorming beginnt, nachdem eine Richtung gewählt wurde. Es prüft diese eine Idee gegen ihr Ziel, ihre Vorgaben, ihre stärkste gewöhnliche Alternative, den Alltagsbetrieb und ihre eigene Art zu scheitern und liefert ein kurzes Konzeptmemo. Verstößt die Richtung gegen das Briefing oder unterliegt sie etwas Einfacherem, sagt es das, statt sie aufzupolieren.

> [!TIP]
> **Die meisten sollten [Imagination Octo](https://github.com/djfksjd/imagination-octo) installieren.** Es erzeugt Richtungen mit der Engine, wartet auf deine Wahl und gibt diese Wahl an diesen Workshop weiter.

**Dies ist `v0.4.3`, eine reine Umbenennung der als v0.4.2 evaluierten Runtime.** Die Messwerte unten stammen aus einem einzigen kleinen, von KI bewerteten Vergleich und behaupten nicht, dass jedes Konzept besser wird. Der implizite Aufruf bleibt aus: Rufe den Skill mit seinem Namen auf.

## Was es tut

| | |
|---|---|
| **Vorgaben-Vorprüfung** | Kehrt ein ausgeschlossener Mechanismus unter anderem Namen, Verantwortlichen, Ort oder Maßstab zurück? |
| **Tragende Annahme** | Welche einzelne Überzeugung brächte die Idee zum Einsturz, wenn sie falsch wäre? |
| **Gewöhnlicher Konkurrent** | Warum verdient sie ihre zusätzliche Komplexität gegenüber der üblichen Antwort? |
| **Kernmechanismus** | Welche beobachtbare Ursache verändert das Ergebnis? |
| **Die langweilige Hälfte** | Wer übernimmt wiederkehrende Arbeit, Warteschlangen, Ausnahmen und Wartung? |
| **Eigenes Scheitern** | Wie scheitert der prägende Mechanismus aus sich selbst heraus? |
| **Falsifikator** | Welches Ergebnis sollte das Team zum Stoppen oder Umsteuern bringen? |

## So funktioniert es

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

- Die Vorprüfung ist verhältnismäßig. Ein kleiner Verstoß bekommt die kleinste Reparatur, die vorläufig bleibt, und keine Neufassung der Idee.
- Es wird nichts implementiert. Das Ergebnis ist ein Konzeptmemo, kein Code, kein Gerüst und kein Umsetzungsplan.
- Zur Laufzeit wird nur eine Markdown-Datei geladen: keine ausgeteilten Frames, keine Verbotsverträge, keine JSON-Begleitdateien, keine Qualitäts-Gates.

## Ausprobieren

```text
Nutze $imagination-octo-brainstorming, um diese gewählte Richtung auszuarbeiten. Zeige
die erste echte Nutzung, den wiederkehrenden Betriebsaufwand, die eigene Art zu scheitern,
den Falsifikator und die nächste Entscheidung, die wir treffen müssen.
```

Die Antwort ist ein Konzeptmemo, das mit der nächsten Entscheidung endet und dann stoppt.

## Messwerte

v0.4.2 gegen einen starken einfachen Prompt, präregistriert und verblindet: 10 neue englische und koreanische Briefings mit bereits gewählter Richtung, je 5 Läufe, 5 Bewerter (2026-07-30).

| Kennzahl | Workshop minus einfacher Prompt |
|---|---:|
| Für die Planung bevorzugt | **45–5 (90%)** |
| Umsetzbarkeit | **+1,37** |
| Passung zur Entscheidung | **+0,95** |
| Robustheit | **+0,82** |
| Kausale Klarheit | **+0,71** |
| Tokens | `1,14×` |

Ehrlich gelesen:

- **Ein einziges Modell hat erzeugt und bewertet.** Nur `gpt-5.4`, mit Bewertern aus derselben Familie. Das 95-%-Wilson-Intervall der Präferenz liegt bei 78,6–95,7 %; die Untergrenze belegt also keine Quote von 90 %.
- **Er kann verlieren.** Neun Briefings gingen einstimmig an den Workshop, eines ging einstimmig an den einfachen Prompt.
- **Weder mit Claude noch von Menschen gemessen.** Die modellübergreifenden Experimente im Octo-Repository ([A](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-a.md), [B](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-b.md)) haben nur die Engine getestet. Daraus folgt nichts darüber, wie sich der Workshop mit anderen Modellen verhält.
- **Ein früherer Entwurf wurde ersetzt.** Der Deck-und-Gate-Workflow (v0.3.0) mit ausgeteilten Frames, Verbotsverträgen und mechanischen Qualitäts-Gates liegt als Protokoll unter [`legacy/v0.3.0/`](legacy/v0.3.0/) und wird nie geladen.

Protokoll, Entscheidungsregel und eingefrorene Ergebnisse: [`evals/`](evals/README.md).

## Wann einsetzen, wann nicht

**Nutze ihn**, wenn es bereits eine Richtung, einen Favoriten der engeren Auswahl oder ein Rohkonzept gibt und du vor der Planung wissen musst, ob es trägt.

**Nutze etwas anderes** für erste Ideen oder für die Umsetzung. Für erste Ideen gibt es [Imagination Octo Engine](https://github.com/djfksjd/imagination-octo-engine). Der Workshop stoppt bewusst vor der Umsetzung.

## Umbenannt von `imagination-brainstorming`

Bis v0.4.2 hieß dieses Repository `imagination-brainstorming-skill` und der Skill `$imagination-brainstorming`. GitHub leitet die alte URL weiter, aber Plugin, Marketplace-ID und Befehl haben sich geändert: Installiere `imagination-octo-brainstorming@imagination-octo-brainstorming` und rufe `$imagination-octo-brainstorming` auf. Die Anweisungen der Runtime sind ansonsten unverändert.

## Einzelinstallation

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-octo-brainstorming/main/install.sh | bash
```

Zum Aktualisieren denselben Befehl erneut ausführen. Meldet er ältere, einzeln installierte Kopien dieser Skills, den Befehl mit `| bash -s -- --clean-legacy` beenden, um sie beiseitezulegen; gelöscht wird nichts.

```bash
# Claude Code
claude plugin marketplace add djfksjd/imagination-octo-brainstorming
claude plugin install imagination-octo-brainstorming@imagination-octo-brainstorming

# Codex
codex plugin marketplace add djfksjd/imagination-octo-brainstorming
codex plugin add imagination-octo-brainstorming@imagination-octo-brainstorming
```

## Entwicklung

```bash
python3 -m pytest tests/ -q
python3 evals/harness.py --help
bash -n install.sh
```

## Lizenz

[MIT](LICENSE).
