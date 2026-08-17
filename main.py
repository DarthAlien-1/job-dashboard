"""
main.py
Runs the full pipeline: fetch jobs from all sources -> score against skills -> save to database.
Run this whenever you want to pull fresh postings.
"""

import fetch_adzuna
import fetch_remoteok
from match import load_skills, score_all_jobs
from db import init_db, save_postings

if __name__ == "__main__":
    init_db()

    print("Fetching from Adzuna (multiple countries)...")
    adzuna_jobs = fetch_adzuna.fetch_jobs()
    print(f"  -> {len(adzuna_jobs)} entry-level postings")

    print("Fetching from RemoteOK...")
    remoteok_jobs = fetch_remoteok.fetch_jobs()
    print(f"  -> {len(remoteok_jobs)} entry-level postings")

    all_jobs = adzuna_jobs + remoteok_jobs

    print("Loading your skills...")
    skills = load_skills()

    print("Scoring jobs...")
    scored_jobs = score_all_jobs(all_jobs, skills)

    print("Saving to database...")
    new_count = save_postings(scored_jobs)

    print(f"\nDone. {new_count} new postings saved out of {len(all_jobs)} fetched.")
