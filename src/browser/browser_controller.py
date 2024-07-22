from playwright.sync_api import Page, Browser
import logging
from models.base_llm_client import ReActOutput

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BrowserController:

    page: Page
    action_history: list[ReActOutput] = []

    def __init__(self, browser: Browser):
        self.page = browser.new_page()

    def navigate(self, url: str):
        self.page.goto(url)
        self.page.wait_for_load_state('networkidle')

    def get_page_object(self) -> Page:
        return self.page

    def digest_action(self, action: ReActOutput):
        logger.debug(f"Performing action: {action.action}")
        if action.action == 'CLICK':
            # Locate the element
            logger.info(f"Locating element_id: {action.action_params['element_id']}")
            target = self.page.locator(f"[element_id=\"{action.action_params['element_id']}\"]")
            logger.info(f"Found element: {(target.first.evaluate('el => el.outerHTML'))}")

            # Click the element
            target.click()

            # Wait for the browser to load react
            logger.info("Clicked, awaiting browser load...")
            self.page.wait_for_timeout(3000)

        elif action.action == 'TYPE':
            # Locate the element
            logger.info(f"Locating element_id: {action.action_params['element_id']}")
            target = self.page.locator(f"[element_id=\"{action.action_params['element_id']}\"]")
            logger.info(f"Found element: {(target.first.evaluate('el => el.outerHTML'))}")

            # Type the text
            logger.info(f"Entering text: {action.action_params['text']}")
            target.type(action.action_params['text'])

            # Wait for the browser to load react
            if action.action_params.get('press_enter', False):
                logger.info("Pressing enter...")
                target.press('Enter')
                logger.info("Awaiting browser load...")
                self.page.wait_for_timeout(3000)

        elif action.action == 'FINISH':
            logger.info(f"Finishing the task with output {str(action.action_params['output'])}")

