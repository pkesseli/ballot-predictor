from bp.data.chronology import Chronology, POPULAR_INITIATIVES_CHRONOLOGY
from bp.entity.bill import Bill

import unittest
from datetime import datetime
from typing import List


class TestStringMethods(unittest.TestCase):

    def test_get_bills(self):
        chronology = Chronology(POPULAR_INITIATIVES_CHRONOLOGY)
        ballots: List[str] = chronology.get_bills()
        for ballot in ballots:
            self.assertRegex(
                ballot, "https://www.bk.admin.ch/ch/d/pore/vi/vis\d+.html")

    def test_get_bill(self):
        bill: Bill = Chronology.get_bill("https://www.bk.admin.ch/ch/d/pore/vi/vis457.html")
        self.assertEqual("Default title", bill.title)
        self.assertEqual("Default wording", bill.wording)
        self.assertEqual(datetime(2024, 1, 1, 0, 0, 0, 0), bill.date)
