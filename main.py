"""
main.py
Runs the full pipeline: fetch jobs from all sources -> score against default skills -> save to database.
Run this locally whenever you want to pull fresh postings in bulk.
(The deployed dashboard also runs a lighter version of this automatically.)
"""

import fetch_adzuna
import fetch_remoteok
from match import load_skills, score_all_jobs
from db import init_db, save_postings

# Optional extra sources — only used if these modules exist in your repo.
try:
    import fetch_jobicy
except ImportError:
    fetch_jobicy = None

try:
    import fetch_arbeitnow
except ImportError:
    fetch_arbeitnow = None

DEFAULT_QUERY = "software developer"

if __name__ == "__main__":
    init_db()

    print(f"Fetching from Adzuna (multiple countries) for '{DEFAULT_QUERY}'...")
    adzuna_jobs = fetch_adzuna.fetch_jobs(DEFAULT_QUERY)
    print(f"  -> {len(adzuna_jobs)} entry-level postings")

    print("Fetching from RemoteOK...")
    remoteok_jobs = fetch_remoteok.fetch_jobs()
    print(f"  -> {len(remoteok_jobs)} entry-level postings")

    all_jobs = adzuna_jobs + remoteok_jobs

    if fetch_jobicy:
        print("Fetching from Jobicy...")
        jobicy_jobs = fetch_jobicy.fetch_jobs()
        print(f"  -> {len(jobicy_jobs)} entry-level postings")
        all_jobs += jobicy_jobs

    if fetch_arbeitnow:
        print("Fetching from Arbeitnow...")
        arbeitnow_jobs = fetch_arbeitnow.fetch_jobs()
        print(f"  -> {len(arbeitnow_jobs)} entry-level postings")
        all_jobs += arbeitnow_jobs

    print("Loading default skills...")
    skills = load_skills()

    print("Scoring jobs...")
    scored_jobs = score_all_jobs(all_jobs, skills)

    print("Saving to database...")
    new_count = save_postings(scored_jobs)

    print(f"\nDone. {new_count} new postings saved out of {len(all_jobs)} fetched.")
