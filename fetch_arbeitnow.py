"""
fetch_arbeitnow.py
Pulls jobs from the Arbeitnow Free Job Board API.
"""
import requests
import html
from filters import is_entry_level

URL = "https://arbeitnow.com/api/job-board-api"

def fetch_jobs():
    headers = {"User-Agent": "job-dashboard-app"}
    response = requests.get(URL, headers=headers)
    
    if response.status_code != 200:
        print(f"  [arbeitnow] Error {response.status_code}")
        return []
        
    data = response.json()
    jobs = []
    
    for item in data.get("data", []):
        title = html.unescape(item.get("title", ""))
        description = html.unescape(item.get("description", ""))
        company = item.get("company_name", "")
        
        if not is_entry_level(title, description):
            continue
            
        jobs.append({
            "title": title,
            "company": html.unescape(company) if company else company,
            "location": item.get("location", "Remote"),
            "description": description,
            "url": item.get("url"),
            "posted_date": item.get("created_at"),
            "source": "arbeitnow",
        })
        
    return jobs

if __name__ == "__main__":
    results = fetch_jobs()
    print(f"Found {len(results)} jobs:\n")
    for job in results:
        print(f"- {job['title']} at {job['company']}")