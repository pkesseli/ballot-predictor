from bp.data.chronology import Chronology, POPULAR_INITIATIVES_CHRONOLOGY
from bp.entity.bill import Bill

import unittest
from datetime import datetime
from typing import List
from lxml import html


class TestChronology(unittest.TestCase):

    def test_get_bills(self):
        chronology = Chronology(POPULAR_INITIATIVES_CHRONOLOGY)
        ballots: List[str] = chronology.get_bills()
        for ballot in ballots:
            self.assertRegex(
                ballot, "https://www.bk.admin.ch/ch/d/pore/vi/vis\d+.html")

    def test_extract_title_invalid(self):
        page: html.HtmlElement = html.fromstring("""
            <div class='contentHead'>
                <h2>Eidgenössische Volksinitiative Ja zum Schutz der Kinder und Jugendlichen vor Tabakwerbung (Kinder und Jugendliche ohne Tabakwerbung)</h2>
            </div>
            """)
        with self.assertRaises(ValueError):
            Chronology._Chronology__extract_title(page)

    def test_get_bill_modern_accepted(self):
        bill: Bill = Chronology.get_bill(
            "https://www.bk.admin.ch/ch/d/pore/vi/vis484.html")
        self.assertEqual(
            "Ja zum Schutz der Kinder und Jugendlichen vor Tabakwerbung (Kinder und Jugendliche ohne Tabakwerbung)", bill.title)
        self.assertEqual("""Die Bundesverfassung^1 wird wie folgt geändert:

Art. 41 Abs. 1 Bst. g

^1 Bund und Kantone setzen sich in Ergänzung zu persönlicher Verantwortung und privater Initiative dafür ein, dass:

g. Kinder und Jugendliche in ihrer Entwicklung zu selbstständigen und sozial verantwortlichen Personen gefördert und in ihrer sozialen, kulturellen und politischen Integration unterstützt werden sowie ihre Gesundheit gefördert wird.

Art. 118 Abs. 2 Bst. b

^2 Er erlässt Vorschriften über:

b. die Bekämpfung übertragbarer, stark verbreiteter oder bösartiger Krankheiten von Menschen und Tieren; er verbietet namentlich jede Art von Werbung für Tabakprodukte, die Kinder und Jugendliche erreicht;

Art. 197 Ziff. 12^2
12. Übergangsbestimmung zu Art. 118 Abs. 2 Bst. b (Schutz der Gesundheit)

Die Bundesversammlung verabschiedet die gesetzlichen Ausführungsbestimmungen innert drei Jahren seit Annahme von Artikel 118 Absatz 2 Buchstabe b durch Volk und Stände.

^1 SR 101
^2 Die endgültige Ziffer dieser Übergangsbestimmung wird nach der Volksabstimmung von der Bundeskanzlei festgelegt.""", bill.wording)
        self.assertEqual(datetime(2018, 3, 20, 0, 0, 0, 0), bill.date)

    def test_get_bill_historic_accepted(self):
        bill: Bill = Chronology.get_bill(
            "https://www.bk.admin.ch/ch/d/pore/vi/vis1.html")
        self.assertEqual(
            "für ein Verbot des Schlachtens ohne vorherige Betäubung", bill.title)
        self.assertEqual("""Die Volksinitiative lautet:

Die Bundesverfassung wird wie folgt ergänzt:

Art. 25^bis (neu)

Das Schlachten der Tiere ohne vorherige Betäubung vor dem Blutentzuge ist bei jeder Schlachtart und Viehgattung ausnahmslos untersagt.""", bill.wording)
        self.assertEqual(datetime(1892, 5, 10, 0, 0, 0, 0), bill.date)
