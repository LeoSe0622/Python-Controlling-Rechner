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


def main():
    parser = argparse.ArgumentParser(description="Kennzahlen aus einer Buchungs-CSV berechnen.")
    parser.add_argument("csv_pfad", help="Pfad zur Buchungs-CSV-Datei")

    args = parser.parse_args()
    csv_pfad = args.csv_pfad

    try:
        spalten, buchungen = lade_buchungen(csv_pfad)
        wandle_werte(buchungen, spalten)
    except CsvFehler as fehler:
        print(f"Fehler: {fehler}", file=sys.stderr)
        sys.exit(1)

    print(f"Datei: {csv_pfad}")
    print(f"Spalten: {', '.join(spalten)}")
    print(f"{len(buchungen)} Buchungen gelesen")

    möglich, fehlt = bestimme_kennzahlen(spalten)

    zeige_liste("Mögliche Kennzahlen:", möglich)
    zeige_liste("Nicht möglich:", fehlt)

    if "Summen und Saldo" in möglich:
        einnahmen, ausgaben, saldo = berechne_summen(buchungen)
        print()
        print("Summen und Saldo:")
        print(f"  {'Einnahmen:':12} {formatiere_betrag(einnahmen):>14}")
        print(f"  {'Ausgaben:':12} {formatiere_betrag(ausgaben):>14}")
        print(f"  {'Saldo:':12} {formatiere_betrag(saldo):>14}")

    if "Auswertung nach Kategorie" in möglich:
        kategorien = berechne_kategorien(buchungen)
        print()
        print("Auswertung nach Kategorie:")
        for kategorie, summe in sorted(kategorien.items()):
            print(f"  {kategorie + ':':16} {formatiere_betrag(summe):>14}")

    if "Monatsverlauf" in möglich:
        monate = berechne_monate(buchungen)
        print()
        print("Monatsverlauf:")
        for monat, summe in sorted(monate.items()):
            print(f"  {monat + ':':16} {formatiere_betrag(summe):>14}")


if __name__ == "__main__":
    main()
