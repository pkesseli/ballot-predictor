from bp.entity.ballot import BallotStatus

from datetime import datetime
from jsonpickle.handlers import BaseHandler


class DatetimeHandler(BaseHandler):
    """jsonpickle handler to serialise datetime in human-readable format."""

    def flatten(self, obj: datetime, _) -> str:
        return obj.isoformat()

    def restore(self, obj: str) -> datetime:
        return datetime.fromisoformat(obj)


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
