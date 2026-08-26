"""
api.py
FastAPI backend that serves job postings as JSON and handles dynamic CV matching.
Run with: python -m uvicorn api:app --reload --port 8000
"""

from fastapi import FastAPI, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel
from db import get_all_postings

# New dynamic imports
from cv_parser import extract_skills_from_cv
import fetch_adzuna
import fetch_jobicy
import fetch_remotive
import fetch_jsearch
from match import score_all_jobs

app = FastAPI(title="Job Match API")

# Allow the Next.js frontend (running on localhost:3000) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Posting(BaseModel):
    id: int
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    posted_date: Optional[str] = None
    source: Optional[str] = None
    match_score: float
    matched_skills: Optional[str] = None

@app.get("/api/jobs", response_model=List[Posting])
def list_jobs(
    min_score: float = Query(0.0, ge=0, le=1),
    source: Optional[str] = None,
    search: Optional[str] = None,
):
    # This route still serves your default portfolio jobs from the DB
    postings = get_all_postings()

    if min_score:
        postings = [p for p in postings if p["match_score"] >= min_score]

    if source:
        postings = [p for p in postings if p["source"] == source]

    if search:
        s = search.lower()
        postings = [
            p for p in postings
            if s in (p["title"] or "").lower() or s in (p["company"] or "").lower()
        ]

    return postings

@app.get("/api/stats")
def get_stats():
    postings = get_all_postings()
    sources = sorted(set(p["source"] for p in postings if p["source"]))
    avg_score = round(sum(p["match_score"] for p in postings) / len(postings), 3) if postings else 0

    return {
        "total_jobs": len(postings),
        "average_match_score": avg_score,
        "sources": sources,
    }

@app.post("/api/match-cv")
async def upload_and_match_cv(file: UploadFile = File(...)):
    # 1. Read the uploaded PDF
    contents = await file.read()
    
    # 2. Let Gemini extract the dynamic skills
    extracted_skills = extract_skills_from_cv(contents)
    
    if not extracted_skills:
        return {"extracted_skills": [], "jobs": []}
        
    # 3. Use the primary skill as the live search query
    primary_query = extracted_skills[0] 
    print(f"Live Searching for: {primary_query}")
    
    # 4. Fetch jobs live (this may take 5-10 seconds depending on API response times)
    live_adzuna = fetch_adzuna.fetch_jobs(primary_query)
    live_jobicy = fetch_jobicy.fetch_jobs(primary_query)
    live_remotive = fetch_remotive.fetch_jobs(primary_query)
    live_jsearch = fetch_jsearch.fetch_jobs(primary_query)

    all_live_jobs = live_adzuna + live_jobicy + live_remotive + live_jsearch
    
    # 5. Score the freshly fetched jobs against ALL of the extracted skills
    scored_jobs = score_all_jobs(all_live_jobs, extracted_skills)
    
    # 6. Sort highest matches to the top
    scored_jobs.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    
    # 7. Format the jobs to ensure they match the frontend's expected data structure
    formatted_jobs = []
    for i, job in enumerate(scored_jobs):
        job_copy = dict(job)
        
        # Add a temporary ID for the React frontend, as live jobs are not in the DB yet
        job_copy["id"] = i + 1 
        
        # Convert the matched skills list into a comma-separated string for the frontend UI
        if isinstance(job_copy.get("matched_skills"), list):
             job_copy["matched_skills"] = ", ".join(job_copy["matched_skills"])
             
        formatted_jobs.append(job_copy)
    
    return {
        "extracted_skills": extracted_skills,
        "jobs": formatted_jobs
    }