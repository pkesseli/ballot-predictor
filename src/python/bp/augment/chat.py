import aiofiles
import jsonpickle
import re
import os
from abc import ABC, abstractmethod
from hashlib import sha256
from typing import List, Coroutine


REMOVE_JSON_MARKUP: re.Pattern = re.compile("```json\n?(.*)```", re.DOTALL)
"""re.Pattern: Regex pattern intended for use with re.Pattern.sub to remove
optional JSON markup from a chat response."""


class Chat(ABC):
    """Implementing classes accept batch prompts for a chat model. This is used
    for data augmentation, generating paraphrased bills or bills with opposite
    meaning using prompt engineering.
    """

    @abstractmethod
    def prompt(self, queries: List[str]) -> List[str]:
        """Batch chat prompt.

        Args:
            queries (List[str]): All queries to send to the chat model.

        Returns:
            List[str]: Response for each query.
        """
        pass

    @staticmethod
    def remove_json_markup(response: str) -> str:
        """Removes optional markup for JSON code in a string. ChatGPT for
        example sometimes includes such markup.

        Args:
            response (str): Text from which to remove markup.

        Returns:
            str: JSON without any markup formatting.
        """
        return REMOVE_JSON_MARKUP.sub("\\1", response)


CACHE_FILE: str = "../resources/openai/cache.json"
"""str: Location of cache JSON file relative to this module."""


class CachedChat(Chat):
    """Decorator Chat implementation caching previously executed queries.
    """

    def __init__(self, chat: Chat, cache_file: str = CACHE_FILE):
        """

        Args:
            chat (Chat): Chat implementation to which to add a cache.
            cache_file (str, optional): Path to persistent JSON file to store
            cache on exit. Will be loded in __aenter__ and written in
            __aexit__. Defaults to CACHE_FILE.
        """
        self.chat = chat
        self.cache_file = cache_file

    async def __aenter__(self):
        """Loads the JSON cache file into memory."""
        path: str = self.__get_cache_file_path()
        if os.path.isfile(path):
            serialised: str
            async with aiofiles.open(path) as file:
                serialised = await file.read()
            cache: dict[str, str] = jsonpickle.decode(serialised)
            self.cache = cache
        else:
            self.cache = {}
        return self

    def prompt(self, queries: List[str]) -> List[str]:
        """Invokes the wrapped prompt method whie caching previous query
        results.

        Args:
            queries (List[str]): All queries to execute.

        Returns:
            List[str]: Potentially cached response for each query.
        """
        responses: List[str] = [None] * len(queries)
        uncached_queries: List[str] = []
        index: int = 0
        while index < len(queries):
            query: str = queries[index]
            cached_response: str = self.cache.get(query)
            if cached_response is None:
                uncached_queries.append(query)
            else:
                responses[index] = cached_response
            index = index + 1

        if len(uncached_queries) > 0:
            new_responses: List[str] = self.chat.prompt(uncached_queries)
            index = 0
            for response in new_responses:
                while responses[index] is not None:
                    index = index + 1
                responses[index] = response
                self.cache[queries[index]] = response

        return responses

    def __get_cache_file_path(self) -> str:
        """Provides the path to the serialised JSON cache file, persisting
        cached query results.

        Returns:
            str: Path to JSON cache file.
        """
        module_location: str = os.path.dirname(__file__)
        return os.path.join(module_location, self.cache_file)

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> Coroutine:
        """Writes in-memory cache to cache JSON file on exit."""
        serialised: str = jsonpickle.encode(self.cache)
        path: str = self.__get_cache_file_path()
        async with aiofiles.open(path, "w") as file:
            await file.write(serialised)
