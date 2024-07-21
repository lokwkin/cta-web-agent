from playwright.sync_api import Page, Browser
from bs4 import Tag
from markdownify import markdownify as MarkdownConverter
import uuid
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

    def prepare_markdown(self) -> str:
        # Assign unique element_id to all elements
        logger.debug("Assigning Element IDs to DOM")
        self._dom_assign_element_id()

        # Convert the page to markdown preserving neccessary elements
        logger.debug("Converting HTML to Markdown...")
        markdown = self._convert_to_markdown()
        return markdown

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

    def _dom_assign_element_id(self):
        def generate_unique_id():
            return f"{uuid.uuid4().hex[:8]}"

        for role in ["search", "searchbox", "textbox", "button", "textbox", "link"]:
            for cta in self.page.get_by_role(role).all():
                cta.evaluate(f"el => el.setAttribute('element_id', '{generate_unique_id()}')")

        for tag in ["textarea"]:
            for cta in self.page.locator(f"{tag}").all():
                cta.evaluate(f"el => el.setAttribute('element_id', '{generate_unique_id()}')")

    def _convert_to_markdown(self):

        class CTAMarkdownConverter(MarkdownConverter):

            def get_element_representation(self, el: Tag):
                if 'aria-label' in el.attrs:
                    return el.attrs['aria-label']
                if 'placeholder' in el.attrs:
                    return el.attrs['placeholder']
                texts = el.get_text(' ', strip=True)
                if len(texts) > 0:
                    return texts
                if len(el.find_all('img')) > 0:
                    return ','.join([img.attrs['alt'] for img in el.find_all('img')])
                return None

            def should_convert_tag(self, tag: str):
                if tag in ['a', 'button', 'input', 'textarea']:
                    return True
                return super().should_convert_tag(tag)

            def convert_button(self, el: Tag, text, convert_as_inline):
                if 'element_id' not in el.attrs:
                    return ''
                return f"[{self.get_element_representation(el)}](Button)<{el.attrs['element_id']}>\n\n"

            def convert_img(self, el, text, convert_as_inline):
                # NOT converting images into markdown, as we are only interested in text
                return ''

            def convert_a(self, el: Tag, text, convert_as_inline):
                if 'element_id' not in el.attrs:
                    return super().convert_a(el, text, convert_as_inline)
                return super().convert_a(el, text, convert_as_inline) + f"<{el.attrs['element_id']}>\n\n"

            def convert_input(self, el: Tag, text, convert_as_inline):
                if 'element_id' not in el.attrs:
                    return ''
                element_type = el.attrs['type'] if 'type' in el.attrs else 'input'
                return f"[{self.get_element_representation(el)}]({element_type})<{el.attrs['element_id']}>\n\n"

            def convert_textarea(self, el: Tag, text, convert_as_inline):
                if 'element_id' not in el.attrs:
                    return ''
                return f"[{self.get_element_representation(el)}](textarea)<{el.attrs['element_id']}>\n\n"

        markdown = CTAMarkdownConverter().convert(self.page.content())

        return markdown.strip()
