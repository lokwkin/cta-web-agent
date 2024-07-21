import time
import os
from openai import OpenAI, DefaultHttpxClient
import logging

from models.base_llm_client import BaseLLMClient, LLMInput, LLMResponse, LLMTokenUsage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class OpenAIClient(BaseLLMClient):
    def __init__(self, log_path: str = './prompt_logs'):
        super().__init__(log_path)
        if os.environ.get("OPENAI_PROXY_URL") is not None:
            self.client = OpenAI(
                api_key=os.environ.get("OPENAI_API_KEY"),
                http_client=DefaultHttpxClient(
                    proxy=os.environ.get("OPENAI_PROXY_URL"),
                ),
            )
        else:
            self.client = OpenAI(
                api_key=os.environ.get("OPENAI_API_KEY"),
            )

    def _request(self, prompt_input: LLMInput) -> LLMResponse:
        ts = time.time()
        response = self.client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": prompt_input.system_message},
                {"role": "user", "content": prompt_input.user_message},
            ],
            temperature=prompt_input.temperature,
            max_tokens=prompt_input.max_tokens,
            response_format={"type": "json_object"},
        )

        return LLMResponse(
            request=prompt_input,
            response_str=response.choices[0].message.content,
            time_used=time.time() - ts,
            usage=LLMTokenUsage(
                input_token=response.usage.prompt_tokens,
                output_token=response.usage.completion_tokens,
            )
        )
