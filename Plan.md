# Plan

## Stand

Das Rechenwerk läuft. **16 Rechnungen** in fünf Gruppen, **25 automatische
Tests**, 15 Testdateien. Aufbau und Bedienung stehen in `README.md`.

Seit dem letzten Stand erledigt:

- **Ausgabe gestaltet** — Ergebnisse nach Gruppen sortiert, „Nicht möglich"
  standardmäßig als kurze Namensliste, die Gründe nur auf `--fehlend`
- **Tippfehler-Erkennung** — unbekannte Größen werden gemeldet, mit Vorschlag
  ähnlicher Namen aus dem Register (`difflib.get_close_matches`)
- **`--liste`** — zeigt alle Rechnungen mit ihren Größen, ohne CSV-Datei
- **Projekthygiene** — `.gitignore`, `__pycache__` aus der Versionierung

---

## 1. Bedienung

- **`--nur "Break-Even"`** — nur eine bestimmte Rechnung ausführen. Komfort,
  kein Problem: seit der Gruppierung sind 16 Blöcke gut lesbar.

`--beispiel` ist gestrichen. `tests/04_alles.csv` ist die Beispieldatei; ein
Generator daneben wäre eine zweite Wahrheit, die auseinanderlaufen kann.

---

## 2. Refactoring

Kleinigkeiten, die sich angesammelt haben:

- Leerzeichen hinter dem Doppelpunkt in `def rechne_abweichungsanalyse(werte): `
- `for t,zahlung in ...` — Leerzeichen nach dem Komma
- Die `return {`-Zeile in `rechne_investition_dynamisch` ist anders eingerückt
  als in allen übrigen Rechenfunktionen
- `zeige_ergebnis` (Einzahl) und `zeige_liste` ruft niemand mehr auf
- „Unbekannte Groessen" in der Ausgabe schreibt sich ohne Umlaut, anders als
  der übrige Text
- Der Operating Leverage hat als einziger Wert keine Einheit — dadurch endet
  seine Zeile auf ein Leerzeichen
- `kennzahlen.py` ist auf 581 Zeilen gewachsen. Eine Aufteilung wäre denkbar:
  `rechnungen.py` für Rechenfunktionen und Register, `ausgabe.py` für
  Formatierung und Anzeige, `kennzahlen.py` nur noch für Einlesen und Ablauf.

---

## 3. Dokumentation

- **`tests/README.md` fehlt.** Sie beschrieb, was jede Testdatei prüft, und ging
  beim Umbenennen von `testdaten/` nach `tests/` verloren. Für die Dateien 11
  bis 15 gab es sie noch nie.
- **`Möglichkeiten.md` gibt es nicht mehr** — die Liste des fachlichen Umfangs.
  Sie war nie in Git und ist von der Platte verschwunden. Die Verweise darauf
  sind aus README und Plan entfernt. Falls der fachliche Umfang wieder
  schriftlich gebraucht wird, ersetzt ihn heute `python kennzahlen.py --liste`.

---

## Bewusst nicht umgesetzt

Steht so auch in der README:

- **Der BAB als vollständige Verteilungstabelle.** Berechnet werden die
  Zuschlagssätze, nicht die Verteilung mehrerer Kostenarten auf mehrere
  Kostenstellen. Das bräuchte eine Matrix statt einer Werteliste.
- **Optimales Produktionsprogramm.** Der Vergleich mehrerer Produkte über den
  relativen Deckungsbeitrag je Engpasseinheit setzt mehrere Produktzeilen voraus.
- **Ergebnisse einer Rechnung als Eingabe für eine andere.** Jede Rechnung
  arbeitet nur mit den CSV-Werten. Zwischenschritte innerhalb einer Rechnung sind
  normale lokale Variablen; weitergereicht wird nichts. Bewusste Entscheidung
  zugunsten eines durchschaubaren Ablaufs.

Sollte eines davon doch dazukommen, wäre es je eine eigene Phase — die ersten
beiden brauchen ein zweites Eingabeformat, das dritte eine Ableitungsschleife.

---

## Arbeitsweise

- Pro Sitzung ein Thema
- Bausteine erklärt, TODOs in den Code, Umsetzung durch mich (Leonard)
- Nach jedem Schritt `python -m unittest discover -s tests -t .`
- Neue Rechnung heißt: Funktion schreiben, Registerzeile eintragen, Testdatei
  ergänzen, Testklasse schreiben
