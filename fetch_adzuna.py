"""
fetch_adzuna.py
Pulls job postings from the Adzuna API across several countries,
searching for remote, entry-level roles.
"""

import os
import requests
from dotenv import load_dotenv
from filters import is_entry_level

load_dotenv()
APP_ID = os.getenv("APP_ID")
APP_KEY = os.getenv("APP_KEY")

# --- Settings you can change ---
COUNTRIES = ["us", "gb", "ca", "au", "sg", "in"]
QUERY = "remote entry level developer"
RESULTS_PER_PAGE = 20
# --------------------------------


def fetch_jobs_for_country(country, query=QUERY, page=1):
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": RESULTS_PER_PAGE,
        "what": query,
        "content-type": "application/json",
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"  [{country}] Error {response.status_code}: {response.text[:200]}")
        return []

    data = response.json()
    jobs = []

    for item in data.get("results", []):
        title = item.get("title", "")
        description = item.get("description", "")

        if not is_entry_level(title, description):
            continue

        jobs.append({
            "title": title,
            "company": item.get("company", {}).get("display_name"),
            "location": item.get("location", {}).get("display_name"),
            "description": description,
            "url": item.get("redirect_url"),
            "posted_date": item.get("created"),
            "source": f"adzuna-{country}",
        })

    return jobs


def fetch_jobs():
    """Fetches entry-level remote jobs across all configured countries."""
    all_jobs = []
    for country in COUNTRIES:
        print(f"  Fetching Adzuna [{country}]...")
        all_jobs.extend(fetch_jobs_for_country(country))
    return all_jobs


if __name__ == "__main__":
    results = fetch_jobs()
    print(f"\nFound {len(results)} jobs:\n")
    for job in results:
        print(f"- {job['title']} at {job['company']} ({job['location']}) [{job['source']}]")
