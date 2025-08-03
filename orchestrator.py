from app.agents import profiler
from app.agents.perplexica_researcher import run_perplexica_research
from app.agents import chief_analyst

from app.services.gemini_service import get_gemini_response


def _get_candidate_seniority(resume_json_string: str) -> str:
    # (This function remains unchanged)
    prompt = f"""
    Analyze the "work_experience" and "education" sections of the following structured resume.
    Based on the total years of experience, job titles, and graduation dates, classify the candidate's seniority level.
    Return ONLY ONE of the following keywords: Intern, Entry-Level, Mid-Level, Senior.
    **Structured Resume (JSON):**
    {resume_json_string}
    """
    return get_gemini_response(prompt).strip()


def run_analysis_pipeline(resume_json_string: str) -> str:
    """
    Manages the NEW, more robust multi-agent workflow using Perplexica.
    """
    print("Orchestrator: Starting Perplexica-powered multi-agent pipeline...")

    # ... (seniority and profiler steps are unchanged) ...
    seniority = _get_candidate_seniority(resume_json_string)
    print(f"Orchestrator: Determined seniority is '{seniority}'.")

    print("Orchestrator: Dispatching to Profiler Agent...")
    search_brief = profiler.create_search_brief(resume_json_string)
    search_queries = search_brief.get("search_queries", [])

    # --- This is the only change in the orchestrator ---
    # Call the new high-level research function
    print("Orchestrator: Dispatching to enhanced Perplexica Researcher Agent...")
    market_brief = run_perplexica_research(search_queries)
    # ---

    print("--- Perplexica Market Intelligence Brief ---")
    print(market_brief)
    print("------------------------------------------")

    print("Orchestrator: Dispatching to Chief Analyst Agent for final report...")
    final_report = chief_analyst.generate_final_report(
        resume_json_string, market_brief, seniority
    )

    print("Orchestrator: Pipeline complete.")
    return final_report
