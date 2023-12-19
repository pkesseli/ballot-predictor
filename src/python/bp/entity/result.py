from decimal import Decimal


class DoubleMajorityBallotResult:
    """Double majority ballot result."""

    def __init__(self, percentageYes: Decimal, acceptingCantons: Decimal) -> None:
        self.percentageYes = percentageYes
        self.acceptingCantons = acceptingCantons
