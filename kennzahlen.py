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


def formatiere_betrag(wert, einheit="€"):
    text = f"{wert:,.2f}"
    text = text.replace(",", "X").replace(".", ",").replace("X", ".")
    if einheit == "%":
        text = f"{wert * 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{text} {einheit}"


def rechne_deckungsbeitrag(werte):
    umsatz = werte["absatzmenge"] * werte["preis_stueck"]
    var_kosten_gesamt = werte["absatzmenge"] * werte["var_kosten_stueck"]
    db_stueck = werte["preis_stueck"] - werte["var_kosten_stueck"]
    db_gesamt = werte["absatzmenge"] * db_stueck
    db_quote = db_gesamt / umsatz
    betriebsergebnis = db_gesamt - werte["fixkosten"]
    return {
        "Umsatz": (umsatz, "€"),
        "Variable Kosten gesamt": (var_kosten_gesamt, "€"),
        "Deckungsbeitrag je Stück": (db_stueck, "€"),
        "Deckungsbeitrag gesamt": (db_gesamt, "€"),
        "DB-Quote": (db_quote, "%"),
        "Betriebsergebnis": (betriebsergebnis, "€")
    }


def rechne_break_even(werte):
    db_stueck = werte["preis_stueck"] - werte["var_kosten_stueck"]
    db_gesamt = werte["absatzmenge"] * db_stueck
    betriebsergebnis = db_gesamt - werte["fixkosten"]

    break_even_menge = werte["fixkosten"] / db_stueck
    break_even_umsatz = break_even_menge * werte["preis_stueck"]
    sicherheitsstrecke = werte["absatzmenge"] - break_even_menge
    sicherheitskoeffizient = sicherheitsstrecke / werte["absatzmenge"]
    operating_leverage = db_gesamt / betriebsergebnis

    return {
        "Break-Even-Menge": (break_even_menge, "Stück"),
        "Break-Even-Umsatz": (break_even_umsatz, "€"),
        "Sicherheitsstrecke": (sicherheitsstrecke, "Stück"),
        "Sicherheitskoeffizient": (sicherheitskoeffizient, "%"),
        "Operating Leverage": (operating_leverage, "")
    }


def rechne_roi(werte):
    roi_umsatz = werte["umsatz"]
    roi_betriebsergebnis = werte["betriebsergebnis"]
    roi_gesamtkapital = werte["gesamtkapital"]

    umsatzrentabilitaet = roi_betriebsergebnis / roi_umsatz
    kapitalumschlag = roi_umsatz / roi_gesamtkapital
    roi = umsatzrentabilitaet * kapitalumschlag

    return {
        "Umsatzrentabilität": (umsatzrentabilitaet, "%"),
        "Kapitalumschlag": (kapitalumschlag, ""),
        "Return on Investment": (roi, "%")
    }


def rechne_kapitalstruktur(werte):
    gesamtkapital = werte["eigenkapital"] + werte["fremdkapital"]
    eigenkapitalquote = werte["eigenkapital"] / gesamtkapital
    verschuldungsgrad = werte["fremdkapital"] / werte["eigenkapital"]

    return {
        "Gesamtkapital": (gesamtkapital, "€"),
        "Eigenkapitalquote": (eigenkapitalquote, "%"),
        "Verschuldungsgrad": (verschuldungsgrad, "%")
    }


def rechne_liquidität(werte):
    cashflow = werte["jahresueberschuss"] + werte["abschreibungen"]
    working_capital = werte["umlaufvermoegen"] - werte["kurzfristige_verbindlichkeiten"]
    liquiditaet_3 = werte["umlaufvermoegen"] / werte["kurzfristige_verbindlichkeiten"]

    return {
        "Cashflow": (cashflow, "€"),
        "Working Capital": (working_capital, "€"),
        "Liquidität 3. Grades": (liquiditaet_3, "%")
    }


RECHNUNGEN = [
    ("Deckungsbeitragsrechnung",
     {"absatzmenge", "preis_stueck", "var_kosten_stueck", "fixkosten"},
     rechne_deckungsbeitrag),
    ("Break-Even-Analyse",
     {"absatzmenge", "preis_stueck", "var_kosten_stueck", "fixkosten"},
     rechne_break_even),
    ("ROI / DuPont", {"umsatz", "betriebsergebnis", "gesamtkapital"}, rechne_roi),
    ("Kapitalstruktur", {"eigenkapital", "fremdkapital"}, rechne_kapitalstruktur),
    ("Liquidität", {"jahresueberschuss", "abschreibungen", "umlaufvermoegen", "kurzfristige_verbindlichkeiten"}, rechne_liquidität),
]


def fuehre_rechnungen_aus(werte):
    ergebnisse = []
    fehlt = []
    vorhanden = set(werte)
    for name, benoetigt, funktion in RECHNUNGEN:
        if benoetigt <= vorhanden:
            try:
                ergebnisse.append((name, funktion(werte)))
            except ZeroDivisionError:
                fehlt.append(f"{name} (Division durch Null)")
        else:
            fehlt.append(f"{name} (braucht {', '.join(sorted(benoetigt - vorhanden))})")
    return ergebnisse, fehlt


def zeige_ergebnis(name, ergebnis):
    print()
    print(f"{name}:")
    for bezeichnung, (wert, einheit) in ergebnis.items():
        print(f"  {bezeichnung + ':':28} {formatiere_betrag(wert, einheit):>18}")


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
