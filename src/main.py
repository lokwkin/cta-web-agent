from playwright.sync_api import sync_playwright, Page, Browser
from colorama import Fore, Style
from dotenv import load_dotenv
from models.openai_client import OpenAIClient
from browser_controller import BrowserController
import argparse
import utils
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()

def run(url: str, task: str, playwright):
    
    llm_client = OpenAIClient(log_path=f"./prompt_logs/{utils.normalize_url(url)}")
    
    # Setup    
    browser = playwright.chromium.launch(headless=False)
    browserctl = BrowserController(browser)
    action_histories = []

    # Start navigation
    browserctl.navigate(url)

    while True:
        markdown = browserctl.prepare_markdown()

        # Prompt LLM for next action
        logger.debug('Prompting LLM for next action...')
        
        action_histories_dict = [h.action_desc for h in action_histories]
        
        todo = llm_client.prompt_templated('action', {'markdown': markdown, 'task': task, 'action_history': action_histories_dict})
        

        # Perform action according to the response
        if todo.action == 'FINISH':
            browserctl.get_page_object().pause()
            return todo.action_params['result']
        
        browserctl.digest_action(todo)
        
        # Memorize the action performed
        action_histories.append(todo)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("task")
    args = parser.parse_args()
    
    logging.basicConfig(format='%(asctime)s [%(name)s] %(message)s')
    
    with sync_playwright() as playwright:
        run(args.url, args.task, playwright)
