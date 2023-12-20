from decimal import Decimal


class DoubleMajorityBallotResult:
    """Double majority ballot result."""

    def __init__(self, percentageYes: Decimal, acceptingCantons: Decimal) -> None:
        """Ballot voting result for a double majority vote.

        Args:
            percentageYes (Decimal): Share of population voting yes.
            acceptingCantons (Decimal): Share of cantons voting yes.
        """
        self.percentageYes = percentageYes
        self.acceptingCantons = acceptingCantons
