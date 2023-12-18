
from bp.data.scraper import Scraper
from bp.entity.bill import Bill

import requests
from datetime import datetime
from lxml import html
from typing import List


POPULAR_INITIATIVES_CHRONOLOGY: str = 'https://www.bk.admin.ch/ch/d/pore/vi/vis_2_2_5_1.html'
"""str: Popular initiatives chronology website."""


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
    def get_bill(billDetailsUri: str) -> Bill:
        """Retrieve bill details information.

        Args:
            billDetailsUri (str): _description_

        Returns:
            Bill: _description_
        """
        return Bill("Default title", "Default wording", datetime(2024, 1, 1, 0, 0, 0, 0))
