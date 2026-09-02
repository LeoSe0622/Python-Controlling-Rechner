"""Controlling-Rechnungen aus einer Wertetabelle berechnen.

Aufruf:
    python kennzahlen.py werte.csv
"""
import argparse
import csv
import sys


class CsvFehler(Exception):
    """Etwas an der CSV-Datei stimmt nicht - Datei fehlt, ist leer oder enthält ungültige Werte."""


def lade_werte(csv_pfad):
    try:
        with open(csv_pfad, encoding="utf-8", newline="") as datei:
            leser = csv.DictReader(datei, delimiter=";")
            spalten = leser.fieldnames
            zeilen = list(leser)
    except FileNotFoundError:
        raise CsvFehler(f"Datei nicht gefunden: {csv_pfad}")

    if spalten is None:
        raise CsvFehler(f"Keine Spalten in der CSV-Datei gefunden: {csv_pfad}")
    if "groesse" not in spalten or "wert" not in spalten:
        raise CsvFehler(f"Falsches Format: erwartet 'groesse' und 'wert' in den Spalten")

    werte = {}
    for zeile in zeilen:
        name = zeile["groesse"]
        try:
            werte[name] = float(zeile["wert"].replace(".", "").replace(",", "."))
        except ValueError:
            raise CsvFehler(f"Ungültiger Wert für {name}: {zeile['wert']}")

    return werte


def zeige_liste(ueberschrift, eintraege):
    print()
    print(ueberschrift)
    for eintrag in eintraege:
        print(f"  - {eintrag}")


# TODO 16 - formatiere_betrag zu formatiere_wert(wert, einheit) erweitern.
#   Grund: Nicht alles ist Geld. Break-Even-Menge ist eine Stueckzahl, die
#   DB-Quote ein Prozentwert, der Operating Leverage ein blosser Faktor.
#   Bisher haengt an allem ein "€" dran.
#
#   Aufbau (0 / 4 / 8 / 4 / 4 / 4):
#       def formatiere_wert(wert, einheit):
#           if einheit == "%":
#               <wert mit 100 multiplizieren>
#           <die bestehenden zwei Zeilen mit :,.2f und den replace bleiben>
#           return f"{text} {einheit}"
#
#   Das *100 beim Prozent: Eine Quote wird als Verhaeltnis gerechnet (0,4),
#   angezeigt werden soll aber 40,00 %. Das Rechnen bleibt sauber, nur die
#   Anzeige rechnet um.
#
#   Statt "€" fest im return steht jetzt {einheit}. Fuer Werte ohne Einheit
#   (Operating Leverage) uebergibt man einen leeren String "".
#
#   Die alte Funktion wird ersetzt, nicht ergaenzt - sie hat nur einen
#   Aufrufer (zeige_ergebnis, TODO 17).
def formatiere_betrag(wert):
    text = f"{wert:,.2f}"
    text = text.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{text} €"


# TODO 18 - rechne_deckungsbeitrag auf (Wert, Einheit)-Paare umstellen
#   und die DB-Quote ergaenzen.
#
#   a) Neue Zwischenzeile vor betriebsergebnis:
#          db_quote = db_gesamt / umsatz
#
#   b) Im return steht ab jetzt hinter jeder Bezeichnung ein PAAR in runden
#      Klammern - Zahl und Einheit:
#          "Umsatz": (umsatz, "€"),
#          "DB-Quote": (db_quote, "%"),
#      Alle sechs Eintraege umstellen. Reihenfolge fachlich sinnvoll lassen:
#      Umsatz, variable Kosten, DB je Stueck, DB gesamt, DB-Quote, Betriebsergebnis.
#
#   Ein Tupel in runden Klammern - dieselbe Bauform wie die Zeilen im Register.
def rechne_deckungsbeitrag(werte):
    umsatz = werte["absatzmenge"] * werte["preis_stueck"]
    var_kosten_gesamt = werte["absatzmenge"] * werte["var_kosten_stueck"]
    db_stueck = werte["preis_stueck"] - werte["var_kosten_stueck"]
    db_gesamt = werte["absatzmenge"] * db_stueck
    betriebsergebnis = db_gesamt - werte["fixkosten"]
    return {
        "Umsatz": umsatz,
        "Variable Kosten gesamt": var_kosten_gesamt,
        "Deckungsbeitrag je Stück": db_stueck,
        "Deckungsbeitrag gesamt": db_gesamt,
        "Betriebsergebnis": betriebsergebnis
    }


# TODO 19 - Zweite Rechnung: rechne_break_even(werte)
#   HIER hin, zwischen rechne_deckungsbeitrag und RECHNUNGEN - die Funktion muss
#   ueber dem Register stehen, sonst kennt Python den Namen dort noch nicht.
#
#   Braucht: absatzmenge, preis_stueck, var_kosten_stueck, fixkosten
#
#   Zwischenschritte (lokale Variablen, wie gehabt):
#       db_stueck          = preis_stueck - var_kosten_stueck
#       db_gesamt          = absatzmenge * db_stueck
#       betriebsergebnis   = db_gesamt - fixkosten
#
#   Ergebnisse (mit Einheit als Paar):
#       Break-Even-Menge        = fixkosten / db_stueck                "Stück"
#       Break-Even-Umsatz       = break_even_menge * preis_stueck      "€"
#       Sicherheitsstrecke      = absatzmenge - break_even_menge       "Stück"
#       Sicherheitskoeffizient  = sicherheitsstrecke / absatzmenge     "%"
#       Operating Leverage      = db_gesamt / betriebsergebnis         ""
#
#   Ja, db_stueck und db_gesamt werden hier ein zweites Mal gerechnet - sie
#   stehen ja schon in rechne_deckungsbeitrag. Das ist der bewusste Preis dafuer,
#   dass Rechnungen nichts voneinander uebernehmen. Dafuer ist jede fuer sich
#   verstaendlich und laeuft auch, wenn die andere nicht moeglich ist.


# TODO 20 - Registerzeile fuer die Break-Even-Analyse ergaenzen.
#   Hinter die bestehende Zeile, Komma nicht vergessen:
#       ("Break-Even-Analyse",
#        {"absatzmenge", "preis_stueck", "var_kosten_stueck", "fixkosten"},
#        rechne_break_even),
#   Funktionsname ohne Klammern. Das ist der GANZE Aufwand, um die Rechnung
#   ins Programm zu bringen - main() wird nicht angefasst.
RECHNUNGEN = [
    ("Deckungsbeitragsrechnung",
     {"absatzmenge", "preis_stueck", "var_kosten_stueck", "fixkosten"},
     rechne_deckungsbeitrag)
]


# TODO 21 - Division durch Null zentral abfangen.
#   Break-Even teilt durch db_stueck, Operating Leverage durch betriebsergebnis.
#   Sind die 0 (Preis = variable Kosten, oder Ergebnis genau ausgeglichen),
#   bricht das Programm mit einem rohen ZeroDivisionError ab.
#
#   Statt in jeder Rechenfunktion zu pruefen: EINMAL hier, im if-Zweig.
#   Aus der einen Zeile
#       ergebnisse.append((name, funktion(werte)))
#   wird ein try/except (Einrueckung 12 / 16 / 12 / 16):
#       try:
#           ergebnisse.append((name, funktion(werte)))
#       except ZeroDivisionError:
#           <an fehlt anhaengen, mit Hinweis auf die Division durch Null>
#
#   Der Gewinn: Diese eine Absicherung gilt fuer ALLE Rechnungen - auch fuer
#   die, die du erst in Phase 2 und 3 schreibst. Genau wie bei der Registerlogik.
def fuehre_rechnungen_aus(werte):
    ergebnisse = []
    fehlt = []
    vorhanden = set(werte)
    for name, benoetigt, funktion in RECHNUNGEN:
        if benoetigt <= vorhanden:
            ergebnisse.append((name, funktion(werte)))
        else:
            fehlt.append(f"{name} (braucht {', '.join(sorted(benoetigt - vorhanden))})")
    return ergebnisse, fehlt


# TODO 17 - zeige_ergebnis an die Paare anpassen.
#   Im Ergebnis-Dictionary steht jetzt hinter jeder Bezeichnung ein Paar aus
#   Zahl und Einheit. Die Schleifenzeile bekommt dafuer Klammern:
#       for bezeichnung, (wert, einheit) in ergebnis.items():
#
#   Das ist verschachteltes Entpacken: .items() liefert (Bezeichnung, Paar),
#   und die Klammern nehmen das Paar gleich nochmal auseinander. Ohne sie
#   waere 'wert' das ganze Tupel ("(400000.0, '€')").
#
#   In der print-Zeile dann formatiere_wert(wert, einheit) statt
#   formatiere_betrag(wert). Die Breite von 16 auf 18 erhoehen - "3.750,00 Stück"
#   ist laenger als ein Eurobetrag.
def zeige_ergebnis(name, ergebnis):
    print()
    print(f"{name}:")
    for bezeichnung, wert in ergebnis.items():
        print(f"  {bezeichnung + ':':28} {formatiere_betrag(wert):>16}")


def main():
    parser = argparse.ArgumentParser(description="Controlling-Rechnungen aus einer Wertetabelle berechnen.")
    parser.add_argument("csv_pfad", help="Pfad zur CSV-Datei mit den Spalten 'groesse' und 'wert'")

    args = parser.parse_args()
    csv_pfad = args.csv_pfad

    try:
        werte = lade_werte(csv_pfad)
    except CsvFehler as fehler:
        print(f"Fehler: {fehler}", file=sys.stderr)
        sys.exit(1)

    print(f"Datei: {csv_pfad}")
    print(f"Spalten: {', '.join(sorted(werte.keys()))}")
    print(f"{len(werte)} Werte gelesen")

    ergebnisse, fehlt = fuehre_rechnungen_aus(werte)

    for name, ergebnis in ergebnisse:
        zeige_ergebnis(name, ergebnis)
    zeige_liste("Nicht möglich:", fehlt)


if __name__ == "__main__":
    main()
