import fitz
import re
import json
from app.services.gemini_service import get_gemini_response


def parse_pdf_to_text(file_bytes: bytes) -> str:
    """
    Extracts raw text content from a PDF file provided as bytes.
    """
    try:
        # Open the PDF from bytes in memory
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")

        raw_text = ""
        # Iterate through each page and extract text
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            raw_text += page.get_text() + "\n"  # Add a separator between pages

        return raw_text
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""

def preprocess_text(text: str) -> str:
    """
    Cleans up the extracted raw text to make it more suitable for an LLM.

    - Replaces multiple newlines with a single one.
    - Removes excessive spaces.
    - Attempts to fix common ligatures or extraction artifacts (optional but good).
    """
    if not text:
        return ""

    # Replace multiple spaces with a single space
    text = re.sub(r" +", " ", text)

    # Replace multiple newlines with a single newline
    text = re.sub(r"\n\s*\n", "\n", text)

    # Optional: Consolidate lines that seem to be part of the same sentence
    # This helps reconstruct broken paragraphs.
    text = re.sub(r"([a-zA-Z,])\n([a-zA-Z])", r"\1 \2", text)

    # Strip leading/trailing whitespace from the whole text
    text = text.strip()

    # An example of fixing a specific artifact. Can be expanded.
    # text = text.replace('• ', '\n- ') # Replace bullet points for better list formatting

    return text


def parse_text_to_json(resume_text: str) -> dict:
    """
    Uses an LLM to parse raw resume text into a structured JSON object.
    """
    prompt = f"""
    You are an expert resume parsing AI. Your task is to extract information from the following resume text and convert it into a structured JSON object.
    
    The JSON object should have the following keys: "personal_info", "summary", "skills", "work_experience", "education", "projects".
    - "work_experience", "education", and "projects" should be lists of objects.
    - If a section is not present in the resume, its value should be an empty list or an empty string.
    - For skills, categorize them if possible (e.g., "languages", "frameworks", "tools").

    **Resume Text:**
    ---
    {resume_text}
    ---

    **JSON Output:**
    """

    response_text = get_gemini_response(prompt)

    try:
        # The LLM might return the JSON wrapped in markdown ```json ... ```, so we clean it.
        cleaned_json_string = re.sub(
            r"^```json\s*|\s*```$", "", response_text, flags=re.MULTILINE
        ).strip()
        return json.loads(cleaned_json_string)
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the LLM's response.")
        # Fallback: return a simple structure with the raw text to avoid crashing
        return {"error": "Failed to parse resume", "raw_text": resume_text}
