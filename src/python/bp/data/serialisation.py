from bp.entity.ballot import Bill, DoubleMajorityBallot, DoubleMajorityBallotResult, BallotStatus

import aiofiles
import jsonpickle
import os
from datetime import datetime
from decimal import Decimal
from jsonpickle import Pickler, Unpickler
from jsonpickle.handlers import BaseHandler
from jsonpickle.tags import OBJECT
from typing import Any, List


INITIATIVES: str = "../resources/bk.admin.ch/initiatives.json"
"""str: Relative path from python source root to initiatives JSON file."""


AUGMENTED_INITIATIVES: str = "../resources/bk.admin.ch/augmented-initiatives.json"
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

    @staticmethod
    def __to_module_path(file_path: str) -> str:
        """Takes a relative path and applies it relative to the module
        location, producing an absolute path.

        Args:
            file_path (str): Relative path to turn into absolute one.

        Returns:
            str: Absolute path to file.
        """
        module_location: str = os.path.dirname(__file__)
        return os.path.join(module_location, file_path)


INITIATIVES: str = Serialisation._Serialisation__to_module_path(INITIATIVES)
AUGMENTED_INITIATIVES: str = Serialisation._Serialisation__to_module_path(
    AUGMENTED_INITIATIVES)


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
            OBJECT: "bp.entity.bill.Bill"
        }

    def restore(self, obj: dict[str, str]) -> Bill:
        return Bill(
            obj["title"],
            obj["wording"],
            DatetimeHandler(self.context).restore(obj["date"]))


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
        pickler: Pickler = self.context
        return {
            "bill": pickler.flatten(obj.bill, False),
            "status": BallotStatusHandler(self.context).flatten(obj.status, _),
            "result": pickler.flatten(obj.result, False),
            OBJECT: "bp.entity.ballot.DoubleMajorityBallot"
        }

    def restore(self, obj: dict[str, Any]) -> DoubleMajorityBallot:
        unpickler: Unpickler = self.context
        return DoubleMajorityBallot(
            unpickler.restore(obj["bill"], False),
            BallotStatusHandler(self.context).restore(obj["status"]),
            unpickler.restore(obj["result"], False)
        )


class DoubleMajorityBallotResultHandler(BaseHandler):
    """jsonpickle handler to serialise DoubleMajorityBallotResult instances.
    This explicit handler is necessary since the default serialisation
    deserialises Decimal instances as str. This handler instantiates them as
    Decimals.
    """

    def flatten(self, obj: DoubleMajorityBallotResult, data) -> dict[str, str]:
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
