from app.core.knowledge_base import query_knowledge_base
from app.services.gemini_service import get_gemini_response


def _pre_analyze_resume(resume_text: str) -> str:
    """
    A quick pre-analysis step to identify the core field and skills of the candidate.
    This focused summary will be used to retrieve more relevant context from the knowledge base.
    """
    prompt = f"""
    Analyze the following resume text and identify the candidate's primary field/domain and list their top 5-7 key skills.
    Your output should be a single, concise string formatted like this: "Field: [Identified Field]. Skills: [Skill1, Skill2, Skill3]".

    Resume Text:
    {resume_text}

    Analysis:
    """
    return get_gemini_response(prompt)


def build_detailed_prompt(resume_json_string: str, context_documents: list[str]) -> str:
    """
    Builds the comprehensive prompt for the LLM using a structured resume.
    """
    context = "\n---\n".join(context_documents)

    prompt = f"""
    You are a world-class AI Resume Insight Assistant. Your task is to conduct a detailed analysis of a candidate's resume, provided as a structured JSON object, and generate actionable feedback.
    You MUST use the "Market & ATS Context" provided below.

    **Market & ATS Context:**
    {context}
    ---
    **Candidate's Structured Resume (JSON):**
    {resume_json_string}
    ---
    **INSTRUCTIONS:**
    Based on the structured resume and the context, generate a professional report in Markdown using EXACTLY the following sections:
    Identified Field, Key Skills, Skill Gaps / Missing Keywords, ATS Optimization Tips, Suitable Job Roles, Upskilling Recommendations, Career Growth Roadmap, Final Insight Summary.
    """
    return prompt


def analyze_resume(resume_json_string: str) -> str:
    # Step 1: Determine Seniority
    seniority = _get_candidate_seniority(resume_json_string)

    # Step 2: Perform Pre-analysis for retrieval (can even include seniority for a better query)
    pre_analysis_summary = (
        _pre_analyze_resume(resume_json_string) + f" Seniority: {seniority}"
    )

    # Step 3: Retrieve context
    retrieved_context = query_knowledge_base(pre_analysis_summary, n_results=5)

    # Step 4: Augment the main prompt WITH the seniority level
    prompt = build_detailed_prompt(resume_json_string, retrieved_context, seniority)

    # Step 5: Generate the final analysis
    final_analysis = get_gemini_response(prompt)
    return final_analysis


def _pre_analyze_for_job_match(resume_text: str, job_description: str) -> str:
    """A quick pre-analysis to extract key terms from both resume and JD for targeted retrieval."""
    prompt = f"""
    Analyze the resume and the job description. Extract the primary field, 5-7 key skills from the resume, 
    and 5-7 key requirements from the job description.
    Format your output as a single, concise string: 
    "Field: [Identified Field]. Resume Skills: [Skill1, Skill2]. Job Requirements: [Req1, Req2]".

    Resume Text:
    {resume_text}

    Job Description:
    {job_description}

    Analysis:
    """
    return get_gemini_response(prompt)


def build_job_match_prompt(
    resume_json_string: str, job_description: str, context_documents: list[str]
) -> str:
    """Builds the comprehensive prompt for a detailed resume-to-job-description analysis from a structured resume."""
    context = "\n---\n".join(context_documents)

    prompt = f"""
    You are an expert AI Talent Acquisition Specialist. Your task is to perform a detailed gap analysis between a candidate's resume (provided as a JSON object) and a specific job description.
    You MUST use the "Market Context" to inform your analysis.

    **Market Context:**
    {context}
    ---
    **Candidate's Structured Resume (JSON):**
    {resume_json_string}
    ---
    **Job Description:**
    {job_description}
    ---
    **INSTRUCTIONS:**
    Provide a detailed, structured analysis in Markdown. Use EXACTLY the following format:
    Overall Match Score, Key Strengths & Matches, Critical Gaps & Mismatches, Resume Tailoring Suggestions.
    """
    return prompt


def analyze_resume_for_job(resume_text: str, job_description: str) -> str:
    """The RAG pipeline for comparing a resume against a job description."""
    # 1. Pre-analysis for targeted query
    pre_analysis_summary = _pre_analyze_for_job_match(resume_text, job_description)

    # 2. Retrieve relevant context
    retrieved_context = query_knowledge_base(pre_analysis_summary, n_results=5)

    # 3. Augment with the detailed job-matching prompt
    prompt = build_job_match_prompt(resume_text, job_description, retrieved_context)

    # 4. Generate the final analysis
    analysis = get_gemini_response(prompt)

    return analysis


def _get_candidate_seniority(resume_json_string: str) -> str:
    """
    Analyzes the resume to determine the candidate's experience level.
    Returns one of: 'Intern', 'Entry-Level', 'Mid-Level', 'Senior'.
    """
    prompt = f"""
    Analyze the "work_experience" and "education" sections of the following structured resume. 
    Based on the total years of experience, job titles, and graduation dates, classify the candidate's seniority level.

    - If there is no work experience and the candidate is still in university, classify as 'Intern'.
    - If there is 0-2 years of experience and a recent graduation date, classify as 'Entry-Level'.
    - If there are 2-7 years of relevant experience, classify as 'Mid-Level'.
    - If there are 7+ years of experience with progressive titles, classify as 'Senior'.

    Return ONLY ONE of the following keywords: Intern, Entry-Level, Mid-Level, Senior.

    **Structured Resume (JSON):**
    {resume_json_string}
    """
    return get_gemini_response(prompt).strip()
