from dataclasses import dataclass
from typing import Optional
import os
import json
import httpx
from pydantic import BaseModel, Field
from typing import Optional
from openai import OpenAI, DefaultHttpxClient
import pystache

class ChatGPTInput(BaseModel):
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.1
    model: str = "gpt-3.5-turbo"
    system_message: Optional[str] = "You are a helpful assistant. Please respond with valid JSON only."


class OpenAIClient():
    def __init__(self):
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

    def prompt_templated(self, template: str, params: dict):
        with open(f"./src/models/prompts/{template}.txt", "r") as file:
            template = file.read()
            [system_message, user_message] = pystache.render(template, params).split('!!----SEPERATOR----!!')
            result = self.prompt(ChatGPTInput(prompt=user_message, system_message=system_message))
        return result

    def prompt(self, prompt_input: ChatGPTInput):
        try:
            print(f"[REQUEST] <SYSTEM> {str(prompt_input.system_message)}")
            print(f"[REQUEST] <PROMPT> {str(prompt_input.prompt)}")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt_input.system_message},
                    {"role": "user", "content": prompt_input.prompt},
                    {"role": "assistant", "content": "{"}
                ],
                temperature=prompt_input.temperature,
                max_tokens=prompt_input.max_tokens,
            )

            json_data = json.loads(response.choices[0].message.content)

            print(f"[RESPONSE] {str(json_data)}")
            
            return json_data
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSONDecodeError {str(e)}")
            return None
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None