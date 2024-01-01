import bp.data.serialisation
from bp.data.serialisation import AUGMENTED_INITIATIVES, BallotStatusHandler, DatetimeHandler, DecimalHandler, DoubleMajorityBallotResultHandler, INITIATIVES, Serialisation
from bp.entity.ballot import BallotStatus, Bill, DoubleMajorityBallot, DoubleMajorityBallotResult

import jsonpickle
import tempfile
import unittest
from datetime import datetime
from decimal import Decimal
from typing import List


TEST_BALLOTS: List[DoubleMajorityBallot] = [
    DoubleMajorityBallot(
        Bill(
            "Title",
            "The wording.",
            datetime(2024, 1, 1)
        ),
        BallotStatus.COMPLETED,
        DoubleMajorityBallotResult(
            Decimal("90.1"),
            Decimal("14")
        )
    )
]


class TestSerialisation(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        cls._original_initiatives = INITIATIVES
        cls._original_augmented_initiatives = AUGMENTED_INITIATIVES
        with tempfile.NamedTemporaryFile() as temp_file_generator:
            bp.data.serialisation.INITIATIVES = temp_file_generator.name
        with tempfile.NamedTemporaryFile() as temp_file_generator:
            bp.data.serialisation.AUGMENTED_INITIATIVES = temp_file_generator.name

    @classmethod
    def tearDownClass(cls):
        bp.data.serialisation.INITIATIVES = cls._original_initiatives
        bp.data.serialisation.AUGMENTED_INITIATIVES = cls._original_augmented_initiatives

    async def test_initiatives(self):
        await Serialisation.write_initiatives(TEST_BALLOTS)
        deserialised: List[DoubleMajorityBallot] = await Serialisation.load_initiatives()
        self.assertEqual(1, len(deserialised))

        expected: DoubleMajorityBallot = TEST_BALLOTS[0]
        actual: DoubleMajorityBallot = deserialised[0]
        self.assertEqual(expected.bill.title, actual.bill.title)
        self.assertEqual(expected.bill.wording, actual.bill.wording)
        self.assertEqual(expected.bill.date, actual.bill.date)
        self.assertEqual(expected.status, actual.status)
        self.assertEqual(expected.result.percentage_yes,
                         actual.result.percentage_yes)
        self.assertEqual(expected.result.accepting_cantons,
                         actual.result.accepting_cantons)

    async def test_augmented_initiatives(self):
        await Serialisation.write_augmented_initiatives(TEST_BALLOTS)
        deserialised: List[DoubleMajorityBallot] = await Serialisation.load_augmented_initiatives()
        self.assertEqual(1, len(deserialised))

        expected: DoubleMajorityBallot = TEST_BALLOTS[0]
        actual: DoubleMajorityBallot = deserialised[0]
        self.assertEqual(expected.bill.title, actual.bill.title)
        self.assertEqual(expected.bill.wording, actual.bill.wording)
        self.assertEqual(expected.bill.date, actual.bill.date)
        self.assertEqual(expected.status, actual.status)
        self.assertEqual(expected.result.percentage_yes,
                         actual.result.percentage_yes)
        self.assertEqual(expected.result.accepting_cantons,
                         actual.result.accepting_cantons)


class TestDatetimeHandler(unittest.TestCase):

    def test_flatten(self):
        self.assertEqual("2024-01-01T00:00:00", DatetimeHandler(
            None).flatten(datetime(2024, 1, 1, 0, 0, 0, 0), None))

    def test_restore(self):
        self.assertEqual(datetime(2024, 1, 1, 0, 0, 0, 0), DatetimeHandler(
            None).restore("2024-01-01T00:00:00"))


class TestBallotStatusHandler(unittest.TestCase):

    def test_flatten(self):
        self.assertEqual("pending", BallotStatusHandler(
            None).flatten(BallotStatus.PENDING, None))
        self.assertEqual("failed", BallotStatusHandler(
            None).flatten(BallotStatus.FAILED, None))
        self.assertEqual("completed", BallotStatusHandler(
            None).flatten(BallotStatus.COMPLETED, None))
        self.assertIsNone(BallotStatusHandler(None).flatten(128, None))

    def test_restore(self):
        self.assertEqual(BallotStatus.PENDING,
                         BallotStatusHandler(None).restore("pending"))
        self.assertEqual(BallotStatus.FAILED,
                         BallotStatusHandler(None).restore("failed"))
        self.assertEqual(BallotStatus.COMPLETED,
                         BallotStatusHandler(None).restore("completed"))
        self.assertIsNone(BallotStatusHandler(None).restore("invalid"))


class TestDecimalHandler(unittest.TestCase):

    def test_flatten(self):
        self.assertEqual("17.1", DecimalHandler(
            None).flatten(Decimal("17.1"), None))

    def test_restore(self):
        self.assertEqual(Decimal("4.3"), DecimalHandler(None).restore("4.3"))


class TestDoubleMajorityBallotResultHandler(unittest.TestCase):

    def test_encode(self):
        jsonpickle.handlers.registry.register(
            DoubleMajorityBallotResult, DoubleMajorityBallotResultHandler)
        self.assertEqual("""{
    "accepting_cantons": "5.3",
    "percentage_yes": "10.7",
    "py/object": "bp.entity.result.DoubleMajorityBallotResult"
}""",
                         jsonpickle.encode(DoubleMajorityBallotResult(
                             Decimal("10.7"),
                             Decimal("5.3")
                         )))

    def test_decode(self):
        jsonpickle.handlers.registry.register(
            DoubleMajorityBallotResult, DoubleMajorityBallotResultHandler)
        result: DoubleMajorityBallotResult = jsonpickle.decode(
            """{"accepting_cantons": "5.3", "percentage_yes": "10.7", "py/object": "bp.entity.result.DoubleMajorityBallotResult"}""")
        self.assertEqual(Decimal("10.7"), result.percentage_yes)
        self.assertEqual(Decimal("5.3"), result.accepting_cantons)
