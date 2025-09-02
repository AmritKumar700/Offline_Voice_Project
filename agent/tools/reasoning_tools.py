# in agent/tools/reasoning_tools.py
import ollama
from . import web_tools # Import other tools to use them internally
import asyncio

# in agent/tools/reasoning_tools.py

async def answer_question_from_web(query: str):
    """
    A comprehensive tool that searches the web, reads multiple sources (HTML and PDF),
    and synthesizes them into a single answer.
    """
    print(f"🧠 Starting research process for query: '{query}'")

    # Step 1: Search the web
    search_results_str = web_tools.search_web(query)
    print(f"Initial search results:\n{search_results_str}")

    # Step 2: Extract URLs and decide which tool to use for each
    urls = []
    lines = search_results_str.split('\n')
    for line in lines:
        if "Link: " in line:
            urls.append(line.split("Link: ")[1].strip())

    tasks = []
    for url in urls[:3]: # Process the top 3 results
        if url.lower().endswith('.pdf'):
            # If it's a PDF, use the PDF reader (which is synchronous)
            tasks.append(asyncio.to_thread(web_tools.read_pdf_from_url, url))
        else:
            # Otherwise, use the async web scraper
            tasks.append(web_tools.scrape_website(url))

    # Run all reading/scraping tasks in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Step 3: Consolidate content for the final summary
    scraped_content = []
    for i, res in enumerate(results):
        if isinstance(res, Exception):
            scraped_content.append(f"## Source {i+1} (URL: {urls[i]}):\nCould not be read. Error: {res}\n\n")
        else:
            scraped_content.append(f"## Source {i+1} (URL: {urls[i]}):\n{res}\n\n")

    # Step 4: Synthesize the final answer
    print("Synthesizing final answer from all sources...")
    synthesis_prompt = f"""
    You are a research assistant. Your task is to answer the user's question based ONLY on the provided sources.
    Analyze all the sources, cross-reference them, and provide a single, comprehensive, and accurate answer.
    Ignore sources that are irrelevant to the user's question.
    Do not use any prior knowledge. If the sources do not contain the answer, state that clearly.

    ## User's Original Question:
    "{query}"

    ## Collected Sources:
    {''.join(scraped_content)}

    ## Your Final Answer:
    """

    try:
        response = ollama.chat(
            model="llama3",
            messages=[{'role': 'user', 'content': synthesis_prompt}],
        )
        final_answer = response['message']['content']
        print(f"✅ Final answer generated.")
        return final_answer
    except Exception as e:
        return f"Error during final synthesis: {e}"