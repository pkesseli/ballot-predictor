from bp.entity.bill import Bill
from bp.entity.result import DoubleMajorityBallotResult

from enum import Enum


class BallotStatus(Enum):
    """Simplification of all possible real-world states in which a ballot could
    be. In reality, ballots may fail for a variety of reasons without vote, but
    we summarise them into one failing state at the moment due to small sample
    sizes for the various subcategories.
    """
    PENDING = 1
    """No vote was held on the measure yet. This is also used for ballots where
    we would like to generate a prediction.
    """
    FAILED = 2
    """The measure failed without a vote."""
    COMPLETED = 3
    """A vote was held on the measure, implying that a respective result is
    available.
    """


class DoubleMajorityBallot:
    """Double majority ballot consisting of bill details information and an
    optional result, if the ballot has already taken place.
    """

    def __init__(self, bill: Bill, status: BallotStatus, result: DoubleMajorityBallotResult | None) -> None:
        """Initialises the ballot with all properties.

        Args:
            bill (Bill): Details information about bill on the ballot.
            status (BallotStatus): Indicates whether a ballot is still pending,
            was already held actually held or wheher the measure failed without
            vote.
            result (DoubleMajorityBallotResult | None): Optional ballot result.
        """
        self.bill = bill
        self.status = status
        self.result = result
