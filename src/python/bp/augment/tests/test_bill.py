from bp.augment.bill import BillAugmenter
from bp.augment.chat import Chat
from bp.entity.ballot import BallotStatus, DoubleMajorityBallot, DoubleMajorityBallotResult
from bp.entity.bill import Bill

import unittest
from datetime import datetime
from decimal import Decimal
from numpy.random import default_rng
from typing import Dict, List


class MockChat(Chat):
    def prompt(self, _: List[str]) -> List[str]:
        return [
            """
[
  {
    "title": "gegen das Schlachten ohne vorherige Betäubung",
    "wording": "Die Volksinitiative lautet:\n\nDie Bundesverfassung wird wie folgt ergänzt:\n\nArt. 25^bis (neu)\n\nDas Töten von Tieren ohne vorherige Betäubung vor dem Blutentzuge ist bei jeder Schlachtart und Viehgattung ausnahmslos untersagt."
  },
  {
    "title": "zum Verbot des unbetäubten Schlachtens",
    "wording": "Die Volksinitiative lautet:\n\nDie Bundesverfassung wird wie folgt ergänzt:\n\nArt. 25^bis (neu)\n\nEs ist generell untersagt, Tiere vor dem Blutentzug ohne vorherige Betäubung zu schlachten, unabhängig von der Schlachtart und Viehgattung."
  },
  {
    "title": "für die Betäubung vor dem Schlachten",
    "wording": "Die Volksinitiative lautet:\n\nDie Bundesverfassung wird wie folgt ergänzt:\n\nArt. 25^bis (neu)\n\nBevor Tiere geschlachtet werden, ist eine vorherige Betäubung vor dem Blutentzug zwingend vorgeschrieben, und zwar für jede Schlachtart und Viehgattung."
  },
  {
    "title": "gegen das Schlachten ohne vorherige Betäubungsmethoden",
    "wording": "Die Volksinitiative lautet:\n\nDie Bundesverfassung wird wie folgt ergänzt:\n\nArt. 25^bis (neu)\n\nDas Schlachten von Tieren ohne vorherige Anwendung von Betäubungsmethoden vor dem Blutentzug ist bei jeder Schlachtart und Viehgattung strikt verboten."
  },
  {
    "title": "zum Verbot der betäubungslosen Schlachtung",
    "wording": "Die Volksinitiative lautet:\n\nDie Bundesverfassung wird wie folgt ergänzt:\n\nArt. 25^bis (neu)\n\nEs ist untersagt, Tiere vor dem Blutentzug ohne vorherige Betäubung bei jeder Schlachtart und Viehgattung zu schlachten."
  },
  {
    "title": "für die obligatorische Betäubung vor dem Schlachten",
    "wording": "Die Volksinitiative lautet:\n\nDie Bundesverfassung wird wie folgt ergänzt:\n\nArt. 25^bis (neu)\n\nDie vorherige Betäubung vor dem Blutentzug ist obligatorisch und ausnahmslos für jede Schlachtart und Viehgattung vorgeschrieben."
  },
  {
    "title": "gegen das Töten ohne vorherige Betäubung",
    "wording": "Die Volksinitiative lautet:\n\nDie Bundesverfassung wird wie folgt ergänzt:\n\nArt. 25^bis (neu)\n\nDas Töten von Tieren ohne vorherige Betäubung vor dem Blutentzuge ist bei jeder Schlachtart und Viehgattung ausnahmslos verboten."
  },
  {
    "title": "zum Verbot des unbetäubten Tötens",
    "wording": "Die Volksinitiative lautet:\n\nDie Bundesverfassung wird wie folgt ergänzt:\n\nArt. 25^bis (neu)\n\nEs ist generell untersagt, Tiere vor dem Blutentzug ohne vorherige Betäubung zu töten, unabhängig von der Schlachtart und Viehgattung."
  },
  {
    "title": "für die Betäubung vor dem Töten",
    "wording": "Die Volksinitiative lautet:\n\nDie Bundesverfassung wird wie folgt ergänzt:\n\nArt. 25^bis (neu)\n\nBevor Tiere getötet werden, ist eine vorherige Betäubung vor dem Blutentzug zwingend vorgeschrieben, und zwar für jede Schlachtart und Viehgattung."
  }
]"""]


class TestBillAugmenter(unittest.TestCase):

    def test_paraphrase_and_contradict(self):
        augment: BillAugmenter = TestBillAugmenter.__create_mock_augment()
        augmented_bills: List[Bill] = augment.paraphrase_and_contradict(
            TestBillAugmenter.__get_ballots())
        self.assertListEqual([], augmented_bills)

    def test_augment_vote(self):
        augment: BillAugmenter = TestBillAugmenter.__create_mock_augment()
        result: DoubleMajorityBallotResult = augment._BillAugmenter__augment_vote(
            Decimal("45.52"), Decimal("34.78"), False)
        self.assertLess(result.percentage_yes, Decimal(50.0))
        self.assertLess(result.accepting_cantons, Decimal(50.0))

    def test_augment_vote_flip(self):
        augment: BillAugmenter = TestBillAugmenter.__create_mock_augment()
        result: DoubleMajorityBallotResult = augment._BillAugmenter__augment_vote(
            Decimal("45.52"), Decimal("34.78"), True)
        self.assertGreaterEqual(result.percentage_yes, Decimal(50.0))
        self.assertGreaterEqual(result.accepting_cantons, Decimal(50.0))

    @staticmethod
    def __create_mock_augment():
        return BillAugmenter(MockChat(), default_rng(346615217))

    @staticmethod
    def __get_ballots() -> List[DoubleMajorityBallot]:
        return [DoubleMajorityBallot(
            Bill(
                "für ein Verbot des Schlachtens ohne vorherige Betäubung",
                "Die Volksinitiative lautet:\n\nDie Bundesverfassung wird wie folgt ergänzt:\n\nArt. 25^bis (neu)\n\nDas Schlachten der Tiere ohne vorherige Betäubung vor dem Blutentzuge ist bei jeder Schlachtart und Viehgattung ausnahmslos untersagt.",
                datetime(1892, 5, 10)
            ),
            BallotStatus.COMPLETED,
            DoubleMajorityBallotResult(
                Decimal("52.27"),
                Decimal("60.1")
            )
        )]