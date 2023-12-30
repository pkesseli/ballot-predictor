from bp.augment.chat import Chat

from openai import OpenAI
from openai.types.chat.completion_create_params import ResponseFormat
from openai.types.chat import ChatCompletion, ChatCompletionUserMessageParam
from typing import List


class ChatGpt(Chat):
    """Implements Chat interface using the ChatGPT API.
    """

    def prompt(self, prompts: List[str]) -> List[str]:
        messages: List[ChatCompletionUserMessageParam] = [
            ChatCompletionUserMessageParam(content=prompt, role="user") for prompt in prompts]
        client = OpenAI()
        response: ChatCompletion = client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo"
        )

        return [Chat.remove_json_markup(choice.message.content) for choice in response.choices]
