"""
cv_parser.py
Extracts text from an uploaded PDF and uses Google Gemini (via the new google-genai SDK)
to dynamically determine the candidate's core skills.
"""
import os
import json
from io import BytesIO
from pypdf import PdfReader
from google import genai
from dotenv import load_dotenv

load_dotenv()

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_skills_from_cv(pdf_bytes: bytes) -> list[str]:
    """Uses Gemini to read the CV and extract the top 5 skills."""
    raw_text = extract_text_from_pdf(pdf_bytes)
    
    # Initialize the new genai client 
    # (It automatically detects GEMINI_API_KEY from your environment variables)
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
        # Use the updated client.models.generate_content syntax
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt
        )
        
        # Parse the JSON response returned by the AI
        skills = json.loads(response.text.strip())
        return skills
    except Exception as e:
        print(f"Error extracting skills with Gemini: {e}")
        return []