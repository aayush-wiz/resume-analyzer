import os
import requests
from googleapiclient.discovery import build
from bs4 import BeautifulSoup


def _get_page_content(url: str) -> str:
    """Fetches and cleans the text content of a single webpage."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Extract text and clean it up
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text(separator=" ", strip=True)
            return " ".join(text.split()[:500])  # Return first 500 words
        return ""
    except Exception as e:
        return f"Error fetching page: {e}"


def search_the_web(search_queries: list[str]) -> list[dict]:
    """Agent 1B: Executes web searches and scrapes the top results."""
    api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("PROGRAMMABLE_SEARCH_ENGINE_ID")

    service = build("customsearch", "v1", developerKey=api_key)

    web_results = []
    for query in search_queries:
        print(f"Researcher Agent: Searching for '{query}'...")
        response = (
            service.cse().list(q=query, cx=search_engine_id, num=3).execute()
        )  # Get top 3 results

        for item in response.get("items", []):
            url = item["link"]
            content = _get_page_content(url)
            web_results.append(
                {
                    "query": query,
                    "url": url,
                    "title": item["title"],
                    "content_snippet": content,
                }
            )
    return web_results
