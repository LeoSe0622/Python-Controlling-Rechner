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

    # TODO 7 - Die beiden neuen Kennzahlen ausgeben. Beide Bloecke hierhin,
    #   nach dem Muster von "Summen und Saldo" darueber.
    #
    #   a) Kategorien (4 / 8 / 8 / 8 / 8 / 12):
    #          if "Auswertung nach Kategorie" in möglich:
    #              kategorien = berechne_kategorien(buchungen)
    #              print()
    #              print("Auswertung nach Kategorie:")
    #              for kategorie, summe in sorted(kategorien.items()):
    #                  <eine Zeile ausgeben, Summe in round(..., 2)>
    #
    #      Achtung: die letzte print-Zeile steht auf 12, sie gehoert IN die
    #      Schleife - anders als bei "Summen und Saldo".
    #
    #   b) Monate: genau derselbe Aufbau, nur mit berechne_monate(buchungen)
    #      und der Ueberschrift "Monatsverlauf:".
    #
    #   Erwartet bei buchungen.csv:
    #      Miete -2500.0 / Software -89.9 / Umsatz 4800.0
    #      2026-01 3460.1 / 2026-02 -1250.0
    #   Gegentest ohne_kategorie.csv: nur der Monatsblock darf erscheinen.


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


# TODO 5 - Funktion berechne_kategorien(buchungen) hier anlegen.
#   Aufbau (Einrueckung 0 / 4 / 4 / 8 / 8 / 4):
#       def berechne_kategorien(buchungen):
#           summen = {}                     <- leeres Dictionary
#           for buchung in buchungen:
#               <Kategorie der Buchung in eine Variable holen>
#               <mit .get(...) aufaddieren:>
#                   summen[kat] = summen.get(kat, 0) + buchung["betrag"]
#           return summen
#
#   Warum .get(kat, 0):  summen[kat] += ... wirft beim ERSTEN Mal einen
#   KeyError, weil der Schluessel noch nicht existiert. .get liefert
#   in dem Fall die 0 und der erste Durchlauf klappt wie alle anderen.


# TODO 6 - Funktion berechne_monate(buchungen) hier anlegen.
#   Genau dasselbe Muster wie TODO 5. Einziger Unterschied: Der Schluessel
#   steht nicht in der Buchung, du baust ihn aus dem Datum:
#       monat = buchung["datum"].strftime("%Y-%m")     -> z.B. '2026-01'
#
#   strftime ist das Gegenstueck zu strptime: strptime liest Text und macht
#   ein Datum daraus, strftime macht aus einem Datum wieder Text.
#   "%Y-%m" (Jahr zuerst!), damit die Monate sich als Text korrekt sortieren
#   lassen - "01.2026" wuerde den Dezember 2025 hinter den Februar 2026 sortieren.


if __name__ == "__main__":
    main()
