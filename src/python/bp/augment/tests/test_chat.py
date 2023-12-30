from bp.augment.chat import CachedChat, Chat

import aiofiles
import jsonpickle
import os
import tempfile
import unittest
from typing import List


class MockChat(Chat):

    def prompt(self, queries: List[str]) -> List[str]:
        return super().prompt(queries)


class TestChat(unittest.TestCase):

    def test_prompt(self):
        chat = MockChat()
        self.assertIsNone(chat.prompt(None))

    def test_remove_json_markup(self):
        self.assertEqual("""[
  {
    \"title\": \"Title\",
    \"wording\": \"Wording\"
  }
]
""", Chat.remove_json_markup("""```json
[
  {
    \"title\": \"Title\",
    \"wording\": \"Wording\"
  }
]
```"""))


class CountingEchoChat(Chat):

    def __init__(self) -> None:
        self.history = {}

    def prompt(self, queries: List[str]) -> List[str]:
        for query in queries:
            current_count: int = self.history.get(query)
            if current_count is None:
                current_count = 0
            self.history[query] = current_count + 1
        return queries


class TestCountingEchoChat(unittest.TestCase):

    def test_prompt(self):
        chat = CountingEchoChat()
        self.assertListEqual(
            ["prompt-1"],
            chat.prompt(["prompt-1"]))
        self.assertDictEqual(
            {"prompt-1": 1},
            chat.history
        )
        self.assertListEqual(
            ["prompt-1"],
            chat.prompt(["prompt-1"]))
        self.assertDictEqual(
            {"prompt-1": 2},
            chat.history
        )


class TestCachedChat(unittest.IsolatedAsyncioTestCase):

    async def test_prompt(self):
        cache_file: str
        with tempfile.NamedTemporaryFile() as temp_file_generator:
            cache_file = temp_file_generator.name

        try:
            wrapped_chat = CountingEchoChat()
            async with CachedChat(wrapped_chat, cache_file) as chat:
                self.assertListEqual(
                    ["prompt-1", "prompt-2"],
                    chat.prompt(["prompt-1", "prompt-2"]))
                self.assertListEqual(
                    ["prompt-1"],
                    chat.prompt(["prompt-1"])
                )
                self.assertListEqual(
                    ["prompt-3"],
                    chat.prompt(["prompt-3"])
                )
                self.assertDictEqual(
                    {
                        "prompt-1": 1,
                        "prompt-2": 1,
                        "prompt-3": 1
                    },
                    wrapped_chat.history
                )

            serialised: str
            async with aiofiles.open(cache_file) as file:
                serialised = await file.read()
            self.assertDictEqual(
                {
                    "prompt-1": "prompt-1",
                    "prompt-2": "prompt-2",
                    "prompt-3": "prompt-3"
                },
                jsonpickle.decode(serialised))

            async with CachedChat(wrapped_chat, cache_file) as chat:
                self.assertListEqual(
                    ["prompt-1", "prompt-2", "prompt-3"],
                    chat.prompt(["prompt-1", "prompt-2", "prompt-3"]))
                self.assertDictEqual(
                    {
                        "prompt-1": 1,
                        "prompt-2": 1,
                        "prompt-3": 1
                    },
                    wrapped_chat.history
                )
        finally:
            os.remove(cache_file)
