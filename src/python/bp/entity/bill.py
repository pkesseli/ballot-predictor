from datetime import datetime


class Bill:
    """Bill detail information

    Contains all relevant information to perform predictions about the bill.
    """

    def __init__(self, title: str, wording: str, date: datetime):
        """Initialise bill with all relevant properties.

        Args:
            title (str): Official title of the bill.
            body (str): Full legal wording, i.e. body content of bill.
            date (datetime): Submission date of bill. This is the only date we
            consider for our predictions, as a hypothetical new bill queried by
            a user has no other dates (e.g. a federal council review date).
        """
        self.title = title
        self.wording = wording
        self.date = date
