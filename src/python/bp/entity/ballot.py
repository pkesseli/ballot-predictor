from bp.entity.bill import Bill
from bp.entity.result import DoubleMajorityBallotResult


class DoubleMajorityBallot:
    """Double majority ballot consisting of bill details information and an
    optional result, if the ballot has already taken place.
    """

    def __init__(self, bill: Bill, result: DoubleMajorityBallotResult | None) -> None:
        """Initialises the ballot with all properties.

        Args:
            bill (Bill): Details information about bill on the ballot.
            result (DoubleMajorityBallotResult | None): Optional ballot result.
        """
        self.bill = bill
        self.result = result
