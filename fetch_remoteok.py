"""
fetch_remoteok.py
Pulls remote job postings from the RemoteOK public API (no key needed).
"""

import requests
from filters import is_entry_level

URL = "https://remoteok.com/api"


def fetch_jobs():
    headers = {"User-Agent": "Mozilla/5.0 (job-dashboard personal project)"}
    response = requests.get(URL, headers=headers)

    if response.status_code != 200:
        print(f"  [remoteok] Error {response.status_code}")
        return []

    data = response.json()
    jobs = []

    # The first item in RemoteOK's response is a legal notice, not a job - skip it
    for item in data[1:]:
        title = item.get("position", "")
        description = item.get("description", "") or ""
        tags = " ".join(item.get("tags", []))

        if not is_entry_level(title, description + " " + tags):
            continue

        jobs.append({
            "title": title,
            "company": item.get("company"),
            "location": "Remote",
            "description": description,
            "url": item.get("url"),
            "posted_date": item.get("date"),
            "source": "remoteok",
        })

    return jobs


if __name__ == "__main__":
    results = fetch_jobs()
    print(f"Found {len(results)} jobs:\n")
    for job in results:
        print(f"- {job['title']} at {job['company']}")
