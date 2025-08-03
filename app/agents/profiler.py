from app.services.gemini_service import get_gemini_response
import json

def create_search_brief(resume_json_string: str) -> dict:
    """Agent 1A: Analyzes the resume and creates a list of targeted search queries."""
    prompt = f"""
    You are a Resume Profiler AI. Analyze the structured resume below and generate a JSON object containing a list of 5-7 highly specific web search queries. These queries should be designed to find the latest job market trends, in-demand skills, and typical job responsibilities relevant to this specific candidate.

    Include queries for:
    1. Overall job descriptions for their likely role.
    2. Specific technical skill trends related to their primary technologies.
    3. Salary expectations or career path information.

    **Structured Resume (JSON):**
    {resume_json_string}
    ---
    **JSON Output with Search Queries:**
    """
    response = get_gemini_response(prompt)
    # Basic cleaning in case the response is wrapped in markdown
    cleaned_response = response.strip().replace("```json", "").replace("```", "")
    return json.loads(cleaned_response)
