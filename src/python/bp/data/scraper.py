from urllib.parse import urlparse, ParseResult


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
