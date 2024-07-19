import requests
import time
import os
import logging
from models.base_llm_client import BaseLLMClient, LLMInput, LLMResponse, LLMTokenUsage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class OllamaClient(BaseLLMClient):
    def __init__(self, log_path: str = './prompt_logs'):
        super().__init__(log_path)
        self.url=os.environ.get("OLLAMA_API_URL")

    def _request(self, prompt_input: LLMInput) -> LLMResponse:
        ts = time.time()
        raw_response = requests.post(self.url, json={
            "model": "phi3:mini-128k",
            "prompt": prompt_input.user_message,
            "system": prompt_input.system_message,
            "format": "json",
            "stream": False
        })
        
        raw_response.raise_for_status()
        response = raw_response.json()

        return LLMResponse(
            request=prompt_input,
            response_str=response['response'],
            time_used=time.time() - ts,
            usage=LLMTokenUsage(
                input_token=response['prompt_eval_count'],
                output_token=response['eval_count'],
            )
        )