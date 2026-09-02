"""Kennzahlen aus einer Buchungs-CSV berechnen.

Aufruf:
    python kennzahlen.py buchungen.csv
"""
import argparse
import csv
import sys
from datetime import datetime


KENNZAHLEN = [
    ("Summen und Saldo", {"betrag"}),
    ("Auswertung nach Kategorie", {"betrag", "kategorie"}),
    ("Monatsverlauf", {"betrag", "datum"}),
    ("Auswertung je Kostenstelle", {"betrag", "kostenstelle"})
]


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


def lade_buchungen(csv_pfad):
    try:
        with open(csv_pfad, encoding="utf-8", newline="") as datei:
            leser = csv.DictReader(datei, delimiter=";")
            spalten = leser.fieldnames
            buchungen = list(leser)
    except FileNotFoundError:
        raise CsvFehler(f"Datei nicht gefunden: {csv_pfad}")

    if spalten is None:
        raise CsvFehler(f"Keine Spalten in der CSV-Datei gefunden: {csv_pfad}")

    return spalten, buchungen


def wandle_werte(buchungen, spalten):
    if "betrag" in spalten:
        for buchung in buchungen:
            try:
                buchung["betrag"] = float(buchung["betrag"].replace(".", "").replace(",", "."))
            except ValueError:
                raise CsvFehler(f"Ungültiger Betrag: {buchung['betrag']}")

    if "datum" in spalten:
        for buchung in buchungen:
            try:
                buchung["datum"] = datetime.strptime(buchung["datum"], "%d.%m.%Y").date()
            except ValueError:
                raise CsvFehler(f"Ungültiges Datum: {buchung['datum']}")


def bestimme_kennzahlen(spalten):
    möglich = []
    fehlt = []

    vorhanden = set(spalten)

    for name, benoetigt in KENNZAHLEN:
        if benoetigt <= vorhanden:
            möglich.append(name)
        else:
            fehlt.append(f"{name} (braucht {', '.join(sorted(benoetigt - vorhanden))})")

    return möglich, fehlt


def zeige_liste(ueberschrift, eintraege):
    print()
    print(ueberschrift)
    for eintrag in eintraege:
        print(f"  - {eintrag}")


def berechne_summen(buchungen):
    einnahmen = 0
    ausgaben = 0
    for buchung in buchungen:
        if buchung["betrag"] > 0:
            einnahmen += buchung["betrag"]
        else:
            ausgaben += buchung["betrag"]
    saldo = einnahmen + ausgaben
    return einnahmen, ausgaben, saldo


def berechne_kategorien(buchungen):
    summen = {}
    for buchung in buchungen:
        kategorie = buchung["kategorie"]
        summen[kategorie] = summen.get(kategorie, 0) + buchung["betrag"]
    return summen


def berechne_monate(buchungen):
    summen = {}
    for buchung in buchungen:
        monat = buchung["datum"].strftime("%Y-%m")
        summen[monat] = summen.get(monat, 0) + buchung["betrag"]
    return summen


def formatiere_betrag(wert):
    text = f"{wert:,.2f}"
    text = text.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{text} €"


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


RECHNUNGEN = [
    ("Deckungsbeitragsrechnung",
     {"absatzmenge", "preis_stueck", "var_kosten_stueck", "fixkosten"},
     rechne_deckungsbeitrag)
]


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


def zeige_ergebnis(name, ergebnis):
    print()
    print(f"{name}:")
    for bezeichnung, wert in ergebnis.items():
        print(f"  {bezeichnung + ':':28} {formatiere_betrag(wert):>16}")


def main():
    parser = argparse.ArgumentParser(description="Kennzahlen aus einer Buchungs-CSV berechnen.")
    parser.add_argument("csv_pfad", help="Pfad zur Buchungs-CSV-Datei")

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
