from bp.data.serialisation import BallotStatusHandler, DatetimeHandler, DecimalHandler, DoubleMajorityBallotResultHandler
from bp.entity.ballot import BallotStatus, DoubleMajorityBallotResult

import jsonpickle
import unittest
from datetime import datetime
from decimal import Decimal


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
        self.assertEqual("""{"accepting_cantons": "5.3", "percentage_yes": "10.7", "py/object": "bp.entity.result.DoubleMajorityBallotResult"}""",
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
