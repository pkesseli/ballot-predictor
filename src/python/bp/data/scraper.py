from lxml import html
from typing import List
from urllib.parse import urlparse, ParseResult


SUPERSCRIPT_MARKER: str = "^"
"""str: Superscript prefix used in HTML to plain text conversions."""


class Scraper:
    """Helper for common HTML scraping tasks.
    Contains URL manipulation and HTML processing helpers.
    """
    @staticmethod
    def get_parent(url: str) -> str:
        """Retrieves the immediate parent of a URL.

        Args:
            url (str): URL whose parent to retrieve.

        Returns:
            str: Immediate parent of URL.
        """
        parsed_url: ParseResult = urlparse(url)
        new_path: str = "/".join(parsed_url.path.split("/")[:-1])
        return parsed_url._replace(path=new_path).geturl()

    @staticmethod
    def convert_to_text(element: List[html.HtmlElement] | html.Element) -> str:
        """Helper to convert an HTML element to plain text. Insofar as useful
           for predictions, the HTML formatting is converted to a plain text
           representation. As an example, "<sup>1</sup>" is converted to "^1".

        Args:
            element (List[html.HtmlElement] | html.Element): HTML element to
            convert.

        Returns:
            str: Plain text with equivalent formatting using special characters
            to represent the original formatted HTML.
        """
        if isinstance(element, List):
            return "".join([Scraper.convert_to_text(child) for child in element])

        text: str = ""
        suffix: str = ""
        if element.tag == "sup":
            text += SUPERSCRIPT_MARKER
        elif element.tag == "br":
            text += "\n"
        elif element.tag == "p":
            suffix += "\n\n"

        if element.text:
            text += element.text
        text += Scraper.convert_to_text([child for child in element])

        if element.tail:
            text += element.tail

        if text == SUPERSCRIPT_MARKER:
            return ""

        return "" if text == "" else text + suffix
