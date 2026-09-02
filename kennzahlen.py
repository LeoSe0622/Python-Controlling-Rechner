"""Kennzahlen aus einer Buchungs-CSV berechnen.

Aufruf:
    python kennzahlen.py buchungen.csv
"""
import argparse

def main():
    parser = argparse.ArgumentParser(description="Kennzahlen aus einer Buchungs-CSV berechnen.")
    parser.add_argument("csv_pfad", help="Pfad zur Buchungs-CSV-Datei")

    args = parser.parse_args()

    csv_pfad = args.csv_pfad
    print(f"Empfangener Dateipfad: {csv_pfad}")


if __name__ == "__main__":
    main()
