from bp.augment.chat import Chat

from openai import OpenAI
from openai.types import Completion
from typing import List


class ChatGpt(Chat):
    """Implements Chat interface using the ChatGPT API.
    """

    def prompt(self, prompts: List[str]) -> List[str]:
        client = OpenAI()
        response: Completion = client.completions.create(
            model="gpt-3.5-turbo",
            prompt=prompts,
            max_tokens=1000
        )

        responses: List[str] = [""] * len(prompts)
        for choice in response.choices:
            responses[choice.index] = choice.text
        return responses
