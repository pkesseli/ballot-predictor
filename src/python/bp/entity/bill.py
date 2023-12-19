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
            date (datetime): First date of record associated with the bill.
            This is usually the start of the signature collection phase. Since
            bills can fail at various stages in the process (e.g. not reaching
            the necessary number of signatures in time), and we do not want to
            ask users too many questions about their hypothetical bills, we
            boil time information down to this one date. In a future iteration,
            we might consider averaging out the dates of the bill as a way to
            normalise the time context of bills that took a long time to reach
            the ballot.
        """
        self.title = title
        self.wording = wording
        self.date = date
