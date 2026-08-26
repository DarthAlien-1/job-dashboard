"""
cv_parser.py
Extracts text from an uploaded CV (PDF, Word, or plain text) and uses Google Gemini
(via the google-genai SDK) to dynamically determine the candidate's core skills.
"""
import os
import json
from io import BytesIO
from pypdf import PdfReader
from docx import Document
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# On Streamlit Cloud there's no .env file — secrets are set in the app's
# "Secrets" settings and exposed via st.secrets. This makes the same code
# work both locally and when deployed, same pattern as fetch_adzuna.py.
if not GEMINI_API_KEY:
    try:
        import streamlit as st
        GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
        if GEMINI_API_KEY:
            os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY  # genai.Client() reads this
    except Exception:
        pass


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)


def extract_text_from_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Routes to the right extractor based on the file's extension."""
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if ext == "pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext == "docx":
        return extract_text_from_docx(file_bytes)
    elif ext in ("txt", "text"):
        return extract_text_from_txt(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: .{ext}. Please upload a PDF, DOCX, or TXT file.")


def extract_skills_from_cv(file_bytes: bytes, filename: str = "resume.pdf") -> list[str]:
    """Uses Gemini to read the CV and extract the top skills."""
    raw_text = extract_text(file_bytes, filename)

    if not raw_text.strip():
        return []

    if not (os.getenv("GEMINI_API_KEY")):
        print("Missing GEMINI_API_KEY — cannot extract skills.")
        return []

    client = genai.Client()

    prompt = f"""
    You are an expert recruiter. I will provide the raw text of a resume.
    Analyze it and extract the top 3 to 5 most important professional skills, technologies, or competencies.

    CRITICAL INSTRUCTION: Your entire response MUST be a valid JSON array of strings, and nothing else.
    Do not include markdown blocks, backticks, or conversational text.

    Example output: ["Human Resources", "Employee Relations", "Onboarding"]

    Resume Text:
    {raw_text}
    """

    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt
        )
        skills = json.loads(response.text.strip())
        return skills
    except Exception as e:
        print(f"Error extracting skills with Gemini: {e}")
        return []
