from abc import ABC, abstractmethod
from typing import List


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


class ChatGpt(Chat):
    """Implements Chat interface using the ChatGPT API.
    """

    def prompt(self, queries: List[str]) -> List[str]:
        return []
