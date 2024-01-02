from typing import List, TypeVar


T = TypeVar("T")
"""TypeVar: Type argument for generic batch operations."""


class Batch:
    """Helper to split datasets into batches."""

    @staticmethod
    def split_into_batches(list: List[T], batch_size: int) -> List[List[T]]:
        """Splits list into batches of exactly batch_size. If len(list) is not
        divisible by batch_size, the last batch will be tiled with elements
        from the first batch.

        Args:
            list (List[T]): List to split into batches.
            batch_size (int): Size of a batch.

        Returns:
            List[List[T]]: Data from list split into batches of batch_size.
        """
        result: List[List[T]] = [[]]
        current_list: List[T] = result[0]
        for element in list:
            if len(current_list) == batch_size:
                current_list = []
                result.append(current_list)
            current_list.append(element)

        index: int = 0
        while (len(current_list) < batch_size):
            tiled_element: T = list[index % len(list)]
            current_list.append(tiled_element)
            index = index + 1

        return result
