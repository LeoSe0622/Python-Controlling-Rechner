# Python-Controlling-Rechner

Eine Rechenmaschine für die typischen Controllingberechnungen. Sie liest eine
CSV-Tabelle betriebswirtschaftlicher Größen und führt **automatisch alle
Rechnungen durch, für die die nötigen Werte vorliegen**. Was nicht geht, wird
aufgelistet — auf Wunsch mit den fehlenden Größen.

# Entstehung

Das Projekt entstand aus dem Versuch, mein schon erlangtes theoretisches Wissen
in Python (durch Googles Cybersecurity-Zertifikat) in einem Projekt umzusetzen.
Dabei stand mir Claude Code zur Seite, plante und schrieb Todos — so wusste ich
genau, was wo hin kommt. Die Logik war dann meine Aufgabe. Sachen, die ich nicht
kannte, erfragte ich und ließ mir helfen, so konnte ich optimal lernen und
effizient arbeiten.

# Berechnungen

16 Rechnungen in fünf Gruppen:

| Gruppe | Rechnungen |
|---|---|
| Teilkostenrechnung | Deckungsbeitragsrechnung, Break-Even-Analyse |
| Vollkostenrechnung | Kostenartenrechnung, Zuschlagssätze (BAB), Zuschlagskalkulation, Prozesskostenrechnung |
| Kontrolle und Steuerung | Abweichungsanalyse (Material), Plankostenrechnung (flexibel), Make-or-Buy |
| Investitionsrechnung | statisch, dynamisch, Interner Zinsfuß |
| Kennzahlen | ROI / DuPont, Kapitalstruktur, Liquidität, Economic Value Added |

Welche Größen eine Rechnung braucht, sagt das Programm selbst — `--liste`
braucht keine Datei:

```
python kennzahlen.py --liste
```

```
Teilkostenrechnung:
  Deckungsbeitragsrechnung:
    absatzmenge, fixkosten, preis_stueck, var_kosten_stueck
```

Die Angaben kommen aus dem Register in `kennzahlen.py` und stehen damit nur an
einer Stelle.

# Datenstruktur

CSV mit **Semikolon** als Trennzeichen, **UTF-8** kodiert, genau zwei Spalten:

```
groesse;wert
absatzmenge;5000
preis_stueck;80,00
var_kosten_stueck;48,00
fixkosten;120000,00
```

- **`groesse`** — der Name, exakt wie in `--liste`
- **`wert`** — deutsches Zahlenformat: Komma als Dezimaltrennzeichen, Punkt als
  Tausendertrenner (`1.234,56` wird korrekt gelesen)

Prozentsätze als Verhältnis: `kalkulationszinssatz;0,08` für 8 %. Unbekannte
Zeilen stören nicht — das Programm meldet sie nur und schlägt bei Tippfehlern
ähnliche Namen vor:

```
Unbekannte Groessen (1) - keine Rechnung verwendet sie:
  - absatzmnge (meinst du absatzmenge?)
```

**Zahlungsreihen** für die dynamische Investitionsrechnung werden ab
`zahlung_0` durchnummeriert (`zahlung_0;-100000,00`, `zahlung_1;30000,00`, …).
Das Programm liest weiter, bis die nächste Nummer fehlt.

# Benutzung

```
python kennzahlen.py tests/01_deckungsbeitrag.csv
```

```
============================================================
  tests/01_deckungsbeitrag.csv   —   4 Größen gelesen
============================================================

Teilkostenrechnung:
  Deckungsbeitragsrechnung:
    Umsatz:                            400.000,00 €
    Deckungsbeitrag je Stück:               32,00 €
    DB-Quote:                               40,00 %
  Break-Even-Analyse:
    Break-Even-Menge:                3.750,00 Stück
    Sicherheitskoeffizient:                 25,00 %

Nicht möglich (14)
  Kostenartenrechnung, Zuschlagssätze (BAB), …
  (--fehlend zeigt, was fehlt)
```

| Option | |
|---|---|
| `--fehlend` | nennt zu jeder nicht möglichen Rechnung die fehlenden Größen |
| `--liste` | zeigt alle Rechnungen mit ihren Größen, ohne Datei |
| `--help` | die eingebaute Hilfe |

| Exit-Code | Bedeutung |
|---|---|
| `0` | gelaufen, Rechnungen soweit möglich |
| `1` | Datei fehlt, ist leer, falsches Format, ungültiger oder doppelter Wert |
| `2` | falscher Aufruf |

Fehler gehen auf `stderr`, Ergebnisse auf `stdout` — die Ausgabe lässt sich also
umleiten, ohne dass Fehler in der Datei landen.

# Aufbau

```
kennzahlen.py         das Programm
Plan.md               was noch offen ist
tests/                Testdaten und automatische Tests
```

Kern ist das Register `RECHNUNGEN` — eine Tabelle aus **Gruppe**, **Name**,
**benötigten Größen** und **Rechenfunktion**:

```python
RECHNUNGEN = [
    ("Teilkostenrechnung", "Deckungsbeitragsrechnung",
     {"absatzmenge", "preis_stueck", "var_kosten_stueck", "fixkosten"},
     rechne_deckungsbeitrag),
    ...
]
```

`fuehre_rechnungen_aus` geht die Tabelle durch, prüft per Mengenoperation, ob die
benötigten Größen vorliegen, und ruft nur dann die Funktion auf. Jede
Rechenfunktion liefert `{Bezeichnung: (Zahl, Einheit)}`, deshalb genügt eine
einzige Ausgabefunktion für alle. Dieselbe Tabelle speist `--liste` und die
Tippfehler-Erkennung — eine neue Rechnung ergänzen heißt darum:
**Funktion schreiben, Zeile eintragen.**

# Tests

```
python -m unittest discover -s tests -t .
```

25 Tests: Rechenformeln gegen bekannte Sollwerte, Einlesen samt Fehlerfällen,
Formatierung, das Programm über die Kommandozeile und das Register selbst — etwa,
dass jede geschriebene Rechenfunktion eingetragen ist und jede Größe in `--liste`
auftaucht.

# Nicht enthalten

- **BAB als Verteilungstabelle.** Berechnet werden die Zuschlagssätze, nicht die
  Verteilung auf mehrere Kostenstellen — das bräuchte eine Matrix.
- **Optimales Produktionsprogramm.** Setzt mehrere Produktzeilen voraus.
- **Ergebnisse einer Rechnung als Eingabe für eine andere.** Jede Rechnung
  arbeitet nur mit den CSV-Werten — bewusst, zugunsten eines durchschaubaren
  Ablaufs.
