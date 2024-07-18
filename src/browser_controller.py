from playwright.sync_api import Page, Browser
from bs4 import Tag
from colorama import Fore, Style
from markdownify import markdownify as md, MarkdownConverter
import uuid
import logging

from models.openai_client import ReActOutput

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

    def prepare_markdown(self) -> str:
        # Assign unique element_id to all elements
        logger.debug(f"Assigning Element IDs to DOM")
        self._dom_assign_element_id()
        
        # Convert the page to markdown preserving neccessary elements
        logger.debug(f"Converting HTML to Markdown...")
        markdown = self._convert_to_markdown()
        return markdown
        

    def digest_action(self, action: ReActOutput):
        logger.debug(f"Performing action: {action.action}")
        if action.action == 'CLICK':
            # Locate the element
            logger.info(f"Locating element_id: {action.action_params['element_id']}")
            target = self.page.locator(f"[element_id=\"{action.action_params['element_id']}\"]")
            logger.info(f"Found element: {(target.first.evaluate('el => el.outerHTML') )}")

            # Click the element
            target.click()

            # Wait for the browser to load react
            logger.info(f"Clicked, awaiting browser load...")
            self.page.wait_for_timeout(3000)

        elif action.action == 'TYPE':
            # Locate the element
            logger.info(f"Locating element_id: {action.action_params['element_id']}")
            target = self.page.locator(f"[element_id=\"{action.action_params['element_id']}\"]")
            logger.info(f"Found element: {(target.first.evaluate('el => el.outerHTML') )}")

            # Type the text
            target.type(action.action_params['text'])

            # Wait for the browser to load react
            logger.info(f"Typed, awaiting browser load...")
            self.page.wait_for_timeout(3000)

        elif action.action == 'FINISH':
            logger.info(f"Finishing the task with output {str(action.action_params['output'])}")

    def _dom_assign_element_id(self):
        def generate_unique_id():
            return f"{uuid.uuid4().hex[:8]}"   
        
        for cta in self.page.get_by_role('link').all():
            cta.evaluate(f"el => el.setAttribute('element_id', '{generate_unique_id()}')")

        # for cta in page.locator('a').all():
        #     cta.evaluate(f"el => el.setAttribute('element_id', '{generate_unique_id()}')")

        for cta in self.page.get_by_role('button').all():
            cta.evaluate(f"el => el.setAttribute('element_id', '{generate_unique_id()}')")

        for cta in self.page.get_by_role('textbox').all():
            cta.evaluate(f"el => el.setAttribute('element_id', '{generate_unique_id()}')")

    def _convert_to_markdown(self):

        class CTAMarkdownConverter(MarkdownConverter):
            def convert_button(self, el: Tag, text, convert_as_inline):
                if 'element_id' not in el.attrs:
                    return ''
                representation = f"{el.text.strip() if len(el.text.strip()) > 0 else ','.join([img.attrs['alt'] for img in el.find_all('img')])}"
                return f"[{representation}](Button)<{el.attrs['element_id']}>\n\n"
            
            def convert_img(self, el, text, convert_as_inline):
                # NOT converting images into markdown, as we are only interested in text
                return ''
            
            def convert_a(self, el: Tag, text, convert_as_inline):
                if 'element_id' not in el.attrs:
                    return super().convert_a(el, text, convert_as_inline)
                return super().convert_a(el, text, convert_as_inline) + f"<{el.attrs['element_id']}>\n\n"
            
            def should_convert_tag(self, tag: Tag):
                if tag in ['a', 'button', 'input']:
                    return True
                return super().should_convert_tag(tag)
            
            def convert_input(self, el: Tag, text, convert_as_inline):
                if 'element_id' not in el.attrs:
                    return ''
                representation = el.attrs['placeholder'] if 'placeholder' in el.attrs else el.text.strip() if len(el.text.strip()) > 0 else ''
                return f"[{representation}]({el.attrs['type']})<{el.attrs['element_id']}>\n\n"
            
        markdown = CTAMarkdownConverter().convert(self.page.content())

        return markdown.strip()


