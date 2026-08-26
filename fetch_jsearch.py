"""
fetch_jsearch.py
Pulls jobs from Google Jobs using the JSearch API on RapidAPI.
Requires a RAPID_API_KEY in your .env file.
"""
import os
import requests
import html
from dotenv import load_dotenv

load_dotenv()
RAPID_API_KEY = os.getenv("RAPID_API_KEY")

def fetch_jobs(search_query: str):
    if not RAPID_API_KEY:
        print("  [jsearch] Skipped: No RAPID_API_KEY found in .env")
        return []

    url = "https://jsearch.p.rapidapi.com/search"
    
    # We construct a query that specifies we want remote jobs
    querystring = {
        "query": f"{search_query} remote", 
        "page": "1",
        "num_pages": "1"
    }

    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code != 200:
        print(f"  [jsearch] Error {response.status_code}")
        return []

    data = response.json()
    jobs = []

    for item in data.get("data", []):
        title = html.unescape(item.get("job_title", ""))
        description = html.unescape(item.get("job_description", ""))
        company = item.get("employer_name", "")
        
        jobs.append({
            "title": title,
            "company": html.unescape(company) if company else company,
            "location": f"{item.get('job_city', '')}, {item.get('job_country', 'Remote')}".strip(", "),
            "description": description,
            "url": item.get("job_apply_link") or item.get("job_google_link"),
            "posted_date": item.get("job_posted_at_datetime_utc"),
            "source": "google-jobs",
        })

    return jobs