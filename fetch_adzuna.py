"""
fetch_adzuna.py
Pulls job postings from the Adzuna API dynamically based on a search query.
"""
import os
import html
import requests
from dotenv import load_dotenv

load_dotenv()
APP_ID = os.getenv("APP_ID")
APP_KEY = os.getenv("APP_KEY")

# On Streamlit Cloud there is no .env file — credentials are set in the app's
# "Secrets" settings instead, and exposed via st.secrets, not os.environ.
# This fallback makes the same code work locally (.env) and when deployed.
if not APP_ID or not APP_KEY:
    try:
        import streamlit as st
        APP_ID = APP_ID or st.secrets.get("APP_ID")
        APP_KEY = APP_KEY or st.secrets.get("APP_KEY")
    except Exception:
        pass

COUNTRIES = ["us", "gb", "ca", "au", "sg", "in"]
RESULTS_PER_PAGE = 20


def fetch_jobs_for_query(country: str, query: str, page: int = 1):
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": RESULTS_PER_PAGE,
        "what": query,  # Dynamic query parameter
        "content-type": "application/json",
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return []

    data = response.json()
    jobs = []

    for item in data.get("results", []):
        title = html.unescape(item.get("title", ""))
        description = html.unescape(item.get("description", ""))
        company = item.get("company", {}).get("display_name")
        location = item.get("location", {}).get("display_name")

        jobs.append({
            "title": title,
            "company": html.unescape(company) if company else company,
            "location": html.unescape(location) if location else location,
            "description": description,
            "url": item.get("redirect_url"),
            "posted_date": item.get("created"),
            "source": f"adzuna-{country}",
        })

    return jobs


def fetch_jobs(search_query: str = "software developer"):
    """Fetches jobs across all countries based on the dynamic query."""
    all_jobs = []
    seen_urls = set()

    if not APP_ID or not APP_KEY:
        print("  [adzuna] Missing APP_ID/APP_KEY — skipping Adzuna fetch.")
        return []

    for country in COUNTRIES:
        print(f"  Fetching Adzuna [{country}] '{search_query}'...")
        for job in fetch_jobs_for_query(country, search_query):
            if job["url"] not in seen_urls:
                seen_urls.add(job["url"])
                all_jobs.append(job)

    return all_jobs
