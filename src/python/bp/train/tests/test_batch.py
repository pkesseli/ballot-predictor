from bp.train.batch import Batch


import unittest
from typing import List


class TestBatch(unittest.TestCase):

    def test_split_into_batches(self):
        actual: List[List[int]] = Batch.split_into_batches(
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 3)
        self.assertEqual([
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
            [10, 11, 1]
        ], actual)

    def test_split_into_batches_exact(self):
        actual: List[List[int]] = Batch.split_into_batches(
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 3)
        self.assertEqual([
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
            [10, 11, 12]
        ], actual)
