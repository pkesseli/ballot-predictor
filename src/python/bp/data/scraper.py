import re
from lxml import html
from typing import List
from urllib.parse import urlparse, ParseResult


SUPERSCRIPT_MARKER: str = "^"
"""str: Superscript prefix used in HTML to plain text conversions."""


SUPERSCRIPT_MARKER_ONLY_PATTERN: re.Pattern = re.compile("^\s*\^\s*$")
"""re.Pattern: Pattern matching strings which only contain whitespaces and the
superscript marker."""


WHITESPACE_ONLY_PATTERN: re.Pattern = re.compile("^\s*$")
"""re.Pattern: Matches strings which only contain whitespaces. Used for removal
of empty lines."""


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
           Furthermore, we try to map various special characters to ASCII ones
           for better comparability between initiatives, e.g. special hyphen
           characters will be mapped to "-".

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
        if element.tag == "ol":
            index = 1
            for li in element:
                text += str(index)
                text += ". "
                text += Scraper.convert_to_text(li)
                text += "\n"
                index += 1
            text += "\n"
            return text

        is_paragraph: bool = False
        if element.tag == "sup":
            text += SUPERSCRIPT_MARKER
        elif element.tag == "br":
            text = text.rstrip(" ")
            text += "\n"
        elif element.tag == "p":
            is_paragraph = True
        elif element.tag == "div" and element.get("id") == "contentNavigation":
            return ""

        if element.text:
            text += element.text
        text += Scraper.convert_to_text([child for child in element])

        if element.tail:
            text += element.tail

        if text == "" or re.match(SUPERSCRIPT_MARKER_ONLY_PATTERN, text):
            return ""

        if is_paragraph:
            if re.match(WHITESPACE_ONLY_PATTERN, text):
                return ""
            text = text.rstrip(" ")
            text += "\n\n"
        text = text.replace("\xa0", " ")
        text = text.replace("\u00ad", "")
        text = text.replace("\u2013", "-")
        text = text.replace("\u002d", "-")
        return text
