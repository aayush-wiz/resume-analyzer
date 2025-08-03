import json
from app.services.gemini_service import get_gemini_response


def create_market_intelligence_brief(web_results: list[dict]) -> str:
    """Agent 2: Takes raw web search results and synthesizes them into a clean brief."""
    web_results_string = json.dumps(web_results, indent=2)

    prompt = f"""
    You are a Data Synthesizer AI. Your job is to read the following raw web search results and synthesize them into a concise and structured "Market Intelligence Brief" in Markdown format.
    
    Filter out ads, boilerplate, and irrelevant information. Focus on extracting:
    - Key responsibilities for the target job role.
    - In-demand technical and soft skills.
    - Popular tools and technologies.
    - Typical career progression advice or salary benchmarks if available.

    **Raw Web Results (JSON):**
    {web_results_string}
    ---
    **Concise Market Intelligence Brief (Markdown):**
    """
    return get_gemini_response(prompt)
