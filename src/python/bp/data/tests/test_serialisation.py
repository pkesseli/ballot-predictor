from bp.data.serialisation import BallotStatusHandler, DatetimeHandler
from bp.entity.ballot import BallotStatus

import unittest
from datetime import datetime


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
