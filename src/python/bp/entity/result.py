from decimal import Decimal


class DoubleMajorityBallotResult:
    """Double majority ballot result."""

    def __init__(self, percentage_yes: Decimal, accepting_cantons: Decimal) -> None:
        """Ballot voting result for a double majority vote.

        Args:
            percentage_yes (Decimal): Share of population voting yes.
            accepting_cantons (Decimal): Share of cantons voting yes.
        """
        self.percentage_yes = percentage_yes
        self.accepting_cantons = accepting_cantons
