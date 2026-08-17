"""
dashboard.py
Streamlit web dashboard showing job postings sorted/filtered by match score.
Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
from db import get_all_postings

st.set_page_config(page_title="Job Match Dashboard", layout="wide")
st.title("Job Match Dashboard")

postings = get_all_postings()

if not postings:
    st.warning("No postings found yet. Run `python main.py` first to fetch and score jobs.")
    st.stop()

df = pd.DataFrame(postings)
df["match_score"] = (df["match_score"] * 100).round(1)

# --- Sidebar filters ---
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
