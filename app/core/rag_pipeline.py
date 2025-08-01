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


def build_detailed_prompt(resume_text: str, context_documents: list[str]) -> str:
    """
    Builds the comprehensive and structured prompt for the LLM based on the new detailed requirements.
    """
    context = "\n---\n".join(context_documents)

    prompt = f"""
    You are a world-class AI Resume Insight Assistant. Your task is to conduct a detailed analysis of a candidate's resume and provide actionable, structured feedback.
    You MUST use the "Market & ATS Context" provided below to inform your analysis about skill gaps, career paths, and optimization. Do not refer to the context directly in your response.

    **Market & ATS Context:**
    {context}

    ---

    **Candidate's Resume Text:**
    {resume_text}

    ---

    **INSTRUCTIONS:**
    Based on the resume and the context, generate a professional, personalized, and actionable report. Structure your output in Markdown using EXACTLY the following sections:

    **Identified Field:**
    (e.g., Data Science, Software Engineering, Product Management)

    **Key Skills:**
    (Summarize their top technical skills like languages, frameworks, and tools. Also mention notable soft skills like leadership or communication if evident.)

    **Skill Gaps / Missing Keywords:**
    (Identify crucial skills and keywords for their field that are missing from the resume. Compare against the market context.)

    **ATS Optimization Tips:**
    (Provide specific advice to improve the resume's compatibility with Applicant Tracking Systems. Suggest adding standard headers, quantifiable achievements, and keywords.)

    **Suitable Job Roles:**
    (Suggest 2-3 specific job titles the candidate is qualified for RIGHT NOW. Explain your reasoning for each.)

    **Upskilling Recommendations:**
    (List concrete skills, tools, certifications, or types of projects the candidate should pursue to advance. Prioritize based on industry demand.)

    **Career Growth Roadmap:**
    - **Short-Term (0-2 years):** Describe the immediate roles they should target and the key skills to solidify.
    - **Long-Term (3-5+ years):** Outline potential advanced roles they can aspire to (e.g., Senior Developer, Analytics Manager, Architect) and the strategic skills required to get there.

    **Final Insight Summary:**
    (A concise, concluding paragraph summarizing the candidate's current standing and primary path to career growth.)
    """
    return prompt


def analyze_resume(resume_text: str) -> str:
    """
    The main RAG pipeline function, now enhanced with a pre-analysis step for more targeted retrieval.
    """
    # 1. Pre-analysis: Get a focused query for retrieval.
    # This step turns the entire resume into a smart query like "Field: Data Science. Skills: Python, SQL, Tableau".
    pre_analysis_summary = _pre_analyze_resume(resume_text)

    # 2. Retrieve: Use the focused summary to query the knowledge base.
    # This fetches more relevant documents about data science career paths, skills, and ATS tips.
    # We increase n_results to get a richer context for our detailed prompt.
    retrieved_context = query_knowledge_base(pre_analysis_summary, n_results=5)

    # 3. Augment: Build the new, highly detailed prompt using the original resume and the retrieved context.
    prompt = build_detailed_prompt(resume_text, retrieved_context)

    # 4. Generate: Get the final, structured analysis from Gemini.
    final_analysis = get_gemini_response(prompt)

    return final_analysis


# Add the new functions below them.


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
    resume_text: str, job_description: str, context_documents: list[str]
) -> str:
    """Builds the comprehensive prompt for a detailed resume-to-job-description analysis."""
    context = "\n---\n".join(context_documents)

    prompt = f"""
    You are an expert AI Talent Acquisition Specialist. Your task is to perform a detailed gap analysis between a candidate's resume and a specific job description.
    You MUST use the "Market Context" to inform your analysis.

    **Market Context:**
    {context}
    ---

    **Candidate's Resume Text:**
    {resume_text}
    ---

    **Job Description:**
    {job_description}
    ---

    **INSTRUCTIONS:**
    Provide a detailed, structured analysis in Markdown. Use EXACTLY the following format:

    **Overall Match Score:** (Provide a score out of 10 and a brief one-sentence justification. E.g., "7/10: The candidate is a strong fit for the frontend aspects of this role but lacks the required database experience.")

    **Key Strengths & Matches:**
    (List 3-5 specific points where the candidate's skills/experience directly match the job requirements. Be specific.)
    - Example: The candidate's proficiency in React.js aligns perfectly with the job's requirement for a frontend developer with experience in modern JavaScript frameworks.

    **Critical Gaps & Mismatches:**
    (List 3-5 of the most important skills or qualifications from the job description that are MISSING from the resume.)
    - Example: The job requires 3+ years of experience with SQL databases, which is not mentioned in the candidate's resume.

    **Resume Tailoring Suggestions:**
    (Provide concrete advice on how to edit the resume to better align with this specific job.)
    - Example: "Update the professional summary to explicitly mention your passion for 'data-driven user experiences' to match the language in the job description."
    - Example: "In the project description for 'Project X', rephrase the bullet points to highlight how you used 'state management with Context API', as 'state management' is a key requirement."

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
