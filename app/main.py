import json
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from app.core.resume_parser import (
    parse_pdf_to_text,
    preprocess_text,
    parse_text_to_json,
)
from orchestrator import run_analysis_pipeline
from app.services.generator_service import (
    generate_cover_letter,
    generate_resume_summary,
)

app = FastAPI(
    title="Multi-Agent AI Resume Insight Assistant",
    description="An advanced API using a team of AI agents for real-time resume analysis.",
)


@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "API is running"}


@app.post("/generate-cover-letter/", tags=["Document Generation"])
async def create_cover_letter(
    resume_text: str = Form(...),
    job_description: str = Form(...),
    company: str = Form(...),
    job_title: str = Form(...),
):
    """Generates a tailored cover letter from raw resume text and a job description."""
    try:
        cover_letter = generate_cover_letter(
            resume_text, job_description, company, job_title
        )
        return {"cover_letter": cover_letter}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate cover letter: {str(e)}"
        )


@app.post("/generate-resume-summary/", tags=["Document Generation"])
async def create_resume_summary(
    resume_text: str = Form(...), job_description: str = Form(...)
):
    """Generates an ATS-optimized professional summary from raw resume text."""
    try:
        summary = generate_resume_summary(resume_text, job_description)
        return {"resume_summary": summary}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate resume summary: {str(e)}"
        )


@app.post("/analyze-resume-with-live-data/", tags=["Multi-Agent Analysis"])
async def process_resume_with_multi_agent_system(file: UploadFile = File(...)):
    """
    Receives a resume PDF, processes it using a multi-agent system
    with live web-search capabilities, and returns a comprehensive,
    up-to-the-minute analysis.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload a PDF."
        )

    try:
        # Step 1: Standard PDF parsing and text preprocessing
        pdf_bytes = await file.read()
        raw_text = parse_pdf_to_text(pdf_bytes)
        processed_text = preprocess_text(raw_text)

        if not processed_text:
            raise HTTPException(
                status_code=500, detail="Could not extract text from the PDF."
            )

        # Step 2: Use the AI parser to get structured JSON data from the text
        structured_resume = parse_text_to_json(processed_text)
        if "error" in structured_resume:
            raise HTTPException(
                status_code=500,
                detail="Failed to parse resume text into a structured format.",
            )

        # Step 3: HAND OFF TO THE ORCHESTRATOR
        # This single function call kicks off the entire multi-agent workflow.
        # We pass the structured resume as a formatted JSON string.
        final_report = run_analysis_pipeline(json.dumps(structured_resume, indent=2))

        # Return both the final report and the structured data that was extracted
        return {
            "final_analysis_report": final_report,
            "structured_resume_data": structured_resume,
        }

    except HTTPException as he:
        # Re-raise known exceptions to ensure FastAPI handles them correctly
        raise he
    except Exception as e:
        # Catch any other unexpected errors during the complex pipeline
        print(f"An unexpected error occurred in the multi-agent pipeline: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during analysis: {str(e)}",
        )
