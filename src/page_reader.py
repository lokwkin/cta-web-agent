from collections import defaultdict
from bs4 import Tag
from playwright.sync_api import sync_playwright, Playwright, Page
from markdownify import markdownify as md, MarkdownConverter
import uuid
import plotly.graph_objects as go
import uuid
from collections import defaultdict
from bs4 import BeautifulSoup, Comment, Tag, NavigableString


def dom_assign_element_id(page: Page):
    def generate_unique_id():
        return f"{uuid.uuid4().hex[:8]}"   
    
    for cta in page.locator('link').all():
        cta.evaluate(f"el => el.setAttribute('element_id', '{generate_unique_id()}')")

    for cta in page.locator('a').all():
        cta.evaluate(f"el => el.setAttribute('element_id', '{generate_unique_id()}')")

    for cta in page.locator('button').all():
        cta.evaluate(f"el => el.setAttribute('element_id', '{generate_unique_id()}')")

def convert_to_markdown(page: Page):

    class CTAMarkdownConverter(MarkdownConverter):
        def convert_button(self, el: Tag, text, convert_as_inline):
            desc = f"{el.text.strip() if len(el.text.strip()) > 0 else ','.join([img.attrs['alt'] for img in el.find_all('img')])}"
            return f"[{desc}](Button)<{el.attrs['element_id']}>\n\n"
        
        def convert_img(self, el, text, convert_as_inline):
            return ''
        
        def convert_a(self, el: Tag, text, convert_as_inline):
            return super().convert_a(el, text, convert_as_inline) + f"<{el.attrs['element_id']}>\n\n"
        
    markdown = CTAMarkdownConverter().convert(page.content())

    return markdown.strip()






def plot_dom_tree(node: Tag):
    def traverse(element: Tag, parent_id):
        node_id = f"{element.name}_{id(element)}"
        tree_data['ids'].append(node_id)
        tree_data['labels'].append(f"{element.name}")
        tree_data['parents'].append(parent_id)
        
        if element.name == 'a':
            hover_text = f"Link: {element.get('href', 'N/A')}"
        elif element.name == 'button':
            hover_text = f"Text: {element.attrs['dt-text'] if 'dt-text' in element.attrs else ''}"
        else:
            hover_text = element.name
        tree_data['hover_text'].append(hover_text)
        
        for child in element.children:
            if child.name:
                traverse(child, node_id)
    
    tree_data = defaultdict(list)
    traverse(node, '')
    
    return tree_data

def visualize_dom_tree(tree_data):
    fig = go.Figure(go.Treemap(
        ids=tree_data['ids'],
        labels=tree_data['labels'],
        parents=tree_data['parents'],
        root_color="lightgrey",
        hovertext=tree_data['hover_text'],
        hoverinfo="text"
    ))
    
    fig.update_layout(
        title="DOM Tree Visualization",
        width=1600,
        height=800
    )
    
    fig.show()
    
def filter_branches(node: Tag):
    
    def preserve_info(node: Tag):
        if node.name == 'button':
            if len(node.text.strip()) > 0:
                node.attrs['dt-text'] = node.text.strip()
        
    def should_keep(node: Tag):
        if isinstance(node, (NavigableString, Comment)):
            return False
        if node.name == 'a':
            return True if node.get('href') else False
        if node.name == 'button':
            return True if len(node.text.strip()) > 0 else False
        return any(should_keep(child) for child in node.children)
        
    def clean_branches(element):    
        if not isinstance(element, Tag):
            return

        children = list(element.children)
        for child in children:
            if isinstance(child, (NavigableString, Comment)):
                # Remove comments
                child.extract()
            elif should_keep(child):
                preserve_info(child)
                clean_branches(child)
            else:
                child.decompose()
                
    clean_branches(node)
    return node

def process_html(html) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    
    tree = soup.html
    
    def generate_unique_id():
        return f"{uuid.uuid4().hex[:8]}"   

    for tag in soup.html.find_all():
        if isinstance(tag, Tag) and tag.name in ['a', 'button']:
            if 'element_id' not in tag.attrs:
                tag['element_id'] = generate_unique_id()
            
    # tree = filter_branches(tree)
    # tree_data = plot_dom_tree(tree)
    # visualize_dom_tree(tree_data)
    # return str(tree)
    return soup

