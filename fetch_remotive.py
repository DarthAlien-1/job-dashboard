"""
fetch_remotive.py
Pulls remote jobs dynamically from the Remotive API based on a search query.
"""
import requests
import html

URL = "https://remotive.com/api/remote-jobs"

def fetch_jobs(search_query: str):
    # Remotive accepts a 'search' parameter to filter jobs
    params = {"search": search_query, "limit": 25}
    headers = {"User-Agent": "job-dashboard-app"}
    
    response = requests.get(URL, params=params, headers=headers)
    if response.status_code != 200:
        print(f"  [remotive] Error {response.status_code}")
        return []
        
    data = response.json()
    jobs = []
    
    for item in data.get("jobs", []):
        title = html.unescape(item.get("title", ""))
        description = html.unescape(item.get("description", ""))
        company = item.get("company_name", "")
            
        jobs.append({
            "title": title,
            "company": html.unescape(company) if company else company,
            "location": item.get("candidate_required_location", "Remote"),
            "description": description,
            "url": item.get("url"),
            "posted_date": item.get("publication_date"),
            "source": "remotive",
        })
        
    return jobs