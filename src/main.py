from playwright.sync_api import sync_playwright, Page, Browser
from colorama import Fore, Style
from dotenv import load_dotenv
from models.openai_client import OpenAIClient
from browser_controller import BrowserController
import argparse
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()

def run(url: str, task: str, playwright):
    
    # Setup    
    browser = playwright.chromium.launch(headless=False)
    browserctl = BrowserController(browser)
    action_history = []

    # Start navigation
    browserctl.navigate(url)

    while True:
        markdown = browserctl.prepare_markdown()

        # Prompt LLM for next action
        logger.debug('Prompting LLM for next action...')
        todo = OpenAIClient().prompt_templated('action', {'markdown': markdown, 'task': task, 'action_history': action_history})
        if todo is None:
            raise Exception("Error: Invalid response from OpenAI API")
        logger.info(f"{Fore.YELLOW}Result from LLM: {str(todo.model_dump())}{Fore.RESET}")


        # Perform action according to the response
        if todo.action == 'FINISH':
            browserctl.get_page_object().pause()
            return todo.action_params['result']
        
        browserctl.digest_action(todo)
        
        # Memorize the action performed
        action_history.append(todo)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("task")
    args = parser.parse_args()
    
    logging.basicConfig(format='%(asctime)s [%(name)s] %(message)s')
    
    with sync_playwright() as playwright:
        run(args.url, args.task, playwright)
    