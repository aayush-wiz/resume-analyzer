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
)

app = FastAPI(
    title="AI Resume Insight Assistant",
    description="An API using RAG with Gemini to analyze resumes from PDF files.",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize knowledge base on startup
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
    Receives a resume in PDF format, parses and preprocesses it,
    then analyzes it using the RAG pipeline.
    """
    # 1. Validate the file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload a PDF."
        )

    try:
        # 2. Read the file content as bytes
        pdf_bytes = await file.read()
        if not pdf_bytes:
            raise HTTPException(status_code=400, detail="PDF file is empty.")

        # 3. Parse and Preprocess the text
        raw_text = parse_pdf_to_text(pdf_bytes)
        processed_text = preprocess_text(raw_text)

        if not processed_text:
            raise HTTPException(
                status_code=500, detail="Could not extract text from the PDF."
            )

        # 4. Analyze the cleaned text with the existing RAG pipeline
        insights = analyze_resume(processed_text)

        print(insights)
        # We can also return the extracted text for debugging purposes if needed
        return {
            "insights": insights,
            # "extracted_text": processed_text
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

        if not processed_text:
            raise HTTPException(
                status_code=500, detail="Could not extract text from the PDF."
            )

        # Call the NEW analysis function
        insights = analyze_resume_for_job(processed_text, job_description)

        print(insights)
        return {"analysis": insights}

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
