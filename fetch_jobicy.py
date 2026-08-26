"""
fetch_jobicy.py
Pulls remote jobs dynamically based on an SEO tag search.
"""
import requests
import html

URL = "https://jobicy.com/api/v2/remote-jobs"

def fetch_jobs(search_query: str):
    # Jobicy uses 'tag' to search across categories (e.g., 'tag=react' or 'tag=marketing')
    params = {"count": 30, "tag": search_query}
    headers = {"User-Agent": "job-dashboard-app"}
    
    response = requests.get(URL, params=params, headers=headers)
    if response.status_code != 200:
        return []
        
    data = response.json()
    jobs = []
    
    for item in data.get("jobs", []):
        title = html.unescape(item.get("jobTitle", ""))
        description = html.unescape(item.get("jobDescription", ""))
        company = item.get("companyName", "")
            
        jobs.append({
            "title": title,
            "company": html.unescape(company) if company else company,
            "location": item.get("jobGeo", "Remote"),
            "description": description,
            "url": item.get("url"),
            "posted_date": item.get("pubDate"),
            "source": "jobicy",
        })
        
    return jobs