
from bp.data.scraper import Scraper
from bp.entity.bill import Bill

import re
import requests
from datetime import datetime
from lxml import html
from typing import List


POPULAR_INITIATIVES_CHRONOLOGY: str = 'https://www.bk.admin.ch/ch/d/pore/vi/vis_2_2_5_1.html'
"""str: Popular initiatives chronology website."""


PREFIXED_TITLE_PATTERN: re.Pattern = re.compile("^.*'([^']*)'$")
"""
re.Pattern: Regex pattern extracting bill title from prefixed details page
title, e.g. extracting "MyTitle" from "My prefix: 'MyTitle'"
"""


class Chronology:
    """Bill information download helper
    Downloads bill information from chronology websites.
    """

    def __init__(self, url: str):
        """Creates an information downloader for the given chronolgy page.

        Args:
            url (str): URL of bill chronology website.
        """
        self.url = url

    def get_bills(self) -> List[str]:
        """Retrieve details page URL for each bill on self.url.

        Returns:
            List[str]: Details page URLs for all bills, ordered newest to
            oldest.
        """
        parent_path: str = Scraper.get_parent(self.url)
        response: requests.Response = requests.get(self.url)
        content: html.HtmlElement = html.fromstring(response.text)
        table_rows: List[html.HtmlElement] = content.xpath("//td/a")
        return [parent_path + "/" + element.get("href") for element in table_rows]

    @staticmethod
    def get_bill(billDetailsUrl: str) -> Bill:
        """Retrieve bill details information.

        Args:
            billDetailsUrl (str): _description_

        Returns:
            Bill: _description_
        """
        response: requests.Response = requests.get(billDetailsUrl)
        content: html.HtmlElement = html.fromstring(response.text)

        return Bill(Chronology.__extract_title(content), Chronology.__extract_wording(billDetailsUrl), Chronology.__extract_date(content))

    @staticmethod
    def __extract_title(billDetailsPageContent: html.HtmlElement) -> str:
        """Extract title from bill details HTML page.

        Args:
            billDetailsPageContent (html.HtmlElement): Bill details HTML
            content.

        Raises:
            ValueError: If no title string with the expected format was found.

        Returns:
            str: Bill title text without any prefixes.
        """
        prefixed_title: List[html.HtmlElement] = billDetailsPageContent.xpath(
            "//div[@class='contentHead']//h2")
        match: re.Match = re.match(
            PREFIXED_TITLE_PATTERN, prefixed_title[0].text)
        if not match:
            raise ValueError(
                "Bill details page did not contain expected title pattern.")
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
            "//div[contains(@class, 'mod-text')]//p")
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
        return datetime.strptime(formatted_date, "%d.%m.%Y")
