"""Automatische Tests für kennzahlen.py.

Aufruf (im Projektordner):
    python -m unittest

Oder mit mehr Ausgabe:
    python -m unittest -v
"""
import os
import subprocess
import sys
import unittest

import kennzahlen


# Eingabewerte, die in mehreren Tests gebraucht werden.
DB_WERTE = {
    "absatzmenge": 5000.0,
    "preis_stueck": 80.0,
    "var_kosten_stueck": 48.0,
    "fixkosten": 120000.0,
}


class TestDeckungsbeitrag(unittest.TestCase):
    """Vollstaendiges Beispiel - daran orientieren sich die TODOs unten."""

    def test_umsatz(self):
        ergebnis = kennzahlen.rechne_deckungsbeitrag(DB_WERTE)
        wert, einheit = ergebnis["Umsatz"]
        self.assertAlmostEqual(wert, 400000.0, places=2)
        self.assertEqual(einheit, "€")

    def test_db_stueck(self):
        ergebnis = kennzahlen.rechne_deckungsbeitrag(DB_WERTE)
        wert, _ = ergebnis["Deckungsbeitrag je Stück"]
        self.assertAlmostEqual(wert, 32.0, places=2)

    def test_db_quote(self):
        ergebnis = kennzahlen.rechne_deckungsbeitrag(DB_WERTE)
        wert, einheit = ergebnis["DB-Quote"]
        self.assertAlmostEqual(wert, 0.40, places=4)
        self.assertEqual(einheit, "%")

    def test_betriebsergebnis(self):
        ergebnis = kennzahlen.rechne_deckungsbeitrag(DB_WERTE)
        wert, _ = ergebnis["Betriebsergebnis"]
        self.assertAlmostEqual(wert, 40000.0, places=2)


class TestBreakEven(unittest.TestCase):
    def test_break_even(self):
        menge, _ = kennzahlen.rechne_break_even(DB_WERTE)["Break-Even-Menge"]
        self.assertAlmostEqual(menge, 3750.0, places=2)


class TestKennzahlen(unittest.TestCase):
    def test_kennzahlen(self):
        roi_werte = {
            "umsatz": 400000.0,
            "betriebsergebnis": 40000.0,
            "gesamtkapital": 250000.0
        }
        kapitalstruktur_werte = {
            "eigenkapital": 100000.0,
            "fremdkapital": 150000.0
        }
        liquiditaet_werte = {
            "jahresueberschuss": 28000.0,
            "abschreibungen": 35000.0,
            "umlaufvermoegen": 120000.0,
            "kurzfristige_verbindlichkeiten": 80000.0
        }

        roi_ergebnis = kennzahlen.rechne_roi(roi_werte)
        self.assertAlmostEqual(roi_ergebnis["Umsatzrentabilität"][0], 0.10, places=2)
        self.assertAlmostEqual(roi_ergebnis["Kapitalumschlag"][0], 1.6, places=2)
        self.assertAlmostEqual(roi_ergebnis["Return on Investment"][0], 0.16, places=2)

        kapitalstruktur_ergebnis = kennzahlen.rechne_kapitalstruktur(kapitalstruktur_werte)
        self.assertAlmostEqual(kapitalstruktur_ergebnis["Gesamtkapital"][0], 250000.0, places=2)
        self.assertAlmostEqual(kapitalstruktur_ergebnis["Eigenkapitalquote"][0], 0.40, places=2)
        self.assertAlmostEqual(kapitalstruktur_ergebnis["Verschuldungsgrad"][0], 1.50, places=2)

        liquiditaet_ergebnis = kennzahlen.rechne_liquidität(liquiditaet_werte)
        self.assertAlmostEqual(liquiditaet_ergebnis["Cashflow"][0], 63000.0, places=2)
        self.assertAlmostEqual(liquiditaet_ergebnis["Working Capital"][0], 40000.0, places=2)
        self.assertAlmostEqual(liquiditaet_ergebnis["Liquidität 3. Grades"][0], 1.50, places=2)


class TestInvestition(unittest.TestCase):
    def test_investitionen(self):
        statische_werte = {
            "anschaffungswert": 100000.0,
            "restwert": 20000.0,
            "nutzungsdauer": 5,
            "kalkulationszinssatz": 0.08,
            "jaehrlicher_gewinn": 12000.0
        }
        dynamische_werte = {
            "kalkulationszinssatz": 0.08,
            "zahlung_0": -100000.0,
            "zahlung_1": 30000.0,
            "zahlung_2": 30000.0,
            "zahlung_3": 30000.0,
            "zahlung_4": 40000.0
        }

        statisches_ergebnis = kennzahlen.rechne_investition_statisch(statische_werte)
        self.assertAlmostEqual(statisches_ergebnis["Abschreibung p.a."][0], 16000.0, places=2)
        self.assertAlmostEqual(statisches_ergebnis["Rentabilität"][0], 0.28, places=2)
        self.assertAlmostEqual(statisches_ergebnis["Amortisationsdauer"][0], 3.57142857, places=2)

        dynamisches_ergebnis = kennzahlen.rechne_investition_dynamisch(dynamische_werte)
        self.assertAlmostEqual(dynamisches_ergebnis["Kapitalwert"][0], 6714.10, places=2)
        self.assertAlmostEqual(dynamisches_ergebnis["Annuität"][0], 2027.13, places=2)

        zahlungen = kennzahlen.sammle_zahlungen(dynamische_werte)
        self.assertEqual(zahlungen, [-100000.0, 30000.0, 30000.0, 30000.0, 40000.0])

    # TODO 34 - Klasse TestFormatierung fuer formatiere_wert.
    #   Hier passt assertEqual, weil das Ergebnis ein String ist:
    #       formatiere_wert(1234.56)         ->  "1.234,56 €"
    #       formatiere_wert(0.4, "%")        ->  "40,00 %"
    #       formatiere_wert(3750.0, "Stück") ->  "3.750,00 Stück"
    #       formatiere_wert(-1250.0)         ->  "-1.250,00 €"
    #
    #   Der letzte Fall ist der interessante: negative Betraege durch die
    #   replace-Kette zu schicken hat noch nie jemand geprueft.


class TestFormatierung(unittest.TestCase):
    def test_formatierung(self):
        self.assertEqual(kennzahlen.formatiere_wert(1234.56), "1.234,56 €")
        self.assertEqual(kennzahlen.formatiere_wert(0.4, "%"), "40,00 %")
        self.assertEqual(kennzahlen.formatiere_wert(3750.0, "Stück"), "3.750,00 Stück")
        self.assertEqual(kennzahlen.formatiere_wert(-1250.0), "-1.250,00 €")

    # TODO 35 - Klasse TestLadeWerte fuer das Einlesen.
    #   Hier werden die Dateien aus tests/ benutzt.
    #
    #   a) Erfolgsfall: lade_werte("tests/01_deckungsbeitrag.csv") muss ein
    #      Dictionary mit vier Eintraegen liefern, absatzmenge davon 5000.0.
    #
    #   b) Tausendertrenner: lade_werte("tests/10_tausendertrenner.csv")
    #      muss aus "5.000" die Zahl 5000.0 und aus "1.234,56" die Zahl 1234.56 machen.
    #
    #   c) Fehlerfaelle - hier pruefst du, dass eine Ausnahme FLIEGT:
    #          with self.assertRaises(kennzahlen.CsvFehler):
    #              kennzahlen.lade_werte("tests/07_leer.csv")
    #      Genauso fuer 08_falsches_format.csv, 09_ungueltiger_wert.csv
    #      und einen Pfad, den es nicht gibt.
    #
    #      assertRaises kehrt die Logik um: Der Test besteht, WENN die Ausnahme
    #      kommt - und schlaegt fehl, wenn der Aufruf klaglos durchlaeuft.


class TestLadeWerte(unittest.TestCase):
    def test_lade_werte(self):
        werte = kennzahlen.lade_werte("tests/01_deckungsbeitrag.csv")
        self.assertEqual(werte["absatzmenge"], 5000.0)

        werte = kennzahlen.lade_werte("tests/10_tausendertrenner.csv")
        self.assertEqual(werte["absatzmenge"], 5000.0)
        self.assertEqual(werte["preis_stueck"], 1234.56)

        with self.assertRaises(kennzahlen.CsvFehler):
            kennzahlen.lade_werte("tests/07_leer.csv")

        with self.assertRaises(kennzahlen.CsvFehler):
            kennzahlen.lade_werte("tests/08_falsches_format.csv")

        with self.assertRaises(kennzahlen.CsvFehler):
            kennzahlen.lade_werte("tests/09_ungueltiger_wert.csv")

        with self.assertRaises(kennzahlen.CsvFehler):
            kennzahlen.lade_werte("tests/gibtsnicht.csv")

    # TODO 36 - Klasse TestKommandozeile - das Programm als Ganzes aufrufen.
    #   Das ersetzt, was ich bisher jede Runde von Hand gemacht habe.
    #
    #   Eine Hilfsmethode, die das Programm startet und das Ergebnis zurueckgibt:
    #       def starte(self, *argumente):
    #           return subprocess.run([sys.executable, "kennzahlen.py", *argumente],
    #                                 capture_output=True, text=True, encoding="utf-8")
    #
    #   Damit dann pruefen:
    #       04_alles.csv          -> returncode 0, "Nicht möglich:" ohne Eintraege darunter
    #       01_deckungsbeitrag.csv-> returncode 0, "Deckungsbeitragsrechnung" in der Ausgabe
    #       06_nulldivision.csv   -> returncode 0, "Division durch Null" in der Ausgabe
    #       07_leer.csv           -> returncode 1
    #       gibtsnicht.csv        -> returncode 1
    #       ohne Argument         -> returncode 2
    #
    #   Zugriff auf das Ergebnis: .returncode, .stdout, .stderr
    #   Fuer "steht das im Text": self.assertIn("Deckungsbeitragsrechnung", ergebnis.stdout)
    #
    #   sys.executable ist der Pfad zum laufenden Python - so wird garantiert
    #   dieselbe Version benutzt wie fuer die Tests.


class TestKommandozeile(unittest.TestCase):
    def test_kommandozeile(self):
        def starte(*argumente):
            # PYTHONIOENCODING zwingt das Kindprogramm, UTF-8 zu schreiben.
            # Ohne das benutzt es unter Windows cp1252 und "Nicht möglich"
            # laesst sich hier nicht als UTF-8 dekodieren.
            umgebung = {**os.environ, "PYTHONIOENCODING": "utf-8"}
            return subprocess.run([sys.executable, "kennzahlen.py", *argumente],
                                  capture_output=True, text=True,
                                  encoding="utf-8", env=umgebung)

        ergebnis = starte("tests/04_alles.csv")
        self.assertEqual(ergebnis.returncode, 0)
        self.assertIn("Nicht möglich:", ergebnis.stdout)

        ergebnis = starte("tests/01_deckungsbeitrag.csv")
        self.assertEqual(ergebnis.returncode, 0)
        self.assertIn("Deckungsbeitragsrechnung", ergebnis.stdout)

        ergebnis = starte("tests/06_nulldivision.csv")
        self.assertEqual(ergebnis.returncode, 0)
        self.assertIn("Division durch Null", ergebnis.stdout)

        ergebnis = starte("tests/07_leer.csv")
        self.assertEqual(ergebnis.returncode, 1)

        ergebnis = starte("tests/gibtsnicht.csv")
        self.assertEqual(ergebnis.returncode, 1)

        ergebnis = starte()
        self.assertEqual(ergebnis.returncode, 2)


class TestRegister(unittest.TestCase):
    """Prüft das Register selbst, nicht einzelne Formeln."""

    def test_jede_rechenfunktion_ist_eingetragen(self):
        """Eine geschriebene, aber nicht eingetragene Funktion wird nie aufgerufen."""
        eingetragen = {funktion for _, _, funktion in kennzahlen.RECHNUNGEN}
        geschrieben = {
            getattr(kennzahlen, name)
            for name in dir(kennzahlen)
            if name.startswith("rechne_")
        }
        vergessen = sorted(f.__name__ for f in geschrieben - eingetragen)
        self.assertEqual(vergessen, [], f"nicht im Register: {vergessen}")

    def test_namen_sind_eindeutig(self):
        namen = [name for name, _, _ in kennzahlen.RECHNUNGEN]
        self.assertEqual(len(namen), len(set(namen)))

    def test_alles_csv_laesst_jede_rechnung_laufen(self):
        """tests/04_alles.csv muss alle Größen enthalten, die irgendeine Rechnung braucht."""
        werte = kennzahlen.lade_werte("tests/04_alles.csv")
        ergebnisse, fehlt = kennzahlen.fuehre_rechnungen_aus(werte)
        self.assertEqual(fehlt, [], f"nicht berechenbar: {fehlt}")
        self.assertEqual(len(ergebnisse), len(kennzahlen.RECHNUNGEN))

    def test_ergebnisse_haben_wert_und_einheit(self):
        """Jede Rechnung muss {Bezeichnung: (Zahl, Einheit)} liefern."""
        werte = kennzahlen.lade_werte("tests/04_alles.csv")
        for name, _, funktion in kennzahlen.RECHNUNGEN:
            with self.subTest(rechnung=name):
                for bezeichnung, paar in funktion(werte).items():
                    self.assertEqual(len(paar), 2, f"{name} / {bezeichnung}")
                    wert, einheit = paar
                    self.assertIsInstance(wert, (int, float))
                    self.assertIsInstance(einheit, str)


if __name__ == "__main__":
    unittest.main()
