import json
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from app.services.generator_service import (
    generate_cover_letter,
    generate_resume_summary,
)
from app.core.rag_pipeline import analyze_resume, analyze_resume_for_job
from app.core.knowledge_base import initialize_knowledge_base
from contextlib import asynccontextmanager
from app.core.resume_parser import (
    parse_pdf_to_text,
    preprocess_text,
    parse_text_to_json,
)

app = FastAPI(
    title="AI Resume Insight Assistant",
    description="An API using RAG with Gemini to analyze resumes from PDF files.",
)


@asynccontextmanager
async def lifespan():
    initialize_knowledge_base()
    yield


def on_startup():
    """Initializes the knowledge base when the application starts."""
    initialize_knowledge_base()


@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "API is running"}


# Updated endpoint to handle file uploads
@app.post("/analyze-resume/", tags=["Resume Analysis"])
async def process_resume_pdf(file: UploadFile = File(...)):
    """
    Receives a resume in PDF format, parses it into a structured JSON,
    and then analyzes it using the RAG pipeline.
    """
    # Validate the file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload a PDF."
        )

    try:
        # Step 1 & 2: Parse PDF and Preprocess text (same as before)
        pdf_bytes = await file.read()
        raw_text = parse_pdf_to_text(pdf_bytes)
        processed_text = preprocess_text(raw_text)

        # Step 3: NEW - Parse text to structured JSON
        structured_resume = parse_text_to_json(processed_text)

        # Step 4: Analyze using the structured data
        # We convert the dict to a formatted string to pass to the pipeline
        insights = analyze_resume(json.dumps(structured_resume, indent=2))

        return {
            "insights": insights,
            "structured_resume": structured_resume,  # Also return the structured data for frontend use
        }

    except HTTPException as he:
        # Re-raise HTTPException to ensure FastAPI handles it
        raise he
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred during analysis: {e}"
        )


@app.post("/analyze-resume-against-job/", tags=["Resume Analysis"])
async def process_resume_and_job(
    file: UploadFile = File(...), job_description: str = Form(...)
):
    """
    Receives a resume PDF and a job description text.
    Performs a detailed gap analysis between the two.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload a PDF."
        )

    try:
        # Resume parsing logic (same as before)
        pdf_bytes = await file.read()
        raw_text = parse_pdf_to_text(pdf_bytes)
        processed_text = preprocess_text(raw_text)
        structured_resume = parse_text_to_json(processed_text)

        if not processed_text:
            raise HTTPException(
                status_code=500, detail="Could not extract text from the PDF."
            )

        insights = analyze_resume_for_job(
            json.dumps(structured_resume, indent=2), job_description
        )

        return {"analysis": insights, "structured_resume": structured_resume}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred during analysis: {e}"
        )


@app.post("/generate-cover-letter/", tags=["Document Generation"])
async def create_cover_letter(
    resume_text: str = Form(...),
    job_description: str = Form(...),
    company: str = Form(...),
    job_title: str = Form(...),
):
    """Generates a tailored cover letter from resume text and a job description."""
    try:
        cover_letter = generate_cover_letter(
            resume_text, job_description, company, job_title
        )
        return {"cover_letter": cover_letter}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate cover letter: {e}"
        )


@app.post("/generate-resume-summary/", tags=["Document Generation"])
async def create_resume_summary(
    resume_text: str = Form(...), job_description: str = Form(...)
):
    """Generates an ATS-optimized professional summary for a resume."""
    try:
        summary = generate_resume_summary(resume_text, job_description)
        return {"resume_summary": summary}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate resume summary: {e}"
        )
