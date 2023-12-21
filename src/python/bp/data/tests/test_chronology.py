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
            Chronology._Chronology__extract_title(
                "http://www.example.com/", page)

    def test_extract_title_unexpected_tag(self):
        page: html.HtmlElement = html.fromstring("""
            <div class='contentHead'>
                <h3>Eidgenössische Volksinitiative 'Ja zum Schutz der Kinder und Jugendlichen vor Tabakwerbung (Kinder und Jugendliche ohne Tabakwerbung)'</h3>
            </div>
            """)
        with self.assertRaises(ValueError):
            Chronology._Chronology__extract_title(
                "http://www.example.com/", page)

    def test_parse_canton_count(self):
        self.assertEqual(
            Decimal(7), Chronology._Chronology__parse_canton_count("7"))
        self.assertEqual(
            Decimal(5.5), Chronology._Chronology__parse_canton_count("4 3/2"))

    def test_find_result_table_no_match(self):
        page: html.HtmlElement = html.fromstring("<p></p>")
        self.assertIsNone(Chronology._Chronology__find_result_table(page, "unknown bill"))

    def test_find_result_table_inconclusive(self):
        page: html.HtmlElement = html.fromstring("""
            <div class='mod-text'>
                <h3>Volksbegehren 'zur Steuerharmonisierung, zur stärkeren Besteuerung des Reichtums und zur Entlastung der unteren Einkommen (Reichtumsteuer-Initiative)'</h3>
                <h3>Bundesgesetz vom 17.12.1976 über die politischen Rechte</h3>
                <h3>Bundesbeschluss vom 05.05.1977 über die Einführung eines zivilen Ersatzdienstes</h3>
                <h3>Bundesgesetz vom 05.05.1977 über Massnahmen zum Ausgleich des Bundeshaushaltes</h3>
                <h3>Regierungsunterstützung</h3>
                <h3>Politische Rechte</h3>
                <h3>Dokumentation</h3>
                <h3>Über die Bundeskanzlei</h3>
            </div>
            """)
        with self.assertRaises(ValueError):
            Chronology._Chronology__find_result_table(page, "Für eine Reichtumssteuer")

    def test_extract_accepting_cantons_incomplete_info_on_website(self):
        self.assertEqual(Decimal(0), Chronology._Chronology__extract_accepting_cantons("Bekämpfung des Alkoholismus", None))
        self.assertEqual(Decimal(8.5), Chronology._Chronology__extract_accepting_cantons("Neuordnung des Alkoholwesens", None))
        self.assertEqual(Decimal(3), Chronology._Chronology__extract_accepting_cantons("Totalrevision der Bundesverfassung", None))

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

    def test_get_initiative_bug_545(self):
        ballot: DoubleMajorityBallot = Chronology.get_initiative(
            "https://www.bk.admin.ch/ch/d/pore/vi/vis545.html")
        self.assertEqual(
            "Aufarbeitung der Hintergründe der Covid-19-Pandemie (Aufarbeitungsinitiative)", ballot.bill.title)
        self.assertEqual("""Die Bundesverfassung[1] wird wie folgt geändert:

Einfügen vor dem Gliederungstitel des 6. Titels:

5. Kapitel: Behörden zur Aufarbeitung der Hintergründe der Covid-19-Pandemie

Art. 191d        Gründung einer schweizerischen Untersuchungskommission

Zur Untersuchung der Hintergründe der Covid-19-Pandemie wird eine ausserparlamentarische schweizerische Untersuchungskommission gegründet.

Art. 191e         Allgemeine Aufgaben der Kommission

^1 Die Kommission nimmt ihre Arbeit nach Annahme der Artikel 191d-191r durch Volk und Stände so schnell wie möglich auf und untersucht die Hintergründe der von der Weltgesundheitsorganisation ausgerufenen Covid-19-Pandemie.

^2 Sämtliche Kosten, die der Kommission in Zusammenhang mit ihrer Aufgabenerfüllung entstehen, gehen zulasten der Schweizerischen Eidgenossenschaft.

^3 Zu den Aufgaben der Kommission gehört insbesondere die Beantwortung der nachfolgenden Fragen:

1. Können die angewandten Tests, welche die Grundlage der Covid-19-Massnahmen in der Schweiz bilden oder bildeten, sicher zwischen Sars-CoV-2-Viren und anderen Viren unterscheiden oder ist eine solche sichere Unterscheidung nicht nachgewiesen?
2. Können oder konnten die angewandten Tests mit Sicherheit das infektiöse Sars-CoV-2-Virus von nicht vermehrungsfähigen Bruchstücken des Virus unterscheiden?
3. Wurden die angewandten Tests immer nach gleichen Vorgaben, zum Beispiel bezüglich der Anzahl Amplifikationen, durchgeführt und waren die Tests geeicht und validiert?
4. Kann nachgewiesen werden, dass asymptomatische, sich gesund fühlende Personen epidemiologisch signifikant für die Verbreitung von Sars-CoV-2-Viren sind oder waren, oder hatten die Entscheidungsträgerinnen und Entscheidungsträger die Massnahmen ohne hinreichende wissenschaftliche Grundlagen angeordnet?
5. Wie viele Intensivpflegekapazitäten waren nach 2019 im Vergleich zu den Vorjahren tatsächlich vorhanden und wie war deren Auslastung im Vergleich zu früheren Jahren?
6. Waren die Massnahmen notwendig und geeignet, um eine Überlastung von Intensivpflegekapazitäten zu verhindern, und waren die dadurch bewirkten Einschränkungen der Grundrechte und Menschenrechte, insbesondere wirtschaftliche und soziale Schäden, angemessen im Vergleich zum beweisbaren Nutzen?
7. Sind die zu Beginn des Jahres 2020 prognostizierten Sterblichkeitsraten aufgrund von Sars-CoV-2-Viren und die anderen Vorhersagen zum Verlauf der Covid-19-Pandemie eingetreten? Falls nicht: Konnten sich die verantwortlichen Personen auf damals tatsächlich existierende, wissenschaftlich hinreichende Grundlagen für die getätigten Prognosen stützen?
8. Wurde die Bevölkerung der Schweiz in transparenter Weise laufend über die bekannten Auswirkungen der Covid-19-Impfungen aufgeklärt oder gibt es Beweise dafür, dass die Bevölkerung der Schweiz fahrlässig oder vorsätzlich unzutreffend oder unzureichend informiert wurde? Gab es in irgendeiner Form Verstösse gegen den Nürnberger Codex?

^4 Die Kommission ist verpflichtet, einen Bericht über das Ergebnis der Untersuchungen zu den Hintergründen und den tatsächlich vorgefallenen Sachverhalten im Zusammenhang mit der Covid-19-Pandemie, insbesondere auch nach Artikel 191q, zu erstellen und zu veröffentlichen.

Art. 191f       Besondere Aufgaben der Kommission für eine würdige Entschädigung von Personen mit Covid-19-Impfschäden

^1 Die Kommission stellt die Covid-19-Impfschäden unabhängig und uneingeschränkt fest und wahrt dabei die Interessen der geschädigten Personen. Jede Person ist der Kommission gegenüber auskunftspflichtig. Vereinbarungen zu Beschaffungen von Covid-19-Impfstoffen sind bei Annahme der Artikel 191d-191r durch Volk und Stände sofort vollständig und unverändert durch den Bundesrat zu veröffentlichen. Die Kommission informiert die Öffentlichkeit transparent über die Arten von Impfschäden und ihr tatsächliches Ausmass in Zahlen.

^2 Die Hersteller der Impfstoffe sind für die Impfschäden und die damit zusammenhängenden Kosten zu 100 Prozent ersatzpflichtig. Subsidiär haften am Hersteller beteiligte oder bisher beteiligte natürliche und juristische Personen, soweit sie durch die Beteiligung bereichert sind. Anderslautende Vereinbarungen, Erlasse oder Entscheide sind nichtig.

Art. 191g       Besondere Aufgaben der Kommission bei Indizien für Straftatbestände

^1 Die Kommission teilt Indizien für Straftatbestände nach Schweizer Recht, die sie während ihrer Untersuchungen erlangt, den ordentlichen Strafbehörden mit. Für Verfahren betreffend Personen, welche Massnahmen im Zusammenhang mit der Covid-19-Pandemie erlassen haben oder massgeblich auf die entsprechende Entscheidungsbildung Einfluss hatten oder an der Umsetzung der Massnahmen beteiligt waren, sowie für Verfahren im Zusammenhang mit der Covid-19-Impfung ist zwingend das Spezialgericht nach Artikel 191h zuständig.

^2 Die Kommission kann aber auch bei Verdacht auf Vergehen oder Verbrechen nach freiem Ermessen Beweise neben den ordentlichen Strafbehörden erforschen und eine Beurteilung durch das Spezialgericht verlangen.

Art. 191h       Gründung eines Spezialgerichts

Zur Beurteilung der von der Kommission untersuchten Sachverhalte wird ein Spezialgericht gegründet; dieses ist zwingend zuständig für Verfahren betreffend Personen, welche Massnahmen im Zusammenhang mit der Covid-19-Pandemie erlassen haben oder massgeblich auf die entsprechende Entscheidungsbildung Einfluss hatten oder an der Umsetzung der Massnahmen beteiligt waren, sowie für Verfahren im Zusammenhang mit der Covid-19-Impfung. Es besteht nach dem Vorbild des Bundesstrafgerichts aus einer erstinstanzlichen Strafkammer, einer Beschwerdekammer sowie einer abschliessend urteilenden Berufungskammer und ersetzt die Zuständigkeit der ordentlichen Gerichte. Ist in einer Strafsache sowohl die ordentliche Gerichtsbarkeit als auch die Gerichtsbarkeit des Spezialgerichts gegeben, so werden die Verfahren in der Hand der Kommission vereinigt.

Art. 191i        Verfolgungsverjährung und Vollstreckungsverjährung

Die Verfolgungsverjährung und die Vollstreckungsverjährung treten bei Verbrechen und Vergehen in Zusammenhang mit der Covid-19-Pandemie nicht ein und die Antragsfrist für einen Strafantrag beträgt sechs Monate nach Veröffentlichung des Untersuchungsberichts der Kommission.

Art. 191j         Zusammensetzung der Kommission

^1 Die Kommission besteht zu Beginn ihrer Arbeit aus sieben Mitgliedern. Das Komitee der am 28. Februar 2023 im Bundesblatt veröffentlichten Volksinitiative «Aufarbeitung der Hintergründe der Covid-19-Pandemie (Aufarbeitungsinitiative)» und die Bundesversammlung schlagen dem Volk jeweils sieben Personen zur Wahl vor. Es dürfen nur Personen vorgeschlagen werden, die weder Amtsträgerinnen und Amtsträger sind oder waren, noch am Erlass von Covid-19-Massnahmen beteiligt waren.

^2 Mindestens jeweils zwei vom Initiativkomitee und von der Bundesversammlung vorgeschlagene Personen sind mittels der meisten Stimmen zu wählen. Scheidet eine Person aus, wird eine Ersatzperson vom Initiativkomitee oder von der Bundesversammlung ernannt, je nachdem, von wem die ausgeschiedene Person vorgeschlagen wurde.

^3 Der Bundesrat stellt sicher, dass die Kommission nach Annahme der Artikel 191d-191r durch Volk und Stände innert sechs Monaten durch das Volk gewählt wird.

^4 Die Kommission kann je nach Umfang der Arbeit weitere Mitglieder durch das Volk wählen lassen.

Art. 191k         Organisation der Kommission

Die Kommission ist in ihrer Organisation und Aufgabenerfüllung frei.

Art. 191l         Immunität der Kommission

^1 Die Mitglieder der Kommission sind hinsichtlich ihrer im Rahmen der Aufgabenerfüllung vorgenommenen Handlungen keiner Gerichtsbarkeit unterworfen. Diese Immunität steht ihnen auch nach Abschluss ihrer Amtstätigkeit zu.

^2 Gegen ein Kommissionsmitglied kann ein Strafverfahren nur mit Ermächtigung der Mehrheit der restlichen Kommissionsmitglieder eingeleitet werden.

Art. 191m      Strafrechtliche Immunität

Die Immunität aller Personen, insbesondere der Mitglieder der Exekutiven, Legislativen und Judikativen aller Staatsebenen, ist für mögliche Straftatbestände in Zusammenhang mit der Covid-19-Pandemie aufgehoben.

Art. 191n       Verhinderung von gesundheitsfördernden Behandlungen

Die Kommission klärt ab, ob der Einsatz von gesundheitsfördernden Behandlungsmethoden und wirksamen Medikamenten oder besserer Prophylaxe verhindert wurde und ob dadurch vermeidbare schwerere Krankheitsverläufe oder Todesfälle verursacht wurden.

Art. 191o        Amnestie

Sollten natürliche oder juristische Personen für das Nichtbefolgen von Covid-19-Massnahmen, die widerrechtlich sind, bestraft worden sein, wird die Strafe erlassen und es erfolgt eine vollumfängliche Entschädigung für Prozess- und Anwaltskosten durch den Staat.

Art. 191p        Öffentlichkeit der Untersuchungen

^1 Die Kommission und das Spezialgericht informieren die Öffentlichkeit mit regelmässigen Pressemitteilungen und TV-Ausstrahlungen möglichst transparent über den Verlauf der Untersuchungen und Gerichtsverhandlungen, soweit dies mit dem Untersuchungszweck vereinbar ist.

^2 Die Schweizerische Radio- und Fernsehgesellschaft ist verpflichtet, jede Information der Kommission sowie des Spezialgerichts zu Hauptsendezeiten auf den Hauptkanälen bedingungslos und unzensuriert auszustrahlen.

^3 Die Kommission sowie das Spezialgericht können ihre Informationen frei und vollständig auffindbar auf ihrer Internetseite veröffentlichen.

Art. 191q        Überprüfung der Grundlagen für Covid-19-Massnahmen

^1 Falls die Kommission in ihrem Untersuchungsbericht einen der folgenden Sachverhalte feststellt, sind die im Zusammenhang mit der Covid-19-Pandemie erlassenen Massnahmen als widerrechtlich zu werten:

1. Es wurde nicht mit schweizweit geeichten und validierten Covid-19-Tests gearbeitet, beispielsweise aufgrund unterschiedlicher Vorgaben je nach Labor bezüglich der Anzahl Amplifikationen, oder die eingesetzten Covid-19-Tests waren nicht geeignet, um replizierbare Sars-CoV-2-Viren festzustellen, die Tests bezogen sich nur auf kleine Teile, beispielsweise Fragmente von Viren anstelle von ganzen infektiösen Viren, oder die Tests konnten nicht zwischen dem Sars-CoV-2-Virus und anderen Viren, beispielsweise anderen Coronavirenstämmen, unterscheiden und die mit diesen Tests erstellten Zahlen oder Ergebnisse dienten als eine Grundlage für die Feststellung der Covid-19-Pandemie.
2. Bei über 50 Prozent der vom Bundesamt für Gesundheit (BAG) als Covid-19-Tote gezählten Verstorbenen kann das BAG nicht nachweisen, dass die betreffenden Verstorbenen tatsächlich natürlich kausal am Sars-CoV-2-Virus verstorben sind, und nicht ausschliessen, dass in Wirklichkeit andere tödliche Krankheiten als ebenso mögliche Todesursache vorlagen.
3. Es gab Länder oder Regionen innerhalb eines Staatsgebietes, beispielsweise amerikanische Bundesstaaten, mit über 500 000 Einwohnerinnen und Einwohnern und mit einer der Schweiz vergleichbaren oder grösseren Bevölkerungsdichte, die 2020 oder 2021 keine oder kaum Covid-19-Massnahmen, wie die Maskenpflicht, erlassen hatten, die aber dennoch keine schlechteren Zahlen bezüglich Covid-19-Sterblichkeit und Hospitalisationen im Vergleich zur Schweiz aufwiesen oder bei denen es im Vergleich zu den Jahren vor Ausrufung der Covid-19-Pandemie zu keiner statistisch signifikanten Übersterblichkeit kam. Oder es gab Bundesstaaten wie beispielsweise Florida, Texas, South Dakota und weitere, welche über mehrere Monate betrachtet keine oder weniger strenge Massnahmen erlassen hatten und tiefere oder nicht signifikant höhere Zahlen bezüglich Covid-19-Sterblichkeit und Hospitalisationen hatten als vergleichbare Bundesstaaten.
4. Niemand in der Schweiz kann innert einer Frist von maximal zwölf Monaten ein gereinigtes Sars-CoV-2-Isolat der Virenstämme von 2020 oder 2021 nach den Henle-Koch-Postulaten, einschliesslich der Kontrollexperimente, vorweisen.
5. Es gab während der Covid-19-Pandemie in der Schweiz keine signifikante Übersterblichkeit innerhalb einer Zeitperiode von zwölf Monaten bis zu dem Zeitpunkt, als über sechzig Prozent der Bevölkerung zweimal geimpft waren, im Vergleich mit den Durchschnittswerten der letzten zehn Jahre unter der Berücksichtigung der Zuwanderung sowie der Altersstruktur der Bevölkerung und der damit zu erwartenden Todesfälle und der damit zusammenhängenden Sterblichkeit.

^2 Sollten sich die auf nationaler oder kantonaler Ebene ergriffenen Massnahmen gemäss der rechtlichen Würdigung der Kommission in ihrem Untersuchungsbericht für widerrechtlich oder verfassungswidrig oder unverhältnismässig oder gar willkürlich erweisen, so haften die Personen, die die Massnahmen erlassen oder massgeblich daran mitgewirkt haben, mit ihrem Vermögen solidarisch mit dem Kanton oder Bund für die entstandenen Schäden und sie werden strafrechtlich verfolgt.

^3 Die Verjährungsfrist für Schadenersatz- wie auch Genugtuungsansprüche im Zusammenhang mit der Covid-19-Pandemie beträgt 20 Jahre.

Art. 191r        Ergänzende Bestimmungen zum Spezialgericht

^1 Zu Richterpersonen des Spezialgerichts ernannt beziehungsweise gewählt werden können an Gerichten des Bundes, der Kantone oder Bezirke aktuell oder ehemals tätige Richterinnen und Richter mit fundierter Erfahrung in der Führung von Strafverfahren und Kenntnissen in den drei Amtssprachen. Zu Gerichtsschreiberinnen und Gerichtsschreibern gewählt werden können Juristinnen und Juristen mit fundierter Erfahrung im Strafrecht und Kenntnissen in den drei Amtssprachen. Das Komitee der Aufarbeitungsinitiative und die Bundesversammlung schlagen dem Volk Personen zur Wahl vor. Der Bundesrat stellt sicher, dass die Richterinnen und Richter nach Annahme der Artikel 191d-191r durch Volk und Stände innert sechs Monaten durch das Volk für eine Amtsdauer von fünf Jahren gewählt werden.

^2 Das Spezialgericht regelt seine Organisation und Verwaltung selbst. Es richtet seine Dienste ein und stellt das nötige Personal an. Es führt eine eigene Rechnung. Die Richterinnen und Richter des Spezialgerichts werden wie ordentliche Bundesrichterinnen und -richter mit einer 100-Prozent-Stelle entlöhnt.

^3 Sämtliche Kosten, die dem Spezialgericht nach freiem Ermessen für seine Aufgabenerfüllung entstehen, gehen zulasten der Schweizerischen Eidgenossenschaft.


[1]      SR 101""", ballot.bill.wording)
        self.assertEqual(datetime(2023, 2, 28, 0, 0, 0, 0), ballot.bill.date)
        self.assertEqual(BallotStatus.PENDING, ballot.status)
        self.assertIsNone(ballot.result)

    def test_get_initiative_bug_512(self):
        ballot: DoubleMajorityBallot = Chronology.get_initiative(
            "https://www.bk.admin.ch/ch/d/pore/vi/vis512.html")
        self.assertEqual("Für sicherere Fahrzeuge", ballot.bill.title)
        self.assertEqual("""Die Bundesverfassung^1  wird wie folgt geändert:

Art. 82 Abs. 1^bis-1^octies

^1bis Der Gesetzgeber orientiert sich an den folgenden Grundsätzen:

a.  Aktivitätsbezogene Ergonomie ist die wissenschaftliche Untersuchung der Beziehung zwischen der Benutzerin  oder dem Benutzer und den Mitteln, den Methoden und der Umgebung beim Führen eines  Fahrzeugs; die  Anwendung der entsprechenden Erkenntnisse muss für möglichst viele Verkehrsteilnehmerinnen und -teilnehmer ein Höchstmass an Komfort, Sicherheitsgefühl und Effizienz  garantieren.

b.  Schutz ist das Handeln, mit dem dafür gesorgt wird, dass Personen und Gegenständen kein Schaden  zugefügt wird; er ist auch darauf ausgerichtet, Schäden im Fall eines Unfalls zu reduzieren.

c.  Sicherheit ist die Eigenschaft all dessen, was sicher ist, das Merkmal von allem, was zuverlässig und seiner  Art  gemäss funktioniert; sie charakterisiert einen Zustand oder eine Situation der Gefahrlosigkeit; die  Anforderung der Sicherheit gilt sowohl für den Gegenstand selber als auch für seinen Gebrauch.

d.  Sicherheitsgefühl ist die Gemütslage des Vertrauens und der Ruhe, die sich aus dem begründeten oder   unbegründeten Gefühl ergibt, vor jeder Gefahr sicher zu sein.

^1ter Der Bund stellt sicher, dass im Bereich des Führens von Fahrzeugen den Herstellern von Fahrzeugen und Zubehör, den Führerinnen und Führern, den Fahrzeughalterinnen und  haltern, den Auftraggebern und den Versicherungen (nachfolgend: Akteure) ihre jeweiligen Verantwortlichkeiten hinsichtlich ihrer Tätigkeit und ihrer Zuständigkeit zugewiesen sind. Er legt die Mittel für Information, Ausbildung und Kontrolle fest.

^1quater Er schreibt vor, welche Bedingungen für die Information der Käuferinnen und Käufer gelten, damit diese eine fundierte Wahl treffen können, unabhängig davon, ob es sich um ein neues oder ein gebrauchtes Fahrzeug oder Zubehörteil handelt.

^1quinquies Er verlangt von den Herstellern oder ihren Vertretungen, zu garantieren, dass ihre Produkte in Bezug auf die aktivitätsbezogene Ergonomie, den Schutz und die Sicherheit dem Stand des Wissens und der Technik entsprechen. Er passt die rechtlichen Rahmenbedingungen an, wenn sich der Stand des Wissens und der Technik in den Bereichen der aktivitätsbezogenen Ergonomie, des Schutzes und der Sicherheit entwickelt.

^1sexies Die Akteure haften zivil- und strafrechtlich für alle Folgen, falls Mängel in diesen Bereichen zu Ereignissen führen, die einen zufriedenstellenden Verlauf beim Führen von Fahrzeugen stören, wie Unaufmerksamkeit, Gefährdung oder ein Unfall. Bei der Berechnung der Verantwortung, die den einzelnen Akteuren zukommt, ist eine Abwägung vorzunehmen gestützt darauf, welche Möglichkeit der jeweilige Akteur hatte, präventiv zu handeln, um so das Risiko störender Ereignisse zu verringern.

^1septies Der Bund legt für Fahrzeuge und Zubehör im Strassenverkehr das Verfahren und die Kriterien der Konformität fest in den Bereichen der aktivitätsbezogenen Ergonomie, des Schutzes und der Sicherheit.

^1octies Werden Funktionalitäten eines Zubehörteils in die Schnittstelle eines Fahrzeugs integriert, so ist der Hersteller, der die Funktionalitäten integriert, für ihre Konformität in Bezug auf die aktivitätsbezogene Ergonomie, den Schutz und die Sicherheit verantwortlich.

^1 SR 101""", ballot.bill.wording)
        self.assertEqual(datetime(2021, 3, 16, 0, 0, 0, 0), ballot.bill.date)
        self.assertEqual(BallotStatus.FAILED, ballot.status)
        self.assertIsNone(ballot.result)

    def test_get_initiative_bug_487(self):
        ballot: DoubleMajorityBallot = Chronology.get_initiative(
            "https://www.bk.admin.ch/ch/d/pore/vi/vis487.html")
        self.assertEqual(
            "Keine Massentierhaltung in der Schweiz (Massentierhaltungsinitiative)", ballot.bill.title)
        self.assertEqual("""Die Bundesverfassung^1 wird wie folgt geändert:

Art. 80a Landwirtschaftliche Tierhaltung

^1 Der Bund schützt die Würde des Tieres in der landwirtschaftlichen Tierhaltung. Die Tierwürde umfasst den Anspruch, nicht in Massentierhaltung zu leben.

^2 Massentierhaltung bezeichnet die industrielle Tierhaltung zur möglichst effizienten Gewinnung tierischer Erzeugnisse, bei der das Tierwohl systematisch verletzt wird.

^3 Der Bund legt Kriterien insbesondere für eine tierfreundliche Unterbringung und Pflege, den Zugang ins Freie, die Schlachtung und die maximale Gruppengrösse je Stall fest.

^4 Er erlässt Vorschriften über die Einfuhr von Tieren und tierischen Erzeugnissen zu Ernährungszwecken, die diesem Artikel Rechnung tragen.

Art. 197 Ziff. 12^2
12. Übergangsbestimmungen zu Art. 80a (Landwirtschaftliche Tierhaltung)

^1 Die Ausführungsbestimmungen zur landwirtschaftlichen Tierhaltung gemäss Artikel 80a können Übergangsfristen von maximal 25 Jahren vorsehen.

^2 Die Ausführungsgesetzgebung muss bezüglich Würde des Tiers Anforderungen festlegen, die mindestens den Anforderungen der Bio-Suisse-Richtlinien 2018^3 entsprechen.

^3 Ist die Ausführungsgesetzgebung zu Artikel 80a nach dessen Annahme nicht innert drei Jahren in Kraft getreten, so erlässt der Bundesrat die Ausführungsbestimmungen vorübergehend auf dem Verordnungsweg.

^1 SR 101
^2 Die endgültige Ziffer dieser Übergangsbestimmungen wird nach der Volksabstimmung von der Bundeskanzlei festgelegt.
^3 Richtlinien der Bio Suisse für die Erzeugung, Verarbeitung und den Handel von Knospe-Produkten, Fassung vom 1. Januar 2018, abrufbar unter www.bio-suisse.ch.""", ballot.bill.wording)
        self.assertEqual(datetime(2018, 6, 12, 0, 0, 0, 0), ballot.bill.date)
        self.assertEqual(BallotStatus.COMPLETED, ballot.status)
        self.assertAlmostEqual(Decimal(37.1), ballot.result.percentage_yes, 2)
        self.assertAlmostEqual(
            Decimal(0.5), ballot.result.accepting_cantons, 2)

    def test_get_initiative_bug_461(self):
        ballot: DoubleMajorityBallot = Chronology.get_initiative(
            "https://www.bk.admin.ch/ch/d/pore/vi/vis461.html")
        self.assertEqual(
            "Zersiedelung stoppen - für eine nachhaltige Siedlungsentwicklung (Zersiedelungsinitiative)", ballot.bill.title)
        self.assertEqual("""Die Bundesverfassung^1 wird wie folgt geändert:

Art. 75 Abs. 4-7

^4 Bund, Kantone und Gemeinden sorgen im Rahmen ihrer Zuständigkeiten für günstige Rahmenbedingungen für nachhaltige Formen des Wohnens und Arbeitens in kleinräumigen Strukturen mit hoher Lebensqualität und kurzen Verkehrswegen (nachhaltige Quartiere).

^5 Anzustreben ist eine Siedlungsentwicklung nach innen, die im Einklang steht mit hoher Lebensqualität und besonderen Schutzbestimmungen.

^6 Die Ausscheidung neuer Bauzonen ist nur zulässig, wenn eine andere unversiegelte Fläche von mindestens gleicher Grösse und vergleichbarem potenziellem landwirtschaftlichem Ertragswert aus der Bauzone ausgezont wird.

^7 Ausserhalb der Bauzone dürfen ausschliesslich standortgebundene Bauten und Anlagen für die bodenabhängige Landwirtschaft oder standortgebundene Bauten von öffentlichem Interesse bewilligt werden. Das Gesetz kann Ausnahmen vorsehen. Bestehende Bauten geniessen Bestandesgarantie und können geringfügig erweitert und geringfügig umgenutzt werden.


^1            SR 101""", ballot.bill.wording)
        self.assertEqual(datetime(2015, 4, 21, 0, 0, 0, 0), ballot.bill.date)
        self.assertEqual(BallotStatus.COMPLETED, ballot.status)
        self.assertAlmostEqual(Decimal(36.3), ballot.result.percentage_yes, 2)
        self.assertAlmostEqual(Decimal(0), ballot.result.accepting_cantons, 2)

    def test_get_initiative_bug_477(self):
        ballot: DoubleMajorityBallot = Chronology.get_initiative(
            "https://www.bk.admin.ch/ch/d/pore/vi/vis477.html")
        self.assertEqual(
            "Ja zum Tier- und Menschenversuchsverbot - Ja zu Forschungswegen mit Impulsen für Sicherheit und Fortschritt", ballot.bill.title)
        self.assertEqual("""Die Bundesverfassung^1 wird wie folgt geändert:

Art. 80 Abs. 2 Bst. b, 3 und 4

^2 Er [der Bund] regelt insbesondere:

b. Aufgehoben

^3 Tierversuche und Menschenversuche sind verboten. Tierversuche gelten als Tierquälerei bis hin zum Verbrechen. Dies und alles Nachfolgende gelten sinngemäss für Tier- und Menschenversuche:

a. Erstanwendung ist nur zulässig, wenn sie im umfassenden und überwiegenden Interesse der Betroffenen (Tiere wie Menschen) liegt; die Erstanwendung muss zudem erfolgversprechend sein und kontrolliert und vorsichtig vollzogen werden.

b. Nach Inkrafttreten des Tierversuchsverbotes sind Handel, Einfuhr und Ausfuhr von Produkten aller Branchen und Arten verboten, wenn für sie weiterhin Tierversuche direkt oder indirekt durchgeführt werden; bisherige Produkte bleiben vom Verbot ausgenommen, wenn für sie keinerlei Tierversuche mehr direkt oder indirekt durchgeführt werden.

c. Die Sicherheit für Mensch, Tier und Umwelt muss jederzeit gewährleistet sein; falls dazu bei Neuentwicklungen respektive Neueinfuhren keine amtlich anerkannten tierversuchsfreien Verfahren existieren, gilt ein Zulas-sungsverbot für das Inverkehrbringen respektive ein Verbot der Ausbringung und Freisetzung in der Umwelt.

d. Es muss gewährleistet sein, dass tierversuchsfreie Ersatzansätze mindestens dieselbe staatliche Unterstützung erhalten wie vormals die Tierversuche.

^4 Für den Vollzug der Vorschriften sind die Kantone zuständig, soweit das Gesetz ihn nicht dem Bund vorbehält.

Art. 118b Abs. 2 Bst. c und 3

^2 Für die Forschung in Biologie und Medizin mit Personen beachtet er [der Bund] folgende Grundsätze:

c. Aufgehoben

^3 Forschungsvorhaben müssen den Anforderungen von Artikel 80 Absatz 3 Buchstabe a genügen.

Art. 197 Ziff. 12^2
12. Übergangsbestimmung zu Art. 80 Abs. 2 Bst. b, 3 und 4 sowie Art. 118b Abs. 2 Bst. c und 3 (Tierversuchsverbot und Menschenversuchsverbot)

Bis zum Inkrafttreten der gesetzlichen Bestimmungen erlässt der Bundesrat innerhalb von zwei Jahren nach Annahme von Artikel 80 Absätze 2 Buchstabe b, 3 und 4 sowie Artikel 118b Absätze 2 Buchstabe c und 3 durch Volk und Stände die erforderlichen Ausführungsbestimmungen.

^1 SR 101
^2 Die endgültige Ziffer dieser Übergangsbestimmung wird nach der Volksabstimmung von der Bundeskanzlei festgelegt.""", ballot.bill.wording)
        self.assertEqual(datetime(2017, 10, 3, 0, 0, 0, 0), ballot.bill.date)
        self.assertEqual(BallotStatus.COMPLETED, ballot.status)
        self.assertAlmostEqual(Decimal(20.9), ballot.result.percentage_yes, 2)
        self.assertAlmostEqual(Decimal(0), ballot.result.accepting_cantons, 2)

    def test_get_initiative_bug_459(self):
        ballot: DoubleMajorityBallot = Chronology.get_initiative(
            "https://www.bk.admin.ch/ch/d/pore/vi/vis459.html")
        self.assertEqual(
            "Zur Förderung der Velo-, Fuss- und Wanderwege (Velo-Initiative)", ballot.bill.title)
        self.assertEqual("""Die Bundesverfassung^1  wird wie folgt geändert:

Art. 88                   Fuss-, Wander- und Velowege

^1 Der Bund legt Grundsätze über Fuss- und Wanderwegnetze und über Netze für den Alltags- und Freizeit-Veloverkehr fest.

^2 Er fördert und koordiniert Massnahmen der Kantone und Dritter zur Anlage und Erhaltung attraktiver und sicherer Netze und zur Kommunikation über diese; dabei wahrt er die Zuständigkeiten der Kantone.

^3 Er nimmt bei der Erfüllung seiner Aufgaben Rücksicht auf solche Netze. Muss er dazugehörende Wege aufheben, so ersetzt er sie.

^1            SR 101""", ballot.bill.wording)
        self.assertEqual(datetime(2015, 3, 3, 0, 0, 0, 0), ballot.bill.date)
        self.assertEqual(BallotStatus.COMPLETED, ballot.status)
        self.assertAlmostEqual(Decimal(73.6), ballot.result.percentage_yes, 2)
        self.assertAlmostEqual(Decimal(23), ballot.result.accepting_cantons, 2)

    def test_get_initiative_bug_456(self):
        ballot: DoubleMajorityBallot = Chronology.get_initiative(
            "https://www.bk.admin.ch/ch/d/pore/vi/vis456.html")
        self.assertEqual(
            "Für die Würde der landwirtschaftlichen Nutztiere (Hornkuh-Initiative)", ballot.bill.title)
        self.assertEqual("""Die Bundesverfassung^1 wird wie folgt geändert:

Art. 104 Abs. 3 Bst. b

^3 Er [der Bund] richtet die Massnahmen so aus, dass die Landwirtschaft ihre multifunktionalen Aufgaben erfüllt. Er hat insbesondere folgende Befugnisse und Aufgaben:

b. Er fördert mit wirtschaftlich lohnenden Anreizen Produktionsformen, die besonders naturnah, umwelt- und tierfreundlich sind; dabei sorgt er insbesondere dafür, dass Halterinnen und Halter von Kühen, Zuchtstieren, Ziegen und Zuchtziegenböcken finanziell unterstützt werden, solange die ausgewachsenen Tiere Hörner tragen.

__________________

^1 RS 101""", ballot.bill.wording)
        self.assertEqual(datetime(2014, 9, 23, 0, 0, 0, 0), ballot.bill.date)
        self.assertEqual(BallotStatus.COMPLETED, ballot.status)
        self.assertAlmostEqual(Decimal(45.3), ballot.result.percentage_yes, 2)
        self.assertAlmostEqual(Decimal(5), ballot.result.accepting_cantons, 2)

    def test_get_initiative_bug_346(self):
        ballot: DoubleMajorityBallot = Chronology.get_initiative(
            "https://www.bk.admin.ch/ch/d/pore/vi/vis346.html")
        self.assertEqual(
            "für ein Verbot von Kriegsmaterial-Exporten", ballot.bill.title)
        self.assertEqual("""I

Die Bundesverfassung vom 18. April 1999 wird wie folgt geändert:

Art. 107 Abs. 3 (neu)

^3 Er [der Bund] unterstützt und fördert internationale Bestrebungen für Abrüstung und Rüstungskontrolle.

Art. 107a (neu)\tAusfuhr von Kriegsmaterial und besonderen militärischen Gütern

^1 Die Ausfuhr und die Durchfuhr folgender Güter sind verboten:

a.\tKriegsmaterial einschliesslich Kleinwaffen und leichte Waffen sowie die zugehörige Munition;

b.\tbesondere militärische Güter;

c.\tImmaterialgüter einschliesslich Technologien, die für die Entwicklung, die Herstellung oder den Gebrauch von Gütern nach den Buchstaben a und b von wesentlicher Bedeutung sind, sofern sie weder allgemein zugänglich sind noch der wissenschaftlichen Grundlagenforschung dienen.

^2 Vom Aus- und vom Durchfuhrverbot ausgenommen sind Geräte zur humanitären Entminung sowie Sport- und Jagdwaffen, die eindeutig als solche erkennbar und in gleicher Ausführung nicht auch Kampfwaffen sind, sowie die zugehörige Munition.

^3 Vom Ausfuhrverbot ausgenommen ist die Ausfuhr von Gütern nach Absatz 1 durch Behörden des Bundes, der Kantone oder der Gemeinden, sofern diese Eigentümer der Güter bleiben, die Güter durch eigene Dienstleistende benutzt und anschliessend wieder eingeführt werden.

^4 Die Vermittlung von und der Handel mit Gütern nach den Absätzen 1 und 2 sind verboten, sofern der Empfänger oder die Empfängerin den Sitz oder Wohnsitz im Ausland hat.

II

Die Übergangsbestimmungen der Bundesverfassung werden wie folgt geändert:

Art. 197 Ziff. 8 (neu)

8.\tÜbergangsbestimmung zu Art. 107a (Ausfuhr von Kriegsmaterial und besonderen militärischen Gütern)

^1 Der Bund unterstützt während zehn Jahren nach der Annahme der eidgenössischen Volksinitiative «für ein Verbot von Kriegsmaterial-Exporten» durch Volk und Stände Regionen und Beschäftigte, die von den Verboten nach Artikel 107a betroffen sind.

^2 Nach Annahme der Artikel 107 Absatz 3 und 107a durch Volk und Stände dürfen keine neuen Bewilligungen für Tätigkeiten nach Artikel 107a erteilt werden.""", ballot.bill.wording)
        self.assertEqual(datetime(2006, 6, 27, 0, 0, 0, 0), ballot.bill.date)
        self.assertEqual(BallotStatus.COMPLETED, ballot.status)
        self.assertAlmostEqual(Decimal(31.8), ballot.result.percentage_yes, 2)
        self.assertAlmostEqual(Decimal(0), ballot.result.accepting_cantons, 2)

    def test_get_initiative_bug_114(self):
        ballot: DoubleMajorityBallot = Chronology.get_initiative(
            "https://www.bk.admin.ch/ch/d/pore/vi/vis114.html")
        self.assertEqual(
            "für eine Reform des Steuerwesens (Gerechtere Besteuerung und Abschaffung der Steuerprivilegien)", ballot.bill.title)
        self.assertEqual("""Die Initiative ist in der Form einer allgemeinen Anregung gestellt und hat folgenden Wortlaut:

Der Bundesverfassung sind die Grundlagen für eine Reform des schweizerischen Steuerwesens nach folgenden Grundsätzen einzufügen:

1. Einkommen und Vermögen werden aussschliesslich nach einheitlichen Grundsätzen und Tarifen besteuert, wobei folgende Richtlinien zu beachten sind:

1. Das Einkommen der natürlichen Personen ist nach einem progressiven Tarif zu besteuern. Mit wachsendem Einkommen nimmt der Steuersatz stetig zu. Die Verschärfung der Progression als Folge der Teuerung ist periodisch zu beseitigen.
2. Die Familienbesteuerung ist so zu regeln, dass eine unangemessene Belastung des Arbeitseinkommens der Ehefrau vermieden wird.
3. Die Renteneinkommen (AHV; IV) sind nur zur Hälfte zu besteuern.
4. Die Ertragsbesteuerung der juristischen Personen erfolgt unabhängig von ihrer Rechtsform proportional zum nicht ausgeschütteten Gewinn.
5. Die Besteuerung von Vermögen, Kapital und Reserven hat nur ergänzenden Charakter.
6. Noch vorhandene Steuerprivilegien sind zu beseitigen.

2. Die Kantone erheben für Rechnung des Bundes die allgemeine Bundessteuer auf dem Einkommen und Vermögen. Sie werden an ihrem Rohertrag soweit beteiligt, dass sie ihren Finanzbedarf weitgehend daraus decken können.

Ein Teil des Rohertrages der Bundessteuer ist für den Finanzausgleich auszuscheiden. Dieser ist so auszubauen, dass die gesamte Steuerbelastung der Kantone untereinander angeglichen werden kann.

Die einheitlichen Grundsätze und Tarife sind auch für die kantonalen und kommunalen Steuern auf dem Einkommen und Vermögen verbindlich. Diese Steuern werden in Prozenten der Bundessteuer erhoben. Der dafür zulässige Rahmen ist einheitlich festzulegen.

3. Der Bund erlässt einheitliche Bestimmungen über die Erhebung einer Erbschafts- und Schenkungssteuer, die den Kantonen zukommt.

4. Der Bund erhebt eine allgemeine Steuer auf allen alkoholischen Getränken, deren Sätze nach dem Alkoholgehalt abzustufen sind.

5. Der Bund sorgt für die Besteuerung des Energieverbrauchs, wobei die Steuersätze nach der Umweltbelastung durch den einzelnen Energieträger abzustufen sind. Der Ertrag dient zur Finanzierung der Erforschung und Lösung der Umweltprobleme und der Raumplanung. Ausgenommen ist der Ertrag der Besteuerung der Treibstoffe für motorische Zwecke, der vorwiegend für Bau, Betrieb und Unterhalt der Strassen zu verwenden ist.

6. In die Verfassung sind nur die Grundsätze aufzunehmen. Ihre Ausführung wird durch die Bundesgesetzgebung festgelegt, wobei angemessene Übergangsfristen einzuräumen sind.

Der deutsche Text der Initiative ist massgebend.""", ballot.bill.wording)
        self.assertEqual(datetime(1973, 5, 3, 0, 0, 0, 0), ballot.bill.date)
        self.assertEqual(BallotStatus.COMPLETED, ballot.status)
        self.assertAlmostEqual(Decimal(42.2), ballot.result.percentage_yes, 2)
        self.assertAlmostEqual(Decimal(0.5), ballot.result.accepting_cantons, 2)
