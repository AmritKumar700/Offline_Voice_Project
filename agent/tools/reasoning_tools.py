import json
import ollama
import asyncio
import re # Import the regular expressions library
from . import web_tools

# This is the structured prompt for the final synthesis step.
SYNTHESIS_PROMPT = """
You are an expert AI assistant that synthesizes information. Based on the provided sources, answer the user's query.

## User Query:
{query}

## Sources:
{sources}

## Instructions:
Respond with a JSON object containing two keys:
1.  `"thought_process"`: A detailed, multi-sentence explanation of how you arrived at the answer, citing the sources.
2.  `"direct_answer"`: A single, concise, and to-the-point sentence that directly answers the user's query.

## Your JSON Response:
"""

async def answer_question_from_web(query: str) -> str:
    """
    The main function for the reasoning tool. It orchestrates the entire research process.
    1. Calls search_web to get links.
    2. Concurrently scrapes all links for their content.
    3. Synthesizes the information using an LLM to get a final answer.
    """
    print(f"Starting research process for query: '{query}'")

    # Step 1: Get search results (links and titles) from web_tools
    search_results = web_tools.search_web(query)
    print(f"Initial search results:\n{search_results}")

    # Step 2: Extract all the URLs from the search results string
    # This uses a regular expression to find all URLs starting with http or https.
    url_pattern = re.compile(r'Link: (https?://[^\s]+)')
    urls_to_scrape = url_pattern.findall(search_results)
    
    if not urls_to_scrape:
        return "Sorry, I couldn't find any valid website links to research."

    # Step 3: Concurrently scrape all found URLs
    # asyncio.gather runs all the scraping tasks at the same time for speed.
    scraping_tasks = [web_tools.scrape_website(url) for url in urls_to_scrape]
    scraped_contents = await asyncio.gather(*scraping_tasks)
    
    # Combine all the scraped text into a single block of sources
    sources_content = "\n\n---\n\n".join(scraped_contents)

    # Step 4: Synthesize the final answer using the LLM
    print("Synthesizing final answer from all sources...")
    try:
        prompt = SYNTHESIS_PROMPT.format(query=query, sources=sources_content)

        response = ollama.chat(
            model="llama3",
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.0}
        )
        response_text = response['message']['content']

        start_index = response_text.find('{')
        end_index = response_text.rfind('}')
        json_str = response_text[start_index:end_index+1]
        response_json = json.loads(json_str)

        print(f"\n--- LLM Thought Process ---\n{response_json.get('thought_process')}\n---------------------------\n")
        print("✅ Final answer generated.")

        return response_json.get("direct_answer", "Sorry, I had trouble forming a direct answer.")

    except Exception as e:
        print(f"Error synthesizing answer: {e}")
        return "I found the information but had trouble summarizing it."