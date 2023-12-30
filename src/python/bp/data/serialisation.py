from bp.entity.ballot import DoubleMajorityBallotResult, BallotStatus

from datetime import datetime
from decimal import Decimal
from jsonpickle.handlers import BaseHandler


class DatetimeHandler(BaseHandler):
    """jsonpickle handler to serialise datetime in human-readable format."""

    def flatten(self, obj: datetime, _) -> str:
        return obj.isoformat()

    def restore(self, obj: str) -> datetime:
        return datetime.fromisoformat(obj)


class DoubleMajorityBallotResultHandler(BaseHandler):
    """jsonpickle handler to serialise DoubleMajorityBallotResult instances.
    This explicit handler is necessary since the default serialisation
    deserialises Decimal instances as str. This handler instantiates them as
    Decimals.
    """

    def flatten(self, obj: DoubleMajorityBallotResult, _) -> dict[str, str]:
        return {
            "accepting_cantons": str(obj.accepting_cantons),
            "percentage_yes": str(obj.percentage_yes),
            "py/object": "bp.entity.result.DoubleMajorityBallotResult"
        }

    def restore(self, obj: dict[str, str]) -> DoubleMajorityBallotResult:
        return DoubleMajorityBallotResult(
            Decimal(obj["percentage_yes"]),
            Decimal(obj["accepting_cantons"])
        )


class BallotStatusHandler(BaseHandler):
    """jsonpickle handler to serialise ballot status enums in human-readable
    format.
    """

    def flatten(self, obj: BallotStatus, _) -> str:
        match obj:
            case BallotStatus.PENDING:
                return "pending"
            case BallotStatus.FAILED:
                return "failed"
            case BallotStatus.COMPLETED:
                return "completed"

    def restore(self, obj: str) -> BallotStatus:
        match obj:
            case "pending":
                return BallotStatus.PENDING
            case "failed":
                return BallotStatus.FAILED
            case "completed":
                return BallotStatus.COMPLETED


class DecimalHandler(BaseHandler):
    """jsonpickle handler to serialise decimals in more straightforward format.
    """

    def flatten(self, obj: Decimal, _) -> str:
        return str(obj)

    def restore(self, obj: str) -> Decimal:
        return Decimal(obj)
