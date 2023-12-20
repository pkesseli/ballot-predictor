from bp.data.chronology import Chronology
from bp.entity.ballot import BallotStatus, DoubleMajorityBallot
from bp.entity.bill import Bill

import unittest
from datetime import datetime
from decimal import Decimal
from typing import List
from lxml import html


class TestChronology(unittest.TestCase):

    def test_get_initiatives(self):
        ballots: List[str] = Chronology.get_initiatives()
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

    def test_get_initiative_modern_accepted(self):
        ballot: DoubleMajorityBallot = Chronology.get_initiative(
            "https://www.bk.admin.ch/ch/d/pore/vi/vis484.html")
        self.assertEqual(
            "Ja zum Schutz der Kinder und Jugendlichen vor Tabakwerbung (Kinder und Jugendliche ohne Tabakwerbung)", ballot.bill.title)
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
^2 Die endgültige Ziffer dieser Übergangsbestimmung wird nach der Volksabstimmung von der Bundeskanzlei festgelegt.""", ballot.bill.wording)
        self.assertEqual(datetime(2018, 3, 20, 0, 0, 0, 0), ballot.bill.date)
        self.assertEqual(BallotStatus.COMPLETED, ballot.status)
        self.assertAlmostEqual(Decimal(56.7), ballot.result.percentage_yes, 2)
        self.assertAlmostEqual(Decimal(15), ballot.result.accepting_cantons, 2)

    def test_get_initiative_historic_accepted(self):
        ballot: DoubleMajorityBallot = Chronology.get_initiative(
            "https://www.bk.admin.ch/ch/d/pore/vi/vis1.html")
        self.assertEqual(
            "für ein Verbot des Schlachtens ohne vorherige Betäubung", ballot.bill.title)
        self.assertEqual("""Die Volksinitiative lautet:

Die Bundesverfassung wird wie folgt ergänzt:

Art. 25^bis (neu)

Das Schlachten der Tiere ohne vorherige Betäubung vor dem Blutentzuge ist bei jeder Schlachtart und Viehgattung ausnahmslos untersagt.""", ballot.bill.wording)
        self.assertEqual(datetime(1892, 5, 10, 0, 0, 0, 0), ballot.bill.date)
        self.assertEqual(BallotStatus.COMPLETED, ballot.status)
        self.assertAlmostEqual(Decimal(60.1), ballot.result.percentage_yes, 2)
        self.assertAlmostEqual(
            Decimal(11.5), ballot.result.accepting_cantons, 2)

    def test_get_initiative_modern_failed(self):
        ballot: DoubleMajorityBallot = Chronology.get_initiative(
            "https://www.bk.admin.ch/ch/d/pore/vi/vis523.html")
        self.assertEqual("Für eine neue Bundesverfassung", ballot.bill.title)
        self.assertEqual(
            "Die Bundesverfassung vom 18. April 1999^1 wird totalrevidiert.", ballot.bill.wording)
        self.assertEqual(datetime(2022, 4, 19, 0, 0, 0, 0), ballot.bill.date)
        self.assertEqual(BallotStatus.FAILED, ballot.status)
        self.assertIsNone(ballot.result)

    def test_get_initiative_modern_pending(self):
        ballot: DoubleMajorityBallot = Chronology.get_initiative(
            "https://www.bk.admin.ch/ch/d/pore/vi/vis556.html")
        self.assertEqual(
            "Für den wirksamen Schutz der verfassungsmässigen Rechte (Souveränitätsinitiative)", ballot.bill.title)
        self.assertEqual("""Die Bundesverfassung[1] wird wie folgt geändert:

Art. 54a^^[2]     Verhältnis von Völkerrecht und nationaler Souveränität

^1 Die Schweiz geht keine völkerrechtlichen Verpflichtungen ein, welche die rechtsetzenden, rechtsanwendenden oder rechtsprechenden Behörden von Bund, Kantonen oder Gemeinden infolge unmittelbarer Anwendbarkeit oder erforderlicher Umsetzung im nationalen Recht verpflichten, in den Schutzbereich von Grundrechten oder übrigen verfassungsmässigen Rechten natürlicher oder juristischer Personen einzugreifen, insbesondere durch sicherheits-, wirtschafts-, gesundheits- oder umweltrechtliche Vorschriften präventiver oder repressiver Natur.

^2 Sie geht zudem keine völkerrechtlichen Verpflichtungen ein, welche die schweizerischen Verwaltungs- oder Gerichtsbehörden direkt oder indirekt verpflichten, sich nach der Rechtsanwendung oder Rechtsprechung ausländischer oder inter- oder supranationaler Behörden oder Gerichte, ausgenommen des Internationalen Gerichtshofs und des Internationalen Strafgerichtshofs, zu richten oder sich einem Schiedsgericht zu unterwerfen.

^3 Steht eine völkerrechtliche Verpflichtung im Widerspruch zu den Vorgaben nach Absatz 1 oder 2 oder tritt ein solcher nachträglich ein, so sind sämtliche erforderlichen Gegenmassnahmen zu ergreifen, jeweils unter Einhaltung des Gebots der schonenden Rechtsausübung. Wo immer möglich, bringt die Schweiz in Bezug auf einzelne Bestimmungen Vorbehalte an, welche deren Geltung ganz oder teilweise ausschliessen oder deren Inhalt modifizieren. Sind im konkreten Fall keine solchen Vorbehalte zulässig, so kündigt die Schweiz ohne Verzug den zugrunde liegenden völkerrechtlichen Vertrag oder tritt aus der entsprechenden internationalen Organisation oder supranationalen Gemeinschaft aus.

^4 Die Absätze 1-3 sind nicht anwendbar auf:

a. die Konvention vom 4. November 1950[3]zum Schutze der Menschenrechte und Grundfreiheiten;

b. völkerrechtliche Verträge des internationalen Privatrechts, einschliesslich des Zivilverfahrensrechts;

c. völkerrechtliche Verträge über die internationale Rechtshilfe in Zivil- und Strafsachen;

d. völkerrechtliche Verträge in den Bereichen des Flug-, Strassen-, Schienen- oder Schiffsverkehrs, des Freihandels, des Asylrechts, des Steuerrechts und des Zollrechts;

e. nichtmilitärische Sanktionen der Vereinten Nationen; und

f. die zwingenden Bestimmungen des Völkerrechts.

Art. 190       Massgebendes Recht

^1 Bundesgesetze und völkerrechtliche Verträge, deren Genehmigungsbeschluss referendumsfähig gewesen ist, sind für das Bundesgericht und die anderen rechtsanwendenden Behörden massgebend, soweit dieser Artikel keine abweichenden Vorgaben enthält.

^2 Völkerrechtliche Bestimmungen, welche entgegen den Vorgaben in Artikel 54a Absätze 1-3 weiterhin in Kraft sind, insbesondere weil die Bundesversammlung oder der Bundesrat es bislang unterlassen haben oder dauerhaft unterlassen, die in Artikel 54a Absatz 3 vorgesehenen Gegenmassnahmen zu ergreifen, dürfen bei der Rechtsanwendung nicht berücksichtigt werden.

^3 Die völkerrechtlichen Verträge gemäss Artikel 54a Absatz 4 werden von allen rechtsanwendenden Behörden auf ihre Konformität mit den in der Bundesverfassung enthaltenen Grundrechten frei überprüft.

Art. 197 Ziff. 15^^[4]

15. Übergangsbestimmung zu den Art. 54a (Verhältnis von Völkerrecht und nationaler Souveränität) und 190 (Massgebendes Recht)

Mit ihrer Annahme durch Volk und Stände werden die Artikel 54a und 190 auf alle bestehenden und künftigen Bestimmungen der Verfassung sowie auf alle bestehenden und künftigen völkerrechtlichen Verpflichtungen von Bund, Kantonen und Gemeinden unmittelbar anwendbar.

[1]              SR 101

[2]              Die endgültige Nummerierung dieses Artikels wird nach der Volksabstimmung von der Bundeskanzlei festgelegt; dabei stimmt diese die Nummerierung ab auf die anderen geltenden Bestimmungen der Bundesverfassung und nimmt diese Anpassung im ganzen Text der Initiative vor.

[3]              SR 0.101

[4]      Die endgültige Ziffer dieser Übergangsbestimmung wird nach der Volksabstimmung von der Bundeskanzlei festgelegt.""", ballot.bill.wording)
        self.assertEqual(datetime(2023, 10, 17, 0, 0, 0, 0), ballot.bill.date)
        self.assertEqual(BallotStatus.PENDING, ballot.status)
        self.assertIsNone(ballot.result)

    def test_parse_canton_count(self):
        self.assertEqual(
            Decimal(7), Chronology._Chronology__parse_canton_count("7"))
        self.assertEqual(
            Decimal(5.5), Chronology._Chronology__parse_canton_count("4 3/2"))
