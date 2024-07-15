from playwright.sync_api import sync_playwright, Playwright
from dotenv import load_dotenv
import time
from models.openai_client import OpenAIClient
import convert
import argparse

load_dotenv()

def run(url: str, playwright: Playwright):
    
    ts = int(time.time())
    
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(url)
    page.wait_for_load_state('networkidle')
    
    with open(f"./outputhtml/{ts}.html", "w") as htmlfile:
        htmlfile.write(page.content())            

    # Assign unique ctaid to all elements
    convert.dom_assign_ctaid(page)

    # Convert the page to markdown preserving neccessary elements
    markdown = convert.convert_to_markdown(page)

    print(f"\n\n{markdown}\n\n")

    # Generate a response from the OpenAI API
    result = OpenAIClient().prompt_templated('action', {'markdown': markdown, 'task': 'view the tnc'})
    if result is None:
        raise Exception("Error: Invalid response from OpenAI API")

    print(result)

    page.locator(f"[ctaid=\"{result['ctaid']}\"]")

    target = page.locator(f"[ctaid=\"{result['ctaid']}\"]")
    
    print(target.inner_html())
    target.click()

    # Close the browser
    # browser.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()

    with sync_playwright() as playwright:
        run(args.url, playwright)
        
    