# Python-Controlling-Rechner

Eine Rechenmaschine, die auf Basis von CSV-Daten die möglichen typischen
Controllingberechnungen durchführt.

Das Programm liest eine Tabelle betriebswirtschaftlicher Größen und führt
**automatisch alle Rechnungen durch, für die die nötigen Werte vorliegen**.
Was nicht geht, wird mit Begründung aufgelistet — inklusive der fehlenden Größen.

# Entstehung

Das Projekt entstand aus dem Versuch, mein schon erlangtes theoretisches Wissen
in Python (durch Googles Cybersecurity-Zertifikat) in einem Projekt umzusetzen.
Dabei stand mir Claude Code zur Seite, plante und schrieb Todos — so wusste ich
genau, was wo hin kommt. Die Logik war dann meine Aufgabe. Sachen, die ich nicht
kannte, erfragte ich und ließ mir helfen, so konnte ich optimal lernen und
effizient arbeiten.

# Berechnungen

16 Rechnungen, die den fachlichen Umfang aus `Möglichkeiten.md` abdecken.
Was eine Rechnung liefert, zeigt der Programmlauf.

| Rechnung | benötigte Größen |
|---|---|
| Deckungsbeitragsrechnung | `absatzmenge`, `preis_stueck`, `var_kosten_stueck`, `fixkosten` |
| Break-Even-Analyse | dieselben |
| Kostenartenrechnung | `materialkosten`, `personalkosten`, `abschreibungen`, `sonstige_kosten` |
| Zuschlagssätze (BAB) | `fertigungsmaterial`, `materialgemeinkosten`, `fertigungsloehne`, `fertigungsgemeinkosten`, `verwaltungsgemeinkosten`, `vertriebsgemeinkosten` |
| Zuschlagskalkulation | `fertigungsmaterial_stueck`, `fertigungsloehne_stueck`, `mgk_satz`, `fgk_satz`, `vwgk_satz`, `vtgk_satz`, `gewinnzuschlag` |
| Prozesskostenrechnung | `prozesskosten_lmi`, `prozesskosten_lmn`, `prozessmenge` |
| Abweichungsanalyse (Material) | `plan_menge`, `plan_preis`, `ist_menge`, `ist_preis` |
| Plankostenrechnung (flexibel) | `plan_beschaeftigung`, `ist_beschaeftigung`, `plan_fixkosten`, `plan_var_kosten_je_einheit`, `ist_kosten` |
| Make-or-Buy | `var_kosten_stueck_eigen`, `fixkosten_eigen`, `bezugspreis_stueck`, `menge` |
| Investitionsrechnung (statisch) | `anschaffungswert`, `restwert`, `nutzungsdauer`, `kalkulationszinssatz`, `jaehrlicher_gewinn` |
| Investitionsrechnung (dynamisch) | `kalkulationszinssatz`, `zahlung_0` … |
| Interner Zinsfuß | `zahlung_0` … |
| ROI / DuPont | `umsatz`, `betriebsergebnis`, `gesamtkapital` |
| Kapitalstruktur | `eigenkapital`, `fremdkapital` |
| Liquidität | `jahresueberschuss`, `abschreibungen`, `umlaufvermoegen`, `kurzfristige_verbindlichkeiten` |
| Economic Value Added | `nopat`, `investiertes_kapital`, `kapitalkostensatz` |

# Datenstruktur

CSV mit **Semikolon** als Trennzeichen, **UTF-8** kodiert, genau zwei Spalten:

```
groesse;wert
absatzmenge;5000
preis_stueck;80,00
var_kosten_stueck;48,00
fixkosten;120000,00
```

- **`groesse`** — der Name, exakt wie in der Tabelle oben
- **`wert`** — deutsches Zahlenformat: Komma als Dezimaltrennzeichen, Punkt als
  Tausendertrenner (`1.234,56` wird korrekt gelesen)

Prozentsätze als Verhältnis, nicht als Prozentzahl: `kalkulationszinssatz;0,08`
für 8 %. Zusätzliche Zeilen stören nicht — sie werden ignoriert, wenn keine
Rechnung sie braucht.

**Zahlungsreihen** für die dynamische Investitionsrechnung werden durchnummeriert,
beginnend bei `zahlung_0` für den Zeitpunkt 0. Das Programm liest weiter, bis die
nächste Nummer fehlt:

```
zahlung_0;-100000,00
zahlung_1;30000,00
zahlung_2;40000,00
```

# Benutzung

```
python kennzahlen.py tests/01_deckungsbeitrag.csv
```

```
Deckungsbeitragsrechnung:
  Umsatz:                            400.000,00 €
  Deckungsbeitrag je Stück:               32,00 €
  DB-Quote:                               40,00 %
  Betriebsergebnis:                   40.000,00 €

Break-Even-Analyse:
  Break-Even-Menge:                3.750,00 Stück
  Sicherheitskoeffizient:                 25,00 %

Nicht möglich:
  - ROI / DuPont (braucht betriebsergebnis, gesamtkapital, umsatz)
  - Kapitalstruktur (braucht eigenkapital, fremdkapital)
```

| Exit-Code | Bedeutung |
|---|---|
| `0` | gelaufen, Rechnungen soweit möglich |
| `1` | Datei fehlt, ist leer, falsches Format oder ungültiger Wert |
| `2` | falscher Aufruf |

Fehler gehen auf `stderr`, Ergebnisse auf `stdout` — die Ausgabe lässt sich also
umleiten, ohne dass Fehler in der Datei landen.

# Aufbau

```
kennzahlen.py         das Programm
Plan.md               was noch offen ist
Möglichkeiten.md      der fachliche Umfang
tests/                Testdaten und automatische Tests
```

Kern ist das Register `RECHNUNGEN` — eine Tabelle aus **Name**, **benötigten
Größen** und **Rechenfunktion**:

```python
RECHNUNGEN = [
    ("Deckungsbeitragsrechnung",
     {"absatzmenge", "preis_stueck", "var_kosten_stueck", "fixkosten"},
     rechne_deckungsbeitrag),
    ...
]
```

`fuehre_rechnungen_aus` geht die Tabelle durch, prüft per Mengenoperation, ob die
benötigten Größen vorliegen, und ruft nur dann die Funktion auf. Jede
Rechenfunktion liefert `{Bezeichnung: (Zahl, Einheit)}` — deshalb genügt eine
einzige Ausgabefunktion für alle.

Eine neue Rechnung ergänzen heißt: **Funktion schreiben, Zeile eintragen.**
Ausgabe, Prüfung und Fehlermeldung entstehen von selbst.

# Tests

```
python -m unittest discover -s tests -t .
```

Geprüft werden die Rechenformeln gegen bekannte Sollwerte, das Einlesen samt
Fehlerfällen, die Formatierung, das Programm über die Kommandozeile und das
Register selbst — etwa, dass jede geschriebene Rechenfunktion eingetragen ist.

# Nicht enthalten

- **BAB als Verteilungstabelle.** Berechnet werden die Zuschlagssätze, nicht die
  Verteilung mehrerer Kostenarten auf mehrere Kostenstellen — das bräuchte eine
  Matrix statt einer Werteliste.
- **Optimales Produktionsprogramm.** Setzt mehrere Produktzeilen voraus.
- **Ergebnisse einer Rechnung als Eingabe für eine andere.** Jede Rechnung
  arbeitet nur mit den CSV-Werten. Bewusste Entscheidung zugunsten eines
  durchschaubaren Ablaufs.
