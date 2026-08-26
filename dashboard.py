"""
dashboard.py
Streamlit web dashboard showing job postings sorted/filtered by match score.
Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd

from db import init_db, get_all_postings, save_postings
from match import load_skills, score_all_jobs
from cv_parser import extract_skills_from_cv
import fetch_adzuna
import fetch_remoteok

# Optional extra live sources — only used if these modules exist and accept
# a query argument the way fetch_adzuna does. Skipped safely otherwise.
OPTIONAL_SOURCES = []
for _mod_name in ("fetch_jobicy", "fetch_remotive", "fetch_jsearch"):
    try:
        OPTIONAL_SOURCES.append(__import__(_mod_name))
    except ImportError:
        pass

st.set_page_config(page_title="Job Match Dashboard", layout="wide")
st.title("Job Match Dashboard")

# Make sure the postings table exists before we query it.
init_db()

DEFAULT_QUERY = "software developer"


def render_job_list(jobs_df: pd.DataFrame, key_prefix: str):
    """Shared rendering for a list of scored postings, with filters."""
    if jobs_df.empty:
        st.info("No postings to show.")
        return

    df = jobs_df.copy()
    df["match_score"] = (df["match_score"] * 100).round(1)

    col1, col2 = st.columns([1, 2])
    with col1:
        min_score = st.slider(
            "Minimum match score (%)", 0, 100, 0, key=f"{key_prefix}_min_score"
        )
    with col2:
        search = st.text_input("Search title or company", key=f"{key_prefix}_search")

    filtered = df[df["match_score"] >= min_score]
    if search:
        mask = (
            filtered["title"].str.contains(search, case=False, na=False)
            | filtered["company"].str.contains(search, case=False, na=False)
        )
        filtered = filtered[mask]

    st.write(f"Showing {len(filtered)} of {len(df)} postings")

    for _, row in filtered.sort_values("match_score", ascending=False).iterrows():
        with st.expander(
            f"{row['match_score']}% — {row['title']} at {row['company']} ({row['location']})"
        ):
            st.write(f"**Matched skills:** {row['matched_skills']}")
            st.write(row["description"])
            st.markdown(f"[Apply here]({row['url']})")


# --- Tabs: saved default-skills matches vs. live CV-based matches ---
tab_saved, tab_cv = st.tabs(["Saved Matches", "Match My CV"])

# ===================== TAB 1: Saved matches (unchanged behavior) =====================
with tab_saved:
    def run_pipeline(query: str):
        with st.spinner(f"Fetching '{query}' jobs from Adzuna and RemoteOK..."):
            adzuna_jobs = fetch_adzuna.fetch_jobs(query)
            remoteok_jobs = fetch_remoteok.fetch_jobs()
            all_jobs = adzuna_jobs + remoteok_jobs

            skills = load_skills()
            scored_jobs = score_all_jobs(all_jobs, skills)
            new_count = save_postings(scored_jobs)
        st.success(f"Fetched {len(all_jobs)} postings, saved {new_count} new matches.")

    postings = get_all_postings()

    st.sidebar.header("Refresh saved matches")
    query = st.sidebar.text_input(
        "Job search query", value="", placeholder="e.g. software developer"
    )
    if st.sidebar.button("Fetch fresh jobs"):
        if query.strip():
            run_pipeline(query)
            postings = get_all_postings()
        else:
            st.sidebar.warning("Enter a search query first.")

    if postings:
        render_job_list(pd.DataFrame(postings), key_prefix="saved")
    else:
        st.info(
            "👋 Enter a job search query in the sidebar and click **Fetch fresh jobs** "
            "to see postings here."
        )

# ===================== TAB 2: Upload a CV, get live personalized matches =====================
with tab_cv:
    st.write(
        "Upload your CV and we'll pull out your key skills, then search live "
        "job postings and rank them by how well they match."
    )

    uploaded_file = st.file_uploader(
        "Upload your CV (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"]
    )

    if uploaded_file and st.button("Analyze & Find Jobs"):
        with st.spinner("Reading your CV and extracting skills..."):
            file_bytes = uploaded_file.read()
            extracted_skills = extract_skills_from_cv(file_bytes, uploaded_file.name)

        if not extracted_skills:
            st.error(
                "Couldn't extract skills from that file. Make sure GEMINI_API_KEY is "
                "set in your app's secrets, and that the file has readable text."
            )
        else:
            st.session_state["cv_skills"] = extracted_skills

            primary_query = extracted_skills[0]
            with st.spinner(f"Searching live postings for '{primary_query}'..."):
                live_jobs = fetch_adzuna.fetch_jobs(primary_query)
                live_jobs += fetch_remoteok.fetch_jobs()

                for source_mod in OPTIONAL_SOURCES:
                    try:
                        live_jobs += source_mod.fetch_jobs(primary_query)
                    except Exception as e:
                        print(f"  [{source_mod.__name__}] skipped: {e}")

                scored_jobs = score_all_jobs(live_jobs, extracted_skills)

            st.session_state["cv_jobs"] = scored_jobs

    # Render results if we have them in session state (persists across filter reruns
    # without re-calling Gemini or re-fetching every time a slider moves)
    if st.session_state.get("cv_skills"):
        st.write("**Skills detected in your CV:**")
        st.write(", ".join(st.session_state["cv_skills"]))

        cv_jobs = st.session_state.get("cv_jobs", [])
        if cv_jobs:
            render_job_list(pd.DataFrame(cv_jobs), key_prefix="cv")
        else:
            st.info("No live postings matched your extracted skills. Try a different CV or check back later.")
