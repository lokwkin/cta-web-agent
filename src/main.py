from playwright.sync_api import sync_playwright, Playwright
from dotenv import load_dotenv
import time
from models.openai_client import OpenAIClient
import page_reader
import argparse
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()

def run(url: str, task: str, playwright: Playwright):
    
    # ts = int(time.time())
    
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(url)
    page.wait_for_load_state('networkidle')         

    action_history = []
    while True:
        # Assign unique element_id to all elements
        logger.debug('[Controller] Assigning Element IDs to DOM')
        page_reader.dom_assign_element_id(page)

        # Convert the page to markdown preserving neccessary elements
        logger.debug('[Controller] Converting HTML to Markdown...')
        markdown = page_reader.convert_to_markdown(page)

        # Prompt LLM for next action
        logger.debug('[Controller] Prompting LLM for next action...')
        result = OpenAIClient().prompt_templated('action', {'markdown': markdown, 'task': task, 'action_history': action_history})
        logger.info(f'[Controller] Result from LLM: {str(result)}')
        if result is None:
            raise Exception("Error: Invalid response from OpenAI API")

        # Perform action accordingly to the response
        logger.debug(f"[Browser] Performing action: {result.action}")
        if result.action == 'CLICK':
            # Locate the element
            logger.info(f"[Browser] Locating element_id: {result.action_params['element_id']}")
            target = page.locator(f"[element_id=\"{result.action_params['element_id']}\"]")
            logger.info(f"[Browser] Found element: {(target.first.evaluate('el => el.outerHTML') )}")

            # Click the element
            target.click()

            # Wait for the browser to load react
            logger.info(f"[Browser] Clicked, awaiting browser load...")
            page.wait_for_timeout(3000)

        elif result.action == 'TYPE':
            # Locate the element
            logger.info(f"[Browser] Locating element_id: {result.action_params['element_id']}")
            target = page.locator(f"[element_id=\"{result.action_params['element_id']}\"]")
            logger.info(f"[Browser] Found element: {(target.first.evaluate('el => el.outerHTML') )}")

            # Type the text
            target.type(result.action_params['text'])

            # Wait for the browser to load react
            logger.info(f"[Browser] Typed, awaiting browser load...")
            page.wait_for_timeout(3000)

        elif result.action == 'FINISH':
            logger.info(f"Finishing the task with output {str(result.action_params['output'])}")
            break
        
        action_history.append({"thought": result.thought, "action": result.action})

    # Do not auto close the broser
    page.pause()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("task")
    args = parser.parse_args()
    
    logging.basicConfig(format='%(asctime)s [%(name)s] %(message)s')

    with sync_playwright() as playwright:
        run(args.url, args.task, playwright)
        
    