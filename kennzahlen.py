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
def main():

    parser = argparse.ArgumentParser(description="Kennzahlen aus einer Buchungs-CSV berechnen.")
    parser.add_argument("csv_pfad", help="Pfad zur Buchungs-CSV-Datei")

    args = parser.parse_args()

    csv_pfad = args.csv_pfad

    try:
        with open(csv_pfad, encoding="utf-8", newline="") as datei:
            leser = csv.DictReader(datei, delimiter=";")
            spalten = leser.fieldnames
            buchungen = list(leser)

    except FileNotFoundError:
        print(f"Fehler: Datei nicht gefunden: {csv_pfad}", file=sys.stderr)
        sys.exit(1)

    if spalten is None:
        print(f"Fehler: Keine Spalten in der CSV-Datei gefunden: {csv_pfad}", file=sys.stderr)
        sys.exit(1)

    print(f"Datei: {csv_pfad}")
    print(f"Spalten: {', '.join(spalten)}")
    print(f"{len(buchungen)} Buchungen gelesen")

    if "betrag" in spalten:
        for buchung in buchungen:
            try:
                buchung["betrag"] = float(buchung["betrag"].replace(".", "").replace(",", "."))
            except ValueError:
                print(f"Fehler: Ungültiger Betrag: {buchung['betrag']}", file=sys.stderr)
                sys.exit(1)

    if "datum" in spalten:
        for buchung in buchungen:
            try:
                buchung["datum"] = datetime.strptime(buchung["datum"], "%d.%m.%Y").date()
            except ValueError:
                print(f"Fehler: Ungültiges Datum: {buchung['datum']}", file=sys.stderr)
                sys.exit(1)

    möglich = []
    fehlt = []

    vorhanden = set(spalten)

    for name, benoetigt in KENNZAHLEN:
        if benoetigt <= vorhanden:
            möglich.append(name)
        else:
            fehlt.append(f"{name} (braucht {', '.join(sorted(benoetigt - vorhanden))})")

    print()
    print("Mögliche Kennzahlen:")
    for name in möglich:
        print(f"  - {name}")

    print()
    print("Nicht möglich:")

    for name in fehlt:
        print(f"  - {name}")

    if "Summen und Saldo" in möglich:
        einnahmen, ausgaben, saldo = berechne_summen(buchungen)
        print()
        print("Summen und Saldo:")
        print(f"  Einnahmen: {round(einnahmen, 2)}")
        print(f"  Ausgaben: {round(ausgaben, 2)}")
        print(f"  Saldo: {round(saldo, 2)}")

    
    if "Auswertung nach Kategorie" in möglich:
        kategorien = berechne_kategorien(buchungen)
        print()
        print("Auswertung nach Kategorie:")
        for kategorie, summe in sorted(kategorien.items()):
            print(f"  {kategorie}: {round(summe, 2)}")

    if "Monatsverlauf" in möglich:
        monate = berechne_monate(buchungen)
        print()
        print("Monatsverlauf:")
        for monat, summe in sorted(monate.items()):
            print(f"  {monat}: {round(summe, 2)}")

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
    summen ={}
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

if __name__ == "__main__":
    main()
