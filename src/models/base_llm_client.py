from abc import abstractmethod
from colorama import Fore, Style
from typing import Optional
import os
import json
from pydantic import BaseModel
from typing import Optional
import pystache
import logging
import time
import os
import json_repair

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LLMInput(BaseModel):
    max_tokens: int = 512
    temperature: float = 0.1
    model: str = "gpt-3.5-turbo"
    system_message: Optional[str] = "You are a helpful assistant. Please respond with valid JSON only."
    user_message: str
    log_identifier: Optional[str] = 'prompt'
    
class LLMTokenUsage(BaseModel):
    input_token: int
    output_token: int
    
class LLMResponse(BaseModel):
    request: LLMInput
    response_str: str
    time_used: float
    usage: LLMTokenUsage
    
class ReActOutput(BaseModel):
    situation: Optional[str]
    options: Optional[str]
    thought: Optional[str]
    action: str
    action_params: Optional[dict]
    action_desc: Optional[str]

class BaseLLMClient():
    def __init__(self, log_path: str = './prompt_logs'):
        # Preload all templates from the prompts folder
        self.templates: dict[str, str] = {}
        for filename in os.listdir('./src/models/prompts/'):
            if filename.endswith(".txt"):
                with open(f"./src/models/prompts/{filename}", "r") as file:
                    logger.info(f"Loading template: {filename[:-4]}")
                    self.templates[filename[:-4]] = file.read()
                    
        self.log_path = log_path
        if not os.path.exists(log_path):
            os.makedirs(log_path)

    def prompt_templated(self, template: str, params: dict):
        content = self.templates.get(template)
        if content is None:
            raise Exception(f"Template {template} not found")

        [system_message, user_message] = pystache.render(content, params).split('>>>>>>>>>>>>>>>> PROMPT_SEPERATOR >>>>>>>>>>>>>>>>')
        result = self.prompt(LLMInput(user_message=user_message, system_message=system_message, log_identifier=template))
        return result

    @abstractmethod
    def _request(self, prompt_input: LLMInput) -> LLMResponse:
        pass
        
    def prompt(self, prompt_input: LLMInput) -> ReActOutput:
        try:
            log_filename = str(int(time.time())) + (f"_{prompt_input.log_identifier}" if prompt_input.log_identifier is not None else '')  + ".log"
            with open(f"{self.log_path}/{log_filename}", 'w') as f:
                f.write(prompt_input.user_message)
                
                logger.debug(f"{Fore.GREEN}[system_message] {json.dumps(prompt_input.system_message)}{Style.RESET_ALL}")
                logger.debug(f"{Fore.CYAN}[user_message] {json.dumps(prompt_input.user_message)}{Style.RESET_ALL}")
                
                llm_response = self._request(prompt_input)
                logger.debug(f"{Fore.BLUE}[response_message] {str(llm_response.response_str)}{Style.RESET_ALL}")
                
                f.write("\n\n>>>>>>>>>>>>>>>> LLM RESPONSE >>>>>>>>>>>>>>>>\n\n")
                f.write(llm_response.response_str)

            try:
                response_dict = json.loads(llm_response.response_str)
            except json.JSONDecodeError as e:
                response_dict = json_repair.loads(llm_response.response_str)
                if response_dict == '': # failed to fix json
                    raise e

            logger.info(f"{Fore.YELLOW}[response_parsed]: {str(response_dict)}{Fore.RESET}")
            thought_action = ReActOutput(**response_dict)
                
            return thought_action
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            raise e
