<div align="center">

# Imagination Brainstorming

**Ideenentwicklung, die sich weigert, aufs Naheliegende zuzulaufen.**

Ein Agenten-Skill, der die Form guten Brainstormings behält — eine Frage nach der anderen, echte Alternativen,<br>eine geschriebene Spezifikation — und die Teile ersetzt, die alles still zur sicheren Antwort zurücklenken.

[![tests](https://github.com/djfksjd/imagination-brainstorming-skill/actions/workflows/tests.yml/badge.svg)](https://github.com/djfksjd/imagination-brainstorming-skill/actions/workflows/tests.yml)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-D97757)](#installation)
[![Codex](https://img.shields.io/badge/Codex-plugin-1f2328)](#installation)
[![Python](https://img.shields.io/badge/python-3.11%2B_nur_stdlib-3776AB)](#unter-der-haube)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · **Deutsch** · [Português](README.pt-BR.md)

</div>

---

> Brainstorming konvergiert zu früh — und nicht, weil zu wenig gefragt wurde. Der Fehler ist, dass die Fragen aus derselben Verteilung stammen wie die Antworten: *wer ist die Nutzerin, was sind die Einschränkungen, wie sieht Erfolg aus* verfeinern nur die Idee, die man ohnehin schon hat. Keine davon rührt an das, was der Auftrag voraussetzt.
>
> Dann kommen drei Optionen — zwei davon existieren nur, damit die dritte vernünftig aussieht.

## Funktionsweise

```mermaid
flowchart LR
    A["Deine rohe Idee"] --> B["<b>1 · Ausgraben</b><br/>Fragen, die Prämissen<br/>angreifen, eine pro Nachricht"]
    B --> C["<b>2 · Vertrag</b><br/>die 12 billigsten Antworten<br/>+ ihr gemeinsames Skelett,<br/><i>mit dir</i> unterschrieben"]
    C --> D["<b>3 · Divergieren</b><br/>3 Ansätze aus disjunkten<br/>Rahmen, einer auf dem<br/>unbequemen Platz"]
    D --> E{"Divergenz-<br/>prüfung"}
    E -- "Varianten" --> D
    E -- "Alternativen" --> F["<b>4 · Konvergieren</b><br/>was es verbietet ·<br/>die langweilige Hälfte"]
    F --> G{"Spec-<br/>Gate"}
    G -- "Arbeit übersprungen" --> F
    G -- "bestanden" --> H["Konzept-Spec<br/>→ deine Durchsicht<br/>→ Übergabe"]
```

|  | Was passiert | Warum es wirkt |
|---|---|---|
| **1** | **Fragen, die Prämissen angreifen.** Ausgeteilt aus zwölf Frage-Familien — die unausgesprochene Prämisse, die Fassung, die du hassen würdest, für wen das *nicht* ist, wie es endet, bei welcher Größenordnung es bricht, die administrative Hälfte. Jede Familie nennt, worauf zu hören ist, und welche prämissenerhaltende Frage zu vermeiden ist. | Anforderungen sitzen auf Prämissen. Nach Anforderungen zu fragen bestätigt die Idee; nach Prämissen zu fragen prüft sie. Mindestens eine Prämisse muss gestrichen oder umgedreht werden — fällt nur eine, muss die Spec sagen, warum die anderen hielten. Eine zweite Umkehrung zu erfinden, um eine Quote zu erfüllen, ist schlimmer als ein ehrliches „sie hat gehalten". |
| **2** | **Ein Verbotsvertrag, den auch du unterschreibst.** Das Modell schreibt die zwölf Antworten auf, die es am wahrscheinlichsten gäbe, benennt das *Skelett*, das sie teilen, und zeigt dir eine gekürzte Fassung — als Ausschlüsse, nie als Vorschläge. Du ergänzt dein eigenes „nicht schon wieder ein X". | Deine Ausschlüsse sind die wertvollste Einschränkung im Raum, und das benannte Skelett verhindert, dass die dreizehnte Fassung derselben Form durchrutscht. |
| **3** | **Alternativen, die keine Varianten sein können.** Drei Ansätze aus disjunkten Umdeutungs-Kategorien, einer davon auf dem **unbequemen Platz** — die Option, die du vermutlich ablehnst, mit voller Kraft vertreten. | Ein Skript prüft es: gleiche Kategorie, identische oder sich wiederholende Zusammenfassungen, zwei mit derselben Todesursache, oder einer deutlich dünner beschrieben — alles scheitert mit Exit 3. Es prüft Struktur, nicht Bedeutung — aber genau diese Formen muss eine Attrappe annehmen. |
| **4** | **Ein Gate, bevor du überhaupt etwas lesen sollst.** Das Konzept muss sagen, was es verbietet, seine nächsten existierenden Nachbarn benennen und mindestens zwei echte offene Fragen tragen. | Eine Spec ohne offene Fragen hat ihre Unbekannten versteckt. Ein Entwurf, der nichts verbietet, ist ein Wunschzettel. Das Gate kann kein Konzept beurteilen — es beweist, dass die Arbeit nicht übersprungen wurde. |

> [!IMPORTANT]
> **Es implementiert nie.** Kein Code, kein Gerüst, kein „soll ich anfangen zu bauen?". Der Endzustand ist eine von dir freigegebene Spec plus eine Übergabe.

## Installation

Läuft in **Claude Code** und **Codex**. Nur Python-3-Standardbibliothek: nichts zu installieren, kein API-Schlüssel, kein Netzzugriff.

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-brainstorming-skill/main/install.sh | bash
```

<details>
<summary><b>Manuelle Installation</b></summary>

```bash
# Claude Code
claude plugin marketplace add djfksjd/imagination-brainstorming-skill
claude plugin install imagination-brainstorming@djfksjd

# Codex
codex plugin marketplace add djfksjd/imagination-brainstorming-skill
codex plugin add imagination-brainstorming@djfksjd
```

Ein Baum bedient beide Hosts: der Skill-Körper liegt unter `skills/imagination-brainstorming/`, und `AGENTS.md` wird als gemeinsamer Kontext geladen.
</details>

## Verwendung

Sag einfach, was dir im Kopf herumgeht. Der Skill greift bei Brainstorming-Anfragen und bei der Klage, alle bisherigen Optionen fühlten sich gleich an. Funktioniert in jeder Sprache; die Spec wird in deiner geschrieben.

```text
Denk das mit mir durch: wie die Station die Schichtübergabe macht.
```

```text
Ich habe drei Ideen für das Onboarding und alle fühlen sich wie dieselbe an.
Bohr richtig nach, bevor ich mich festlege.
```

### Was eine Sitzung tatsächlich tut

| Phase | Was du siehst | Wodurch erzwungen |
|---|---|---|
| Erkundung | „Hier gibt es eine konventionelle Antwort, und sie könnte die richtige sein — willst du die, oder prüfen wir erst die ganze Form?" | Harte Regel: keine fabrizierte Fremdheit |
| Ausgrabung | Eine Frage pro Nachricht, formuliert für deinen Auftrag | 12 Frage-Familien, jede mit ihrem Antipattern |
| Vertrag | Sechs Ausschlüsse + das gemeinsame Skelett, zum Bestätigen und Ergänzen | `banlist.py`, Exit 2 wenn vorgetäuscht |
| Divergenz | Drei Ansätze in gleicher Ausführlichkeit, einer, den du wahrscheinlich hasst | `divergence_check.py`, Exit 3 bei Varianten |
| Konvergenz | Abschnittsweiser Entwurf, jeder freigegeben vor dem nächsten | Was es verbietet, wird zuerst geschrieben |
| Spec | `docs/concepts/JJJJ-MM-TT-<thema>-concept.md` + ein maschinenlesbares Sidecar | `spec_gate.py`, Exit 2 bei übersprungener Arbeit |
| Übergabe | Was diese Spec *nicht* abdeckt und was als Nächstes kommt | Niemals ein Implementierungs-Skill |

### Die Decks

| Deck | Inhalt |
|---|---|
| **Frage-Familien** (12) | unausgesprochene Prämisse · die Fassung, die du hasst · neu definierter Erfolg · umgedrehte Einschränkung · für wen es nicht ist · was unmöglich bleiben muss · der Friedhof · wozu es verpflichtet · benachbarte Welten · wie es endet · die Skala, bei der es bricht · die administrative Hälfte |
| **Rahmen** (40 in 10 Kategorien) | Subtraktion · Umkehrung · Akteurswechsel · Maßstabswechsel · Zeitwechsel · Ökonomie · Instandhaltung · Medienwechsel · Ritual · Scheitern zuerst |
| **Klischees** | Pitch-Reflexe, hohle Adjektive und die Satzmuster, die eine Positionierung statt eines Konzepts verraten |

### Ihr Anteil daran

Diese Fähigkeit ist ein Gespräch, kein Befehl. Vier Momente entscheiden, ob die Sitzung etwas taugt, und alle vier gehören Ihnen.

**1 · Die Prämissenfragen beantworten.** Sie werden sich nicht wie eine Anforderungserhebung anfühlen, denn sie sind keine. *„Wer ist davon betroffen, ohne je gewählt zu haben, es zu benutzen?"* ist keine Stakeholder-Frage. Nützlich sind die Antworten, über die Sie nachdenken müssen; die, die mit *„na ja, offensichtlich…"* beginnen, sind genau die Prämisse, die die Sitzung sucht. Sagen Sie den offensichtlichen Satz trotzdem — er ist das Material.

**2 · Den Verbotsvertrag unterschreiben.** Nach etwa drei Fragen sehen Sie sechs Antworten und das **Skelett**, das sie teilen: die Struktur darunter, nicht die Formulierung — *ein Apparat, ein Feed, ein Marktplatz, ein Dashboard*. Dann werden Sie gefragt:

> „Das sind die billigsten Antworten hier, ich nehme sie vom Tisch. Welche davon hatten Sie schon im Kopf, und was würden Sie ergänzen?"

Beantworten Sie beide Hälften. Die zu nennen, die Sie ohnehin vor sich sahen, kostet nichts und ist oft der nützlichste Satz der Sitzung. Ihre eigenen Ausschlüsse dürfen in jeder Form kommen — *„nichts, was die Bildschirmzeit am Bett erhöht"* ist völlig in Ordnung, auch wenn kein Skript das abgleichen kann: Das Gatter legt es als manuelle Prüfung ab und lässt die Spezifikation erst durch, wenn dafür eine schriftliche Antwort vorliegt.

**3 · Der unbequeme Platz.** Einer der drei Ansätze ist absichtlich der, den Sie voraussichtlich ablehnen, und er wird mit derselben Sorgfalt vertreten wie die anderen. Lehnen Sie ihn ab, wenn er falsch ist — aber sagen Sie *warum*, in einem Satz. Dieser Satz verschiebt das Konzept meist mehr als die Wahl des Siegers.

**4 · Das Prüf-Gatter.** Die Spezifikation wird in eine Datei geschrieben und mit einem *„bitte lies sie und sag mir, was zu ändern ist"* zurückgegeben. Das ist keine Formalie. Die Gatter prüfen, dass die Arbeit getan wurde, nicht dass das Konzept richtig ist — siehe unten.

### Die drei Sätze, die zählen

**Wenn sich alle Optionen gleich anfühlen:**

```text
Das ist immer noch eine Idee in drei Kostümen. Regeneriere.
```

Sie teilt aus einem neuen Zug neu aus, nimmt *jedes Element der vorigen Runde* in den Vertrag auf und löscht eine weitere Prämisse aus der Ausgrabung — und sagt Ihnen, welche. Diese letzte Zeile ist der Punkt.

**Wenn die konventionelle Antwort tatsächlich richtig ist:** sagen Sie es. Die Fähigkeit muss in einem Satz zustimmen, sich selbst verlassen und die gewöhnliche Arbeit außerhalb erledigen. Ein Login-Formular braucht keine Prämissenausgrabung, und der Fähigkeit ist verboten, etwas anderes vorzugeben.

**Wenn das Briefing zu groß ist:** die Erkundung sollte das fangen, aber falls nicht — *„das sind drei Systeme, trenn sie"* — bekommt jedes Stück seine eigene Sitzung und seine eigene Spezifikation.

### Die Skripte selbst fahren

Python 3.11, Standardbibliothek, nichts zu installieren. Die Fähigkeit liegt in `skills/imagination-brainstorming/`, und alle folgenden Befehle sind so geschrieben, dass sie aus diesem Verzeichnis heraus laufen. Schreiben Sie Arbeitsdateien in ein Scratch-Verzeichnis, nie in den Ordner der Fähigkeit.

```bash
cd skills/imagination-brainstorming
SKELETON="A capture tool that turns a spoken conversation into a structured record, with completeness enforced by a form and a signature at the end."

# 1 · Fragefamilien und drei unvereinbare Rahmen austeilen
python3 scripts/deal.py --brief "a way for our ward to hand over shifts" --run 1 --out /tmp/work

# 2 · den Vertrag bauen — zweimal, und die Reihenfolge zählt. --instincts ist eine
#     Datei, die Sie selbst schreiben: eine naheliegende Antwort pro Zeile, zwölf Stück.
python3 scripts/banlist.py --brief "a way for our ward to hand over shifts" \
    --instincts references/example-instincts.txt --skeleton "$SKELETON" --out /tmp/work
#    …dem Nutzer als Ausschlussliste zeigen, seine Antwort einholen, und erst dann:
python3 scripts/banlist.py --brief "a way for our ward to hand over shifts" \
    --instincts references/example-instincts.txt --user references/example-exclusions.txt \
    --skeleton "$SKELETON" --confirmed --out /tmp/work

# 3 · beweisen, dass die drei Ansätze wirklich drei sind
python3 scripts/divergence_check.py --approaches references/example-approaches.json \
    --banlist references/example-banlist.json

# 4 · Spezifikation, Sidecar und Vertrag gemeinsam durchs Gatter — alle drei sind Pflicht
python3 scripts/spec_gate.py --concept references/example-concept.json \
    --markdown references/example-concept.md --banlist references/example-banlist.json
```

Jede dort genannte Datei liegt dem Repository bei, der Block läuft also genau so, und alle vier Schritte enden mit `0`; Schritt 2 erzeugt `references/example-banlist.json` exakt wieder. Tauschen Sie sie im Verlauf gegen die Ihrer eigenen Sitzung.

**`approaches.json` schreiben Sie von Hand.** `deal.py` teilt die Rahmen aus; pro ausgeteiltem Rahmen schreiben Sie einen Ansatz in ein Objekt mit dem Schlüssel `approaches` — eine `id`, eine `frame_id` aus dem Rahmendeck, ein `summary` von mindestens 96 Einheiten, ein `failure_mode` von mindestens 48, das sagt, wie *dieser* Ansatz in *diesem* Auftrag scheitert, ein `frame_fit` von mindestens 40, das sagt, was in diesem Auftrag die vom Rahmen geforderte Stelle ausfüllt, und `unsafe_seat` bei genau einem auf true. `references/decks/approaches-schema.json` dokumentiert jedes Feld und jeden Boden, den die Prüfung anlegt; `references/example-approaches.json` ist eine bestehende Datei, deren Form Sie übernehmen können.

An `frame_fit` wird sichtbar, wenn ein Rahmen den Auftrag nicht trägt. `designed-for-repair` — *nimm an, es geht oft kaputt; nenne das Reparaturverfahren und die Ersatzteile* — landete einmal auf dem unbequemen Platz für einen einmaligen Schließungsritus, der genau einmal stattfindet und weder Hersteller noch Ersatzteile kennt, und der Satz kam trotzdem durch. Wenn nichts im Auftrag die vom Rahmen genannte Stelle ausfüllen kann, schreiben Sie das hin und teilen mit `--run 2` neu aus, statt es zu begründen. Die Prüfung verlangt die Behauptung; ob sie stimmt, kann sie nicht prüfen.

`--confirmed` protokolliert eine Zustimmung, die bereits stattgefunden hat. Sie zu setzen, bevor der Nutzer die Liste gesehen hat, ist eine Lüge, auf die sich die restliche Kette dann stützt, und das Gatter kann sie nicht erkennen — deshalb zwei Aufrufe statt eines Schalters.

Den Vertrag auszutauschen ist nicht umsonst — unmöglich ist es aber auch nicht: nichts hier belegt eine Herkunft. Das Gatter baut ihn aus dem wieder auf, was `concept.json` erklärt, und weist jede Datei ab, der einer der verbrannten Reflexe, einer der eigenen Ausschlüsse des Nutzers oder ein Eintrag des mitgelieferten Klischeedecks fehlt; beide Dateien müssen dasselbe Skelett und denselben Auftrag zeichengenau führen, und der Auftrag der Bannliste muss einen Gegenstand nennen und nicht ein Wort. Dieses Deck wird gegen die Spezifikation angelegt, welcher Vertrag auch kommt — eine kürzere Datei bedeutet nie einen kürzeren Lint. Was das alles belegt, ist die Übereinstimmung zweier Dateien derselben Hand: einen Vertrag auszutauschen heißt, ihn neu zu schreiben, nicht ihn umzubenennen.

`cliche_lint.py` ist für **Entwürfe mitten in der Sitzung**. Auf eine fertige Spezifikation angewandt, markiert es deren eigenen Verbotslisten-Abschnitt; die fertige Spezifikation prüft `spec_gate.py`, und das schneidet diesen Abschnitt vorher heraus.

### Exit-Codes und was jeweils zu tun ist

| Code | Bedeutung | Der Fix |
|---|---|---|
| `0` | bestanden | — |
| `1` | Aufruf, fehlende Datei oder fehlerhaftes Deck | ein Tippfehler, kein Urteil |
| `2` | **Vertrag oder Spezifikation unvollständig** — zu wenige Reflexe, kein Skelett, unbestätigter Vertrag, fehlender Abschnitt, manuelle Prüfung ohne schriftliche Antwort, oder eine Spezifikation, die ihr eigenes Sidecar nicht wirklich enthält | die fehlende Arbeit nachholen |
| `3` | **die Ansätze sind Varianten**, oder verbotenes Material ist vorhanden | neu schreiben, oder mit `--run 2` neu austeilen und neu bauen |

### Was die Gatter nicht prüfen können

> [!IMPORTANT]
> Sie sind Böden. Sie prüfen, ob die verlangte Arbeit **da ist**, nicht ob sie **richtig** war. Drei Dinge passieren jedes Gatter in diesem Repository:
>
> - **eine Begründung, die ihre eigene Evidenz umdreht** — ein Argument, dessen Prämisse bei genauem Lesen die entgegengesetzte Schlussfolgerung stützt;
> - **ein Mechanismus, der mit den eigenen Mitteln angreifbar ist** — etwa eine Zahl, die sich mit der Reihenfolge der Berechnung ändert, präsentiert als Transparenzbeweis des Konzepts;
> - **drei Ansätze, die in Wahrheit eine Idee sind**, in drei Vokabularen. Die Prüfung fängt Umformulierung und gemeinsame Todesursachen; lesen kann sie nicht.
>
> Zwei weitere verlangt das Gatter jetzt, ohne über eines davon zu urteilen: der Fehlermodus, den der gewählte Ansatz selbst aufgeschrieben hat, muss in `chosen.answers_failure_mode` **beantwortet** sein — ein Konzept, das seinen eigenen Zusammenbruch erklärte und weiterging, kam zuvor im ersten Anlauf durch — und jeder Ansatz muss sagen, was im Auftrag seinen Rahmen ausfüllt. In beiden Fällen prüft das Gatter, dass etwas geschrieben wurde, und legt es Ihnen vor; ob die Antwort taugt, kann es nicht sagen.
>
> Eine vierte kam durch und kommt nicht mehr durch: dieselben Worte, zitiert in einem Satz, der sie zurückweist. Das Verbot, das Unmöglichgewordene, die Erstkontakt-Szene und jede offene Frage werden jetzt mit `<!-- bind: … -->` markiert und **exakt** mit dem Sidecar verglichen — je einmal, im eigenen Abschnitt, als schlichte Prosa. Der ersetzte Ähnlichkeitswert konnte *„wir verbieten X"* nicht von *„wir haben erwogen, X zu verbieten, erlauben es aber"* unterscheiden. Und weder dieses Gatter noch die Divergenzprüfung nehmen noch `--allow`: Eine zur Urteilszeit gewährte Ausnahme gewährt die Partei, um die es im Urteil geht.
>
> Alle drei traten im eigenen Probelauf dieser Fähigkeit auf, und alle drei fand ein Mensch, kein Skript. Also: bevor die Spezifikation bei Ihnen ankommt, lassen Sie sie von einem zweiten Leser angreifen — ein anderes Modell, eine Kollegin — mit der Aufgabe zu begründen, dass **sie verliert**, nicht dass sie besser werden könnte. „Wie macht man das besser" bringt Politur. „Warum verliert das" bringt die umgedrehte Prämisse.
>
> Die Fähigkeit führt auch an sich selbst eine **Beweisrichtungs-Prüfung** durch: Zu jedem tragenden *weil* muss sie die entgegengesetzte Schlussfolgerung notieren, die dieselbe Prämisse stützen würde, und benennen, was die entscheidende Instanz tatsächlich beobachten kann. Das ist der Schritt, der *„die Jury ist eine Maschine, also ist unser internes Protokoll das Unterscheidungsmerkmal"* fängt — eine Maschine kann das interne Protokoll nicht beobachten, also spricht diese Prämisse für das Gegenteil.

### Aufträge, die keine Produkte sind

Der Ablauf, die Fragenfamilien, die Rahmen und der Spezifikationsvertrag gelten für jeden Gegenstand — eine Erzählwelt, eine Spielmechanik, einen Ritus, eine Kampagne, ein Format. Zwei Teile der Mechanik sind enger als das, und man sollte wissen, welche:

- **Die Klischee-Phrasenliste ist Pitch- und Produktvokabular** — one-stop shop, KPI-Dashboard, das Uber für X, Gamification. Auf einem erzählerischen oder rituellen Auftrag wird davon kaum etwas jemals auslösen. Das heißt: die maschinell prüfbare Hälfte des Vertrags tut dort wenig, und das Gewicht tragen die Reflexe und das Skelett dieser Sitzung selbst. Die hohlen Adjektive und die verbotenen Züge gelten überall weiter.
- **Ein verbotenes Adjektiv kann gewöhnliches Vokabular sein.** In der Fiktion bezeichnen *magical* und *delightful*, statt zu behaupten, und *„die Gegend ist nicht magical"* wurde genau dafür zurückgewiesen. Markieren Sie die Stelle dort, wo sie steht — `<!-- mention: hollow-magical -->die Gegend ist nicht magical<!-- /mention -->` — und die Freigabe gilt nur für diese Stelle und diese Regel. Ob das Wort wirklich erwähnt und nicht verwendet wird, lässt sich nicht verifizieren; die Behauptung wird explizit und nachlesbar, statt dass nur die pauschale Freigabe der ganzen Regel bliebe.

Zwei Dinge, die man besser erwartet, als sie zu entdecken: Ihre ersten Reflexe sind häufiger Sätze als Nominalphrasen, also landen mehr davon in den manuellen Prüfpunkten — die ein Wiederlesen sind, keine Notizen, die Sie schreiben müssen; schriftlich beantwortet werden nur *die eigenen* Ausschlüsse des Nutzers — und ein ausgeteilter Rahmen ist eher einer, den der Auftrag nicht trägt, wofür `frame_fit` und ein neues Austeilen da sind.

`references/example-ritual-concept.md` ist ein vollständiges Beispiel genau dieser Form: der Schließungsritus einer Bäckerei, die seit neunzig Jahren in derselben Straße steht, samt Vertrag, Ansätzen und Sidecar, geprüft mit denselben zwei Befehlen.

## Was er nicht tut

> [!IMPORTANT]
> - **Irgendetwas bauen.** Zwei harte Gates: nie implementieren; und nichts erreicht dich ungeprüft — Ansätze warten auf die Divergenzprüfung, die Spec auf ihr Gate.
> - **Behaupten, das habe noch nie jemand gedacht.** Unüberprüfbar, also untersagt. Stattdessen werden die nächstliegenden existierenden Dinge benannt und der Unterschied gesagt.
> - **Fremdheit fabrizieren.** Wenn die konventionelle Antwort die richtige ist, muss der Skill das in einem Satz sagen, sich selbst verlassen und die gewöhnliche Arbeit außerhalb erledigen.
> - **Deine Anfrage verkleinern, damit sie leichter zu spezifizieren ist.** Umfang wird offen zerlegt, nie still verengt.
> - **So tun, als hieße ein bestandenes Gate, die Idee sei gut.** Es prüft, dass die verlangten Aussagen und Artefakte vorliegen, nicht dass das Konzept stimmt. Der Skill sagt das in seiner eigenen Ausgabe.

## Unter der Haube

| Skript | Aufgabe | Exit ≠ 0 |
|---|---|---|
| `deal.py` | Teilt Frage-Familien und drei unvereinbare Rahmen aus, einer als unbequem markiert | `1` Nutzungs- oder Deckfehler |
| `banlist.py` | Baut den Verbotsvertrag: Reflexe + Skelett + deine Ausschlüsse | `2` zu wenige Reflexe oder kein Skelett |
| `divergence_check.py` | Beweist, dass die Ansätze Alternativen sind und nicht ein Vorschlag mit zwei Attrappen | `3` divergiert nicht |
| `spec_gate.py` | Prüft geschriebene Spec, Sidecar und Vertrag zusammen, fail-closed | `2` Gate nicht bestanden |
| `cliche_lint.py` | Lintet mitten in der Sitzung jeden Entwurf | `3` verbotenes Material |

**Alles ist reproduzierbar.** Das Austeilen wird aus einem Hash des Auftrags gesetzt: derselbe Auftrag ergibt dieselbe Hand, und jede Sitzung lässt sich wiederholen. `--run 2` teilt frische Rahmen aus — weiterhin aus disjunkten Kategorien — wenn eine Divergenzrunde erschöpft ist, und der unbequeme Platz rotiert, damit ihn nicht immer dieselbe Kategorie trägt.

```text
skills/imagination-brainstorming/
├── SKILL.md                    # der maßgebliche Ablauf
├── references/
│   ├── concept-template.md     # Aufbau der Spec und ihre Abschnittsmarken
│   ├── worked-example.md       # eine komplette Sitzung, samt Verworfenem
│   ├── example-concept.md      # die Spec, die diese Sitzung ergab
│   ├── example-concept.json    # ihr Sidecar — beide bestehen die Gates und dienen als Fixtures
│   ├── example-approaches.json # Eingabe für Stufe 3, in der Form, die divergence_check.py liest
│   ├── example-banlist.json    # der Vertrag, gegen den all das geprüft wurde
│   ├── example-ritual-*.{md,json,txt}  # ein zweites vollständiges Beispiel, das kein Produkt und kein Dienst ist
│   ├── example-instincts.txt   # die zwölf Instinkte, aus denen er gebaut wurde
│   ├── example-exclusions.txt  # und die drei Ausschlüsse des Nutzers
│   └── decks/                  # Frage-Familien · Rahmen · Klischees · Spec-Schema · Ansatz-Schema
└── scripts/                    # deal · banlist · divergence_check · spec_gate · cliche_lint
```

### Begleiter

Unabhängig von [**imagination-engine**](https://github.com/djfksjd/imagination-engine-skill), aber als Nachbar gedacht: jener ist der Einmal-Generator für ein einzelnes fremdartiges Objekt. Dieser Skill übergibt dorthin, wenn ein Wesen, ein Mechanismus oder eine Welt im Konzept weit über das hinausgetrieben werden muss, was eine Spec fassen kann. Keiner setzt den anderen voraus.

## Tests

```bash
python3 -m pytest tests/ -q
```

Offline: Deck-Integrität, Determinismus des Austeilens und Disjunktheit der Kategorien, sämtliche Fehlpfade der drei Gates, und das mitgelieferte Beispiel, das sie besteht.

## Mitwirken

Am einfachsten hilft man bei den Decks — eine Frage-Familie mit einem wirklich anderen Angriffswinkel oder ein Rahmen, den keine bestehende Kategorie abdeckt. Jeder Eintrag muss benutzbar sein: eine Familie braucht, worauf zu hören ist, *und* die prämissenerhaltende Frage, die sie ersetzt; ein Rahmen braucht einen Zug, eine Anforderung und sein charakteristisches Scheitern. Vor dem PR bitte die Tests laufen lassen.

<div align="center">
<sub>MIT-Lizenz · gebaut für <a href="https://claude.com/claude-code">Claude Code</a> und Codex</sub>
</div>
