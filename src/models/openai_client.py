from colorama import Fore, Style
from typing import Optional
import os
import json
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI, DefaultHttpxClient
import pystache
import logging
import os
import json_repair

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LLMInput(BaseModel):
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.1
    model: str = "gpt-3.5-turbo"
    system_message: Optional[str] = "You are a helpful assistant. Please respond with valid JSON only."
    
class ReActOutput(BaseModel):
    situation: str
    thought: str
    expectation: str
    action: str
    action_params: dict

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

        # Preload all templates from the prompts folder
        self.templates: dict[str, str] = {}
        for filename in os.listdir('./src/models/prompts/'):
            if filename.endswith(".txt"):
                with open(f"./src/models/prompts/{filename}", "r") as file:
                    logger.info(f"Loading template: {filename[:-4]}")
                    self.templates[filename[:-4]] = file.read()

    def prompt_templated(self, template: str, params: dict):
        logger.info('self.templates' + str(self.templates))
        content = self.templates.get(template)
        if content is None:
            raise Exception(f"Template {template} not found")

        [system_message, user_message] = pystache.render(content, params).split('!!----SEPERATOR----!!')
        result = self.prompt(LLMInput(prompt=user_message, system_message=system_message))
        return result

    def prompt(self, prompt_input: LLMInput) -> ReActOutput:
        try:
            logger.debug(f"{Fore.GREEN}[system_prompt] {json.dumps(prompt_input.system_message)}{Style.RESET_ALL}")
            logger.info(f"{Fore.CYAN}[user_prompt] {json.dumps(prompt_input.prompt)}{Style.RESET_ALL}")
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
            logger.info(f"{Fore.BLUE}[response] {str(response)}{Style.RESET_ALL}")

            json_data = json_repair.loads(response.choices[0].message.content)
            
            thought_action = ReActOutput(**json_data)
            
            return thought_action
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return None