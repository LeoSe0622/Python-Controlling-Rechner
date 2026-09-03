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


def formatiere_wert(wert, einheit="€"):
    if einheit == "%":
        wert = wert * 100
    text = f"{wert:,.2f}"
    text = text.replace(",", "X").replace(".", ",").replace("X", ".")
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


def rechne_investition_statisch(werte):
    anschaffungswert = werte["anschaffungswert"]
    restwert = werte["restwert"]
    nutzungsdauer = werte["nutzungsdauer"]
    kalkulationszinssatz = werte["kalkulationszinssatz"]
    jaehrlicher_gewinn = werte["jaehrlicher_gewinn"]

    abschreibung = (anschaffungswert - restwert) / nutzungsdauer
    durchschnittskapital = (anschaffungswert + restwert) / 2
    kalk_zinsen = durchschnittskapital * kalkulationszinssatz
    rentabilitaet = (jaehrlicher_gewinn + kalk_zinsen) / durchschnittskapital
    rueckfluss = jaehrlicher_gewinn + abschreibung
    amortisationsdauer = anschaffungswert / rueckfluss

    return {
        "Abschreibung p.a.": (abschreibung, "€"),
        "Durchschnittlich gebundenes Kapital": (durchschnittskapital, "€"),
        "Kalkulatorische Zinsen p.a.": (kalk_zinsen, "€"),
        "Rentabilität": (rentabilitaet, "%"),
        "Jährlicher Rückfluss": (rueckfluss, "€"),
        "Amortisationsdauer": (amortisationsdauer, "Jahre")
    }



def sammle_zahlungen(werte):
    zahlungen = []
    t = 0
    while f"zahlung_{t}" in werte:
        zahlungen.append(werte[f"zahlung_{t}"])
        t += 1
    return zahlungen


def rechne_investition_dynamisch(werte):
    zahlungen = sammle_zahlungen(werte)
    i = werte["kalkulationszinssatz"]

    kapitalwert = 0
    for t,zahlung in enumerate(zahlungen):
        kapitalwert += zahlung / (1 + i) ** t

    n = len(zahlungen) - 1
    kfr = (i * (1 + i) ** n) / ((1 + i) ** n - 1)
    annuitaet = kapitalwert * kfr

    return {    "Kapitalwert":            (kapitalwert, "€"),
                "Annuität":               (annuitaet, "€"),
                "Anzahl Perioden":        (n, "Jahre")
    }


def rechne_abweichungsanalyse(werte): 
    plan_menge = werte["plan_menge"]
    plan_preis = werte["plan_preis"]
    ist_menge = werte["ist_menge"]
    ist_preis = werte["ist_preis"]

    plankosten = plan_menge * plan_preis
    istkosten = ist_menge * ist_preis
    gesamtabweichung = istkosten - plankosten
    preisabweichung = (ist_preis - plan_preis) * ist_menge
    verbrauchsabweichung = (ist_menge - plan_menge) * plan_preis

    return {
        "Plankosten": (plankosten, "€"),
        "Istkosten": (istkosten, "€"),
        "Gesamtabweichung": (gesamtabweichung, "€"),
        "Preisabweichung": (preisabweichung, "€"),
        "Verbrauchsabweichung": (verbrauchsabweichung, "€")
    }


def rechne_plankosten(werte):
    plan_beschaeftigung = werte["plan_beschaeftigung"]
    ist_beschaeftigung = werte["ist_beschaeftigung"]
    plan_fixkosten = werte["plan_fixkosten"]
    plan_var_kosten_je_einheit = werte["plan_var_kosten_je_einheit"]
    ist_kosten = werte["ist_kosten"]

    plankosten = plan_fixkosten + plan_var_kosten_je_einheit * plan_beschaeftigung
    verrechnungssatz = plankosten / plan_beschaeftigung
    verrechnete = verrechnungssatz * ist_beschaeftigung
    sollkosten = plan_fixkosten + plan_var_kosten_je_einheit * ist_beschaeftigung
    gesamtabweichung = ist_kosten - verrechnete
    verbrauchsabw = ist_kosten - sollkosten
    beschaeftigungsabw = sollkosten - verrechnete

    return {
        "Plankosten": (plankosten, "€"),
        "Plankostenverrechnungssatz": (verrechnungssatz, "€"),
        "Verrechnete Plankosten": (verrechnete, "€"),
        "Sollkosten": (sollkosten, "€"),
        "Gesamtabweichung": (gesamtabweichung, "€"),
        "Verbrauchsabweichung": (verbrauchsabw, "€"),
        "Beschäftigungsabweichung": (beschaeftigungsabw, "€")
    }


def rechne_kostenarten(werte):
    materialkosten = werte["materialkosten"]
    personalkosten = werte["personalkosten"]
    abschreibungen = werte["abschreibungen"]
    sonstige_kosten = werte["sonstige_kosten"]

    gesamtkosten = materialkosten + personalkosten + abschreibungen + sonstige_kosten
    materialanteil = materialkosten / gesamtkosten
    personalanteil = personalkosten / gesamtkosten
    abschreibungsanteil = abschreibungen / gesamtkosten
    sonstige_anteil = sonstige_kosten / gesamtkosten

    return {
        "Gesamtkosten": (gesamtkosten, "€"),
        "Materialanteil": (materialanteil, "%"),
        "Personalanteil": (personalanteil, "%"),
        "Abschreibungsanteil": (abschreibungsanteil, "%"),
        "Sonstige Kosten Anteil": (sonstige_anteil, "%")
    }


def rechne_zuschlagssaetze(werte):
    fertigungsmaterial = werte["fertigungsmaterial"]
    materialgemeinkosten = werte["materialgemeinkosten"]
    fertigungsloehne = werte["fertigungsloehne"]
    fertigungsgemeinkosten = werte["fertigungsgemeinkosten"]
    verwaltungsgemeinkosten = werte["verwaltungsgemeinkosten"]
    vertriebsgemeinkosten = werte["vertriebsgemeinkosten"]

    materialkosten = fertigungsmaterial + materialgemeinkosten
    fertigungskosten = fertigungsloehne + fertigungsgemeinkosten
    herstellkosten = materialkosten + fertigungskosten

    mgk_satz = materialgemeinkosten / fertigungsmaterial
    fgk_satz = fertigungsgemeinkosten / fertigungsloehne
    vwgk_satz = verwaltungsgemeinkosten / herstellkosten
    vtgk_satz = vertriebsgemeinkosten / herstellkosten

    return {
        "Materialkosten": (materialkosten, "€"),
        "Fertigungskosten": (fertigungskosten, "€"),
        "Herstellkosten": (herstellkosten, "€"),
        "Materialgemeinkostenzuschlag": (mgk_satz, "%"),
        "Fertigungsgemeinkostenzuschlag": (fgk_satz, "%"),
        "Verwaltungsgemeinkostenzuschlag": (vwgk_satz, "%"),
        "Vertriebsgemeinkostenzuschlag": (vtgk_satz, "%")
    }


def rechne_kalkulation(werte):
    fm_stueck = werte["fertigungsmaterial_stueck"]
    fl_stueck = werte["fertigungsloehne_stueck"]
    mgk_satz = werte["mgk_satz"]
    fgk_satz = werte["fgk_satz"]
    vwgk_satz = werte["vwgk_satz"]
    vtgk_satz = werte["vtgk_satz"]
    gewinnzuschlag = werte["gewinnzuschlag"]

    materialkosten = fm_stueck * (1 + mgk_satz)
    fertigungskosten = fl_stueck * (1 + fgk_satz)
    herstellkosten = materialkosten + fertigungskosten
    selbstkosten = herstellkosten * (1 + vwgk_satz + vtgk_satz)
    gewinn = selbstkosten * gewinnzuschlag
    barverkaufspreis = selbstkosten + gewinn

    return {
        "Materialkosten": (materialkosten, "€"),
        "Fertigungskosten": (fertigungskosten, "€"),
        "Herstellkosten": (herstellkosten, "€"),
        "Selbstkosten": (selbstkosten, "€"),
        "Gewinn": (gewinn, "€"),
        "Barverkaufspreis": (barverkaufspreis, "€")
    }


def rechne_interner_zinsfuss(werte):
    zahlungen = sammle_zahlungen(werte)

    def kapitalwert_bei(zahlungen, i):
        return sum(zahlung / (1 + i) ** t for t, zahlung in enumerate(zahlungen))

    unten, oben = 0.0, 1.0
    for _ in range(100):
        mitte = (unten + oben) / 2
        if kapitalwert_bei(zahlungen, mitte) > 0:
            unten = mitte
        else:
            oben = mitte

    return {"Interner Zinsfuß": (mitte, "%")}


def rechne_make_or_buy(werte):
    var_kosten_stueck_eigen = werte["var_kosten_stueck_eigen"]
    fixkosten_eigen = werte["fixkosten_eigen"]
    bezugspreis_stueck = werte["bezugspreis_stueck"]
    menge = werte["menge"]

    eigenfertigung = fixkosten_eigen + var_kosten_stueck_eigen * menge
    fremdbezug = bezugspreis_stueck * menge
    vorteil = fremdbezug - eigenfertigung
    kritische_menge = fixkosten_eigen / (bezugspreis_stueck - var_kosten_stueck_eigen)

    return {
        "Eigenfertigungskosten": (eigenfertigung, "€"),
        "Fremdbezugskosten": (fremdbezug, "€"),
        "Vorteil Eigenfertigung": (vorteil, "€"),
        "Kritische Menge": (kritische_menge, "Stück")
    }


def rechne_prozesskosten(werte):
    prozesskosten_lmi = werte["prozesskosten_lmi"]
    prozesskosten_lmn = werte["prozesskosten_lmn"]
    prozessmenge = werte["prozessmenge"]

    lmi_satz = prozesskosten_lmi / prozessmenge
    umlagesatz = prozesskosten_lmn / prozesskosten_lmi
    gesamtsatz = lmi_satz * (1 + umlagesatz)

    return {
        "LMI-Satz": (lmi_satz, "€"),
        "Umlagesatz": (umlagesatz, "%"),
        "Gesamtsatz": (gesamtsatz, "€")
    }


def rechne_eva(werte):
    nopat = werte["nopat"]
    investiertes_kapital = werte["investiertes_kapital"]
    kapitalkostensatz = werte["kapitalkostensatz"]

    kapitalkosten = investiertes_kapital * kapitalkostensatz
    eva = nopat - kapitalkosten

    return {
        "Kapitalkosten": (kapitalkosten, "€"),
        "Economic Value Added": (eva, "€")
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
    ("Investitionsrechnung (statisch)", {"anschaffungswert", "restwert", "nutzungsdauer", "kalkulationszinssatz", "jaehrlicher_gewinn"}, rechne_investition_statisch),
    ("Investitionsrechnung (dynamisch)" , {"kalkulationszinssatz", "zahlung_0"},rechne_investition_dynamisch),
    ("Interner Zinsfuß", {"zahlung_0"}, rechne_interner_zinsfuss),
    ("Make-or-Buy",
     {"var_kosten_stueck_eigen", "fixkosten_eigen", "bezugspreis_stueck", "menge"},
     rechne_make_or_buy),
    ("Prozesskostenrechnung",
     {"prozesskosten_lmi", "prozesskosten_lmn", "prozessmenge"},
     rechne_prozesskosten),
    ("Economic Value Added",
     {"nopat", "investiertes_kapital", "kapitalkostensatz"},
     rechne_eva),
    ("Abweichungsanalyse (Material)",
     {"plan_menge", "plan_preis", "ist_menge", "ist_preis"},
     rechne_abweichungsanalyse),
    ("Plankostenrechnung (flexibel)",
     {"plan_beschaeftigung", "ist_beschaeftigung", "plan_fixkosten",
      "plan_var_kosten_je_einheit", "ist_kosten"},
     rechne_plankosten),
    ("Kostenartenrechnung",
     {"materialkosten", "personalkosten", "abschreibungen", "sonstige_kosten"},
     rechne_kostenarten),
    ("Zuschlagssätze (BAB)",
     {"fertigungsmaterial", "materialgemeinkosten", "fertigungsloehne",
      "fertigungsgemeinkosten", "verwaltungsgemeinkosten", "vertriebsgemeinkosten"},
     rechne_zuschlagssaetze),
    ("Zuschlagskalkulation",
     {"fertigungsmaterial_stueck", "fertigungsloehne_stueck", "mgk_satz",
      "fgk_satz", "vwgk_satz", "vtgk_satz", "gewinnzuschlag"},
     rechne_kalkulation),
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
        print(f"  {bezeichnung + ':':28} {formatiere_wert(wert, einheit):>18}")


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
    print(f"Größen: {', '.join(sorted(werte.keys()))}")
    print(f"{len(werte)} Werte gelesen")

    ergebnisse, fehlt = fuehre_rechnungen_aus(werte)

    for name, ergebnis in ergebnisse:
        zeige_ergebnis(name, ergebnis)
    zeige_liste("Nicht möglich:", fehlt)


if __name__ == "__main__":
    main()
