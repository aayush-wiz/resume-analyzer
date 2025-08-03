import os
import time
import requests
import concurrent.futures
from threading import Lock
from dotenv import load_dotenv

# Load environment variables from the project's .env file
load_dotenv()

# --- Configuration from Environment ---
PERPLEXICA_API_URL = "http://localhost:3000/api/search"
PROVIDER = os.getenv("PERPLEXICA_PROVIDER", "openai")
CHAT_MODEL = os.getenv("PERPLEXICA_CHAT_MODEL", "gpt-4o")
EMBEDDING_MODEL = os.getenv("PERPLEXICA_EMBEDDING_MODEL", "text-embedding-3-small")

# --- Performance & Resilience Settings ---
MAX_CONCURRENT_QUERIES = 5
REQUEST_TIMEOUT_SECONDS = 90
MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 10


class PerplexicaResearcherAgent:
    """
    Final robust version of the agent.
    Sends the complete, detailed payload required by the Perplexica API.
    """

    def __init__(self):
        self.lock = Lock()
        self.results = {}
        # Pre-flight check
        if not all([PROVIDER, CHAT_MODEL, EMBEDDING_MODEL]):
            raise ValueError(
                "Missing Perplexica model configuration in .env file (e.g., PERPLEXICA_PROVIDER)."
            )

    def _search_single_query_with_retries(self, query: str, query_index: int):
        print(f"  -> Submitting Query {query_index}: '{query[:60]}...'")

        # --- THIS IS THE DEFINITIVE PAYLOAD STRUCTURE ---
        payload = {
            "query": query,
            "focusMode": "all",
            "chatModel": {"provider": PROVIDER, "name": CHAT_MODEL},
            "embeddingModel": {
                "provider": PROVIDER,  # Often the same provider for both
                "name": EMBEDDING_MODEL,
            },
            "systemInstructions": "You are an expert market research analyst. Provide concise, factual information based on the web search results. Focus on skills, job responsibilities, and industry trends.",
            "stream": False,
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Resume-Insight-Assistant/3.0",
        }

        for attempt in range(MAX_RETRIES):
            try:
                response = requests.post(
                    PERPLEXICA_API_URL,
                    json=payload,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )
                response.raise_for_status()
                data = response.json()
                answer = data.get("response", "No answer found.")
                with self.lock:
                    self.results[query_index] = (
                        f"## Query: {query}\n\n{answer}\n\n---\n\n"
                    )
                    print(f"  <- ✅ SUCCESS for Query {query_index}")
                return
            except requests.exceptions.RequestException as e:
                print(
                    f"  <- ⚠️ FAILED Query {query_index} (Attempt {attempt + 1}/{MAX_RETRIES}): {e}"
                )
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY_SECONDS)
                else:
                    with self.lock:
                        self.results[query_index] = (
                            f"## Query: {query}\n\nError: Could not retrieve information. Check Perplexica server logs.\n\n---\n\n"
                        )

    def fetch_market_intelligence(self, search_queries: list[str]) -> str:
        print(
            "\nPerplexica Researcher Agent: Starting information gathering (Definitive Payload)..."
        )
        self.results = {}
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=MAX_CONCURRENT_QUERIES
        ) as executor:
            futures = [
                executor.submit(self._search_single_query_with_retries, query, i)
                for i, query in enumerate(search_queries)
            ]
            concurrent.futures.wait(futures)
        print("Perplexica Researcher Agent: All queries processed.\n")
        market_brief = "".join(
            self.results.get(i, "") for i in range(len(search_queries))
        )
        return market_brief


def run_perplexica_research(search_queries: list[str]) -> str:
    try:
        agent = PerplexicaResearcherAgent()
        return agent.fetch_market_intelligence(search_queries)
    except ValueError as e:
        print(f"Error: {e}")
        return f"## Error: {e}"
