
from bp.data.scraper import Scraper
from bp.entity.ballot import BallotStatus, DoubleMajorityBallot
from bp.entity.bill import Bill
from bp.entity.result import DoubleMajorityBallotResult

import re
import requests
from datetime import datetime
from decimal import Decimal
from lxml import html
from typing import List


POPULAR_INITIATIVES_CHRONOLOGY: str = 'https://www.bk.admin.ch/ch/d/pore/vi/vis_2_2_5_1.html'
"""str: Popular initiatives chronology website."""


PREFIXED_TITLE_PATTERN: re.Pattern = re.compile("^.*['«]([^'»]*)['»].*$")
"""
re.Pattern: Regex pattern extracting bill title from prefixed details page
title, e.g. extracting "MyTitle" from "My prefix: 'MyTitle'"
"""


class Chronology:
    """Bill information download helper
    Downloads bill information from chronology websites.
    """

    @staticmethod
    def get_initiatives() -> List[str]:
        """Retrieve details page URL for each bill on
        POPULAR_INITIATIVES_CHRONOLOGY.

        Returns:
            List[str]: Details page URLs for all bills, ordered newest to
            oldest.
        """
        return Chronology.__get_bills(POPULAR_INITIATIVES_CHRONOLOGY)

    @staticmethod
    def get_initiative(bill_details_url: str) -> DoubleMajorityBallot:
        """Retrieve popular initiative details information. Includes bill
        details as well as optional ballot results.

        Args:
            billDetailsUrl (str): Bill details page from which to extract data.

        Returns:
            DoubleMajorityBallot: Bill information with optional result.
        """
        response: requests.Response = requests.get(bill_details_url)
        response.encoding = response.apparent_encoding
        content: html.HtmlElement = html.fromstring(response.text)
        vote_row: html.HtmlElement = Chronology.__find_row(
            content, "Abgestimmt am")
        if vote_row is None:
            vote_row = Chronology.__find_row(
                content, "Abstimmung über Gegenentwurf")

        bill: Bill = Chronology.__get_bill(bill_details_url, content)
        status: BallotStatus = Chronology.__get_status(content, vote_row)
        result: DoubleMajorityBallotResult | None = Chronology.__get_initiative_result(
            bill.title, vote_row)
        return DoubleMajorityBallot(bill, status, result)

    @staticmethod
    def __get_initiative_result(title: str, vote_row: html.HtmlElement) -> DoubleMajorityBallotResult | None:
        """Look up the result of the vote for the given initiative, if present.

        Args:
            title (str): Title of the bill. Used to identify the result in case
            multiple votes were held on the same day.
            vote_row (html.HtmlElement): Row in the timetable of the bill which
            indicates when the date was held. Ballot results are categorised by
            date on www.bk.admin.ch, and this date allows us to derive the URL
            which contains the ballot results for title.

        Returns:
            DoubleMajorityBallotResult | None: If a vote was already held,
            which is to say of vote_row is not None, the result is the popular
            and canton vote count as extracted from the vote result page.
            Otherwise None.
        """
        if vote_row is None:
            return None

        formatted_date: str = vote_row.xpath("td")[1].text_content().strip()
        date: datetime = Chronology.__parse_timestamp(formatted_date)
        voteResultUrl: str = f"https://www.bk.admin.ch/ch/d/pore/va/{date.year}{date.month:02d}{date.day:02d}/index.html"
        response: requests.Response = requests.get(voteResultUrl)
        response.encoding = response.apparent_encoding
        content: html.HtmlElement = html.fromstring(response.text)

        initiative_title: html.HtmlElement = Chronology.__find_result_table(
            content, title)
        table: List[html.HtmlElement] = initiative_title.xpath(
            "following-sibling::table[1]")
        rows: List[html.HtmlElement] = table[0].xpath("tbody/tr")
        popular_vote_voting_yes = Decimal(
            rows[0].xpath("td")[3].text_content())
        accepting_cantons: Decimal = Chronology.__extract_accepting_cantons(
            title, rows)

        return DoubleMajorityBallotResult(popular_vote_voting_yes, accepting_cantons)

    @staticmethod
    def __extract_accepting_cantons(title: str, rows: List[html.HtmlElement]) -> Decimal:
        """Helper to read the number of accepting cantons from the rows of a
        ballot result table. title is used to handle a few special cases where
        some ballot information pages have incomplete information.

        Args:
            title (str): Title of the bill.
            rows (List[html.HtmlElement]): Vote result table rows of the bill.

        Returns:
            Decimal: Number of cantons which accepted the bill.
        """
        if "für eine Reform des Steuerwesens (Gerechtere Besteuerung und Abschaffung der Steuerprivilegien)" == title:
            return Decimal(0.5)

        formatted_accepting_cantons: str = rows[1].xpath("td")[
            1].text_content()
        return Chronology.__parse_canton_count(formatted_accepting_cantons)

    @staticmethod
    def __find_result_table(content: html.HtmlElement, title: str) -> html.HtmlElement:
        """Vote results are published per voting day, so multiple vote results
        are on the same page. This method identifies the correct results table
        for the given bill.

        Args:
            content (html.HtmlElement): Voting day results page.
            title (str): Name of the bill to find.

        Returns:
            html.HtmlElement: Table containing the vote results.
        """
        title = title.lower()
        escaped_title = title.replace("(", "[").replace(")", "]").replace(
            "ja zur komplementärmedizin", "zukunft mit komplementärmedizin").replace(
                "für tiefere krankenkassenprämien in der grundversicherung", "für qualität und wirtschaftlichkeit in der krankenversicherung").replace(
                    "überschüssige goldreserven in den ahv-fonds [goldinitiative]", "ueberschüssige goldreserven in den ahv-fonds (goldinitiative)").replace(
                        "strom ohne atom - für eine energiewende und die schrittweise stilllegung der atomkraftwerke [strom ohne atom]", " strom ohne atom - für eine energiewende und schrittweise stilllegung der atomkraftwerke (strom ohne atom)").replace(
                            "moratoriumplus - für die verlängerung des atomkraftwerk-baustopps und die begrenzung des atomrisikos [moratoriumplus]", "moratorium plus - für die verlängerung des atomkraftwerk-baustopps und die begrenzung des atomrisikos (moratoriumplus)").replace(
                                "für die belohnung des energiesparens und gegen die energieverschwendung [energie-umwelt-initiative]", "verfassungsartikel über eine energielenkungsabgabe für die umwelt").replace(
                                    "für einen solar-rappen [solar-initiative]", "für einen solarrappen (solar-initiative").replace(
                                        "zum schutz von leben und umwelt vor genmanipulationen [gen-schutz-initiative]", "zum schutz von leben und umwelt vor genmanipulation (gen-schutz-initiative)").replace(
                                            "für einen arbeitsfreien bundesfeiertag [\"1. august-initiative\"]", "für einen arbeitsfreien bundesfeiertag (1. august-initiative)").replace(
                                                "für eine freie aarelandschaft zwischen biel und solothurn/zuchwil", "für eine autobahnfreie aarelandschaft zwischen biel und solothurn/zuchwil").replace(
                                                    "für die koordination des schuljahrbeginns", "für die koordination des schuljahresbeginns in allen kantonen").replace(
                                                        "für die fristenlösung [beim schwangerschaftsabbruch]", "für die fristenlösung").replace(
                                                            "für 12 motorfahrzeugfreie sonntage pro jahr", "für 12 motorfahrzeugfreie und motorflugzeugfreie sonntage pro jahr").replace(
                                                                "gegen die luftverschmutzung durch motorfahrzeuge [albatrosinitiative]", "gegen die luftverschmutzung durch motorfahrzeuge").replace(
                                                                    "für die vermehrte mitbestimmung der bundesversammlung und des schweizervolkes im nationalstrassenbau", "demokratie im nationalstrassenbau").replace(
                                                                        "für eine reichtumssteuer", "zur steuerharmonisierung, zur stärkeren besteuerung des reichtums und zur entlastung der unteren einkommen (reichtumsteuer-initiative)").replace(
                                                                            "für eine reform des steuerwesens [gerechtere besteuerung und abschaffung der steuerprivilegien]", "gerechtere besteuerung und die abschaffung der steuerprivilegien").replace(
                                                                                "für eine beschränkung der einbürgerungen", "zur beschränkung der einbürgerungen").replace(
                                                                                    "ja zu europa!", "ja zu europa").strip()

        initiative_titles: List[html.HtmlElement] = content.xpath("//h3")
        for initiative_title in initiative_titles:
            actual_title: str = Scraper.convert_to_text(initiative_title)
            actual_title = actual_title.replace("\r\n", " ")
            actual_title = actual_title.replace("\n", " ")
            actual_title = actual_title.lower()
            if title in actual_title or escaped_title in actual_title:
                return initiative_title

    @staticmethod
    def __get_status(content: html.HtmlElement, vote_row: html.HtmlElement | None) -> BallotStatus:
        """Interprets the timetable on a bill details page to identify the
        current status of the bill.

        Args:
            content (html.HtmlElement): Bill details HTML page.
            vote_row (html.HtmlElement): Row containing the ballot vote date,
            if found. This row is used to extract other information by other
            methods. Since it is already extracted, if present we can use it as
            a shortcut and avoid searching content using XPath entirely.

        Returns:
            BallotStatus: Status of the ballot.
        """
        if not vote_row is None:
            return BallotStatus.COMPLETED
        if not Chronology.__find_row(content, "Nicht zustandegekommen am") is None or \
           not Chronology.__find_row(content, "Im Sammelstadium gescheitert") is None or \
           not Chronology.__find_row(content, "Zurückgezogen") is None or \
           not Chronology.__find_row(content, "Bedingter Rückzug") is None:
            return BallotStatus.FAILED
        return BallotStatus.PENDING

    @staticmethod
    def __find_row(content: html.HtmlElement, firstColumnValue: str) -> html.HtmlElement | None:
        """Helper to identify a row in any table in content whose first column
        value starts with firstColumnValue.

        Args:
            content (html.HtmlElement): HTML website content in which to
            search.
            firstColumnValue (str): Search string to find.

        Returns:
            html.HtmlElement | None: "tr" row containing firstColumnValue in
            the first column, or None if no match was found.
        """
        cell: List[html.HtmlElement] = content.xpath(
            f"//tr/td[starts-with(text(), '{firstColumnValue}')]")
        if not cell:
            return None
        return cell[0].getparent()

    @staticmethod
    def __get_bill(billDetailsUrl: str, content: html.HtmlElement) -> Bill:
        """Retrieve bill details information.

        Args:
            billDetailsUrl (str): URL of bill details page.
            content (html.HtmlElement): Page content of billDetailsUrl.

        Returns:
            Bill: Bill details information retrieved from bill details page.
        """
        return Bill(Chronology.__extract_title(billDetailsUrl, content), Chronology.__extract_wording(billDetailsUrl), Chronology.__extract_date(content))

    @staticmethod
    def __get_bills(url: str) -> List[str]:
        """Retrieve details page URL for each bill on url.

        Returns:
            List[str]: Details page URLs for all bills, ordered newest to
            oldest.
        """
        parent_path: str = Scraper.get_parent(url)
        response: requests.Response = requests.get(url)
        content: html.HtmlElement = html.fromstring(response.text)
        table_rows: List[html.HtmlElement] = content.xpath("//td/a")
        return [parent_path + "/" + element.get("href") for element in table_rows]

    @staticmethod
    def __extract_title(bill_details_url: str, bill_details_page_content: html.HtmlElement) -> str:
        """Extract title from bill details HTML page.

        Args:
            bill_details_url (str): Original URL from which
            bill_details_page_content was downloaded. Used only for error
            messages.
            bill_details_page_content (html.HtmlElement): Bill details HTML
            content.

        Raises:
            ValueError: If no title string with the expected format was found.

        Returns:
            str: Bill title text without any prefixes.
        """
        prefixed_title: List[html.HtmlElement] = bill_details_page_content.xpath(
            "//div[@class='contentHead']//h2")
        if len(prefixed_title) == 0:
            prefixed_title = bill_details_page_content.xpath(
                "//div[@class='contentHead']//h1")
        if len(prefixed_title) == 0:
            raise ValueError(
                f"Bill details page did not contain an <h2> or <h1> header in expected <div class='contentHead'> location: {bill_details_url}")

        title: html.HtmlElement = prefixed_title[0]
        text: str = Scraper.convert_to_text(title)
        match: re.Match = re.match(
            PREFIXED_TITLE_PATTERN, text.replace("\r\n", ""))
        if not match:
            raise ValueError(
                f"Bill details page did not contain expected title pattern: {bill_details_url}")
        return match.group(1)

    @staticmethod
    def __extract_wording(billDetailsUrl: str) -> str:
        """Download and extract bill wording for the given bill.

        Args:
            billDetailsUrl (str): URL of details page of bill for which to
            download and extract the wording. The wording is stored in a
            companion page that can be statically derived from this URL.

        Returns:
            str: Text representation of the wording of the bill, suitable for
            predictions.
        """
        billWordingUrl: str = billDetailsUrl.replace(".html", "t.html")
        response: requests.Response = requests.get(billWordingUrl)
        response.encoding = response.apparent_encoding
        content: html.HtmlElement = html.fromstring(response.text)
        paragraphs: List[html.HtmlElement] = content.xpath(
            "//div[contains(@class, 'mod-text')]")
        return Scraper.convert_to_text(paragraphs).strip()

    @staticmethod
    def __extract_date(billDetailsPageContent: html.HtmlElement) -> datetime:
        """Extracts a single date to associate with the bill.

        Args:
            billDetailsPageContent (html.HtmlElement): Bill details HTML
            content.

        Returns:
            datetime: Date timestamp parsed from details page.
        """
        last_table_row: html.HtmlElement = billDetailsPageContent.xpath(
            "//tr")[-1]
        second_cell: html.HtmlElement = last_table_row.xpath("td")[1]
        formatted_date: str = second_cell.text_content()
        return Chronology.__parse_timestamp(formatted_date)

    @staticmethod
    def __parse_timestamp(formatted_date: str) -> datetime:
        """Implements the date format used on www.bk.admin.ch.

        Args:
            formatted_date (str): Date to parse from www.bk.admin.ch.

        Returns:
            datetime: Parsed date equivalent to formatted_date.
        """
        return datetime.strptime(formatted_date, "%d.%m.%Y")

    @staticmethod
    def __parse_canton_count(canton_count_with_fraction: str) -> Decimal:
        """The number of cantons voting yes on a ballot is represented using
        fractions. We translate this to a regular decimal number. As an
        example, "7 3/2" will be translated to 8.5.

        Args:
            canton_count_with_fraction (str): Canton count using fractions.

        Returns:
            Decimal: Equivalent count to canton_count_with_fraction.
        """
        components: List[str] = canton_count_with_fraction.split(" ")
        count = Decimal(0)
        for component in components:
            if "/" in component:
                division: List[str] = component.split("/")
                dividend = Decimal(division[0])
                divisor = Decimal(division[1])
                count += dividend / divisor
            elif component != "":
                count += Decimal(component)
        return count
