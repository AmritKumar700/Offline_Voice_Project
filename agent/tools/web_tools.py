import ollama
import requests
import fitz # PyMuPDF
from playwright.async_api import async_playwright # Use the ASYNC api
from ddgs import DDGS

def search_web(query: str):
    # This function is fast and doesn't need to be async
    print(f"🔎 Searching with DDGS library for: {query}")
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            output = ""
            for i, result in enumerate(results):
                title = result.get('title', 'No Title')
                link = result.get('href', '#')
                output += f"{i+1}. {title}\n   Link: {link}\n\n"
        if not output: return f"Sorry, no search results found for '{query}'."
        return f"Here are the top search results for '{query}':\n\n{output}"
    except Exception as e:
        return f"Error during library search: {e}"

# Add this new function to agent/tools/web_tools.py

def read_pdf_from_url(url: str) -> str:
    """
    Downloads a PDF from a URL and extracts its text content.
    :param url: The URL of the PDF file.
    """
    print(f"📄 Reading PDF from URL: {url}")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        # Open the PDF from the in-memory content
        with fitz.open(stream=response.content, filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()

        return f"Content from PDF at {url}:\n\n{text[:4000]}"
    except Exception as e:
        return f"Error reading PDF from URL {url}: {e}"    

# In agent/tools/web_tools.py

async def scrape_website(url: str):
    """
    Scrapes the main text content from a URL using a list of common selectors.
    """
    print(f" Scraping website with Playwright: {url}")

    # A list of common selectors for main content, in order of preference
    selectors = [
        'article',
        'main',
        'div[role="main"]',
        'div[class*="content"]',
        'div#content',
        'div#main',
    ]

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=30000, wait_until='domcontentloaded')

            text_content = ""
            # Try each selector until we find one that works
            for selector in selectors:
                print(f"... trying selector '{selector}'")
                # Check if the element exists and is visible
                if await page.locator(selector).first.is_visible():
                    print(f"Success! Found content with selector '{selector}'.")
                    text_content = await page.locator(selector).first.inner_text()
                    break # Stop searching once we find content

            # If no specific content is found, fall back to the whole body
            if not text_content:
                print("Could not find specific content, falling back to body.")
                text_content = await page.locator('body').inner_text()

            await browser.close()

        return f"Scraped content from {url}:\n\n{text_content[:4000]}" # Increased character limit
    except Exception as e:
        return f"Error scraping website: {e}"
def summarize_text(text: str):
    # This function is CPU-bound and can remain sync
    print(f"📝 Summarizing text...")
    try:
        response = ollama.chat( model="llama3", messages=[ {'role': 'system', 'content': 'You are an expert summarizer...'}, {'role': 'user', 'content': text} ])
        return f"Summary:\n\n{response['message']['content']}"
    except Exception as e:
        return f"Error summarizing text: {e}"