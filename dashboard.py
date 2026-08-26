"""
dashboard.py
Streamlit web dashboard showing job postings sorted/filtered by match score.
Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd

from db import init_db, get_all_postings, save_postings
from match import load_skills, score_all_jobs
import fetch_adzuna
import fetch_remoteok

st.set_page_config(page_title="Job Match Dashboard", layout="wide")
st.title("Job Match Dashboard")

# Make sure the postings table exists before we query it. On a brand-new
# deploy (e.g. Streamlit Cloud) there is no jobs.db file yet, which is what
# caused the sqlite3.OperationalError — this line fixes that for good.
init_db()

DEFAULT_QUERY = "software developer"


def run_pipeline(query: str):
    """Fetches fresh postings, scores them, and saves new ones to the DB."""
    with st.spinner(f"Fetching '{query}' jobs from Adzuna and RemoteOK..."):
        adzuna_jobs = fetch_adzuna.fetch_jobs(query)
        remoteok_jobs = fetch_remoteok.fetch_jobs()
        all_jobs = adzuna_jobs + remoteok_jobs

        skills = load_skills()
        scored_jobs = score_all_jobs(all_jobs, skills)
        new_count = save_postings(scored_jobs)

    st.success(f"Fetched {len(all_jobs)} postings, saved {new_count} new matches.")


postings = get_all_postings()

# First-ever load on a fresh deploy: auto-populate so any visitor lands on a
# working dashboard instead of an empty one.
if not postings:
    st.info("No postings yet — fetching an initial batch, this takes a few seconds...")
    run_pipeline(DEFAULT_QUERY)
    postings = get_all_postings()

# --- Sidebar: refresh ---
st.sidebar.header("Refresh")
query = st.sidebar.text_input("Job search query", value=DEFAULT_QUERY)
if st.sidebar.button("Fetch fresh jobs"):
    run_pipeline(query)
    postings = get_all_postings()

if not postings:
    st.warning("No postings found yet. Try fetching fresh jobs from the sidebar.")
    st.stop()

df = pd.DataFrame(postings)
df["match_score"] = (df["match_score"] * 100).round(1)

# --- Sidebar: filters ---
st.sidebar.header("Filters")

min_score = st.sidebar.slider("Minimum match score (%)", 0, 100, 0)
sources = st.sidebar.multiselect(
    "Source", options=df["source"].unique(), default=list(df["source"].unique())
)
search = st.sidebar.text_input("Search title or company")

filtered = df[
    (df["match_score"] >= min_score) &
    (df["source"].isin(sources))
]

if search:
    mask = (
        filtered["title"].str.contains(search, case=False, na=False) |
        filtered["company"].str.contains(search, case=False, na=False)
    )
    filtered = filtered[mask]

st.write(f"Showing {len(filtered)} of {len(df)} postings")

# --- Main table ---
for _, row in filtered.iterrows():
    with st.expander(f"{row['match_score']}% — {row['title']} at {row['company']} ({row['location']})"):
        st.write(f"**Matched skills:** {row['matched_skills']}")
        st.write(row["description"])
        st.markdown(f"[Apply here]({row['url']})")
