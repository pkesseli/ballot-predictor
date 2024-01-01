from bp.entity.ballot import Bill, DoubleMajorityBallot, DoubleMajorityBallotResult, BallotStatus

import aiofiles
import jsonpickle
from datetime import datetime
from decimal import Decimal
from jsonpickle.handlers import BaseHandler
from typing import Any, List


INITIATIVES: str = "bp/resources/bk.admin.ch/initiatives.json"
"""str: Relative path from python source root to initiatives JSON file."""


AUGMENTED_INITIATIVES: str = "bp/resources/bk.admin.ch/augmented-initiatives.json"
"""str: Relative path from python source root to augmented initiatives JSON
file."""


class Serialisation:
    """Helper to serialise and deserialise JSON data."""

    @staticmethod
    async def write_initiatives(ballots: List[DoubleMajorityBallotResult]):
        """Persist original initiatives downloaded from bk.admin.ch.

        Args:
            ballots (List[DoubleMajorityBallotResult]): Downloaded double
            majority ballots.
        """
        await Serialisation.__encode_and_write(ballots, INITIATIVES)

    @staticmethod
    async def write_augmented_initiatives(ballots: List[DoubleMajorityBallotResult]):
        """Persist augmented initiatives downloaded from bk.admin.ch.

        Args:
            ballots (List[DoubleMajorityBallotResult]): Augmented double
            majority ballots.
        """
        await Serialisation.__encode_and_write(ballots, AUGMENTED_INITIATIVES)

    @staticmethod
    async def load_initiatives() -> List[DoubleMajorityBallotResult]:
        """Deserialise persisted initiatives.

        Returns:
            List[DoubleMajorityBallotResult]: Previously persisted initiatives.
        """
        return await Serialisation.__decode_and_read(INITIATIVES)

    @staticmethod
    async def load_augmented_initiatives() -> List[DoubleMajorityBallotResult]:
        """Deserialise persisted augmented initiatives.

        Returns:
            List[DoubleMajorityBallotResult]: Previously persisted augmented
            initiatives.
        """
        return await Serialisation.__decode_and_read(AUGMENTED_INITIATIVES)

    @staticmethod
    async def __decode_and_read(file_path: str) -> Any:
        """Helper to decode a JSON object from a file.

        Args:
            file_path (str): Path to JSON file.

        Returns:
            Any: Deserialised python object.
        """
        serialised: str
        async with aiofiles.open(file_path) as file:
            serialised = await file.read()
        return jsonpickle.decode(serialised)

    @staticmethod
    async def __encode_and_write(value: Any, file_path: str):
        """Helper to encode a Python object to a JSON file.

        Args:
            value (Any): Object to serialise.
            file_path (str): JSON file to write.
        """
        serialised: str = jsonpickle.encode(value)
        async with aiofiles.open(file_path, "w") as file:
            await file.write(serialised)


class BillHandler(BaseHandler):
    """jsonpickle handler to serialise Bill instances. This explicit handler is
    necessary since the default serialisation deserialises datetime instances
    as str. This handler instantiates them correctly.
    """

    def flatten(self, obj: Bill, _) -> dict[str, str]:
        return {
            "title": str(obj.title),
            "wording": str(obj.wording),
            "date": DatetimeHandler(self.context).flatten(obj.date, _),
            "py/object": "bp.entity.bill.Bill"
        }

    def restore(self, obj: dict[str, str]) -> Bill:
        return Bill(
            obj["title"],
            obj["wording"],
            DatetimeHandler(self.context).restore(obj["date"])
        )


class DatetimeHandler(BaseHandler):
    """jsonpickle handler to serialise datetime in human-readable format."""

    def flatten(self, obj: datetime, _) -> str:
        return obj.isoformat()

    def restore(self, obj: str) -> datetime:
        return datetime.fromisoformat(obj)


class DoubleMajorityBallotHandler(BaseHandler):
    """jsonpickle handler to serialise DoubleMajorityBallot instances. This
    explicit handler is necessary since the default serialisation deserialises
    enums and Decimal instances as str. This handler instantiates them
    correctly.
    """

    def flatten(self, obj: DoubleMajorityBallot, _) -> dict[str, Any]:
        return {
            "bill": BillHandler(self.context).flatten(obj.bill, _),
            "status": BallotStatusHandler(self.context).flatten(obj.status, _),
            "result": DoubleMajorityBallotResultHandler(self.context).flatten(obj.result, _),
            "py/object": "bp.entity.ballot.DoubleMajorityBallot"
        }

    def restore(self, obj: dict[str, Any]) -> DoubleMajorityBallot:
        return DoubleMajorityBallot(
            BillHandler(self.context).restore(obj["bill"]),
            BallotStatusHandler(self.context).restore(obj["status"]),
            DoubleMajorityBallotResultHandler(
                self.context).restore(obj["result"])
        )


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
