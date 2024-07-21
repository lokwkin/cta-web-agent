from groq import Groq
import time
import os
import logging
from models.base_llm_client import BaseLLMClient, LLMInput, LLMResponse, LLMTokenUsage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GroqClient(BaseLLMClient):
    def __init__(self, log_path: str = './prompt_logs'):
        super().__init__(log_path)
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.client = Groq(
            # This is the default and can be omitted
            api_key=os.environ.get("GROQ_API_KEY"),
        )

    def _request(self, prompt_input: LLMInput) -> LLMResponse:
        ts = time.time()

        response = self.client.chat.completions.create(
            model=os.environ.get("GROQ_MODEL", "llama3-8b-8192"),
            messages=[
                {"role": "system", "content": prompt_input.system_message},
                {"role": "user", "content": prompt_input.user_message},
            ],
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
