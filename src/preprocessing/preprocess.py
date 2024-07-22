from typing import Callable, Optional
from playwright.sync_api import Page
import logging
from bs4 import BeautifulSoup, Tag
from markdownify import MarkdownConverter
import uuid
from preprocessing.html_chunking import chunk_html

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

PRESERVE_TAGS = ['a', 'button', 'input', 'textarea']


class Preprocessor():

    def __init__(self, page: Page) -> None:
        self.page = page
        pass

    def prepare_markdown(self) -> str:
        # Assign unique element_id to all elements
        logger.debug("Assigning Element IDs to DOM")
        self._dom_assign_element_id()

        # Convert the page to markdown preserving neccessary elements
        logger.debug("Converting HTML to Markdown...")
        markdown = self._convert_to_markdown()
        return markdown

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
                if tag in PRESERVE_TAGS:
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
                    return ''
                return f"[{self.get_element_representation(el)}](/url)<{el.attrs['element_id']}>\n\n"

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

    def prepare_necessary_chunks(self, provider: str, model: str, max_token: int):

        soup = BeautifulSoup(self.page.content(), 'html.parser')

        # Filter out unnecessary branches
        _filter_branches(soup.html, lambda node: node.name in PRESERVE_TAGS)

        # Split the HTML into chunks that fit the token limit
        chunks = chunk_html(soup.html, provider, model, max_token)

        return chunks


def _filter_branches(
    node: Tag,
    branch_filter: Optional[Callable[[Tag], bool]]
):
    """
    Filter branches of a tree-like structure, removing branches that don't meet the filter.
    This function mutates the input tree structure in-place.
    """
    if not branch_filter:
        return True

    # if it meets the filter, keep it no matter it is leaf node or not
    if branch_filter(node):
        return True

    children = list(node.children)
    # if it is leaf node and doesn't match the filter, remove it
    if len(children) == 0 and not branch_filter(node):
        return False

    should_keep = False
    for child in children:
        if isinstance(child, Tag):
            if _filter_branches(child, branch_filter):
                should_keep = True
            else:
                child.decompose()
        else:  # NavigableString or Comment
            pass

    return should_keep