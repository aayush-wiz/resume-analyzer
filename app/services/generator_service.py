from app.services.gemini_service import get_gemini_response


def generate_cover_letter(
    resume_text: str, job_description: str, company: str, job_title: str
) -> str:
    """Generates a tailored cover letter."""
    prompt = f"""
    You are a professional career coach and expert resume writer.
    Your task is to write a compelling and professional cover letter based on the provided resume and job description.

    **Candidate's Resume Text:**
    {resume_text}
    ---
    **Job Description for the role of {job_title} at {company}:**
    {job_description}
    ---
    **INSTRUCTIONS:**
    1.  Write a 3-4 paragraph cover letter.
    2.  In the first paragraph, state the position being applied for ({job_title}) and where it was seen. Express enthusiasm.
    3.  In the body paragraphs, highlight 2-3 key skills and experiences from the resume that DIRECTLY align with the most important requirements in the job description. Do not just list skills; explain how they make the candidate a great fit.
    4.  In the final paragraph, reiterate interest and include a call to action (e.g., "I am eager to discuss how my skills in [Key Skill 1] and [Key Skill 2] can benefit your team.").
    5.  Maintain a professional and confident tone.
    """
    return get_gemini_response(prompt)


def generate_resume_summary(resume_text: str, job_description: str) -> str:
    """Generates a tailored professional summary for a resume."""
    prompt = f"""
    You are an expert resume writer specializing in ATS optimization.
    Your task is to write a powerful, 3-4 sentence "Professional Summary" for a resume, tailored specifically to the provided job description.

    **Candidate's Resume Text:**
    {resume_text}
    ---
    **Target Job Description:**
    {job_description}
    ---
    **INSTRUCTIONS:**
    1.  Distill the candidate's most relevant experiences from their resume.
    2.  Integrate the most important keywords and skills from the job description (e.g., "cloud computing," "agile methodologies," "data-driven decisions").
    3.  Frame the candidate's experience in a way that directly addresses the needs outlined in the job description.
    4.  The output should be a single paragraph.
    """
    return get_gemini_response(prompt)
