"""
match.py
Scores a job posting against a list of skills.
Matches against both title and description.
Exact matches use word boundaries to avoid false positives. 
Fuzzy matching is used only for longer skill names.
"""

import json
import re
from rapidfuzz import fuzz

def load_skills(path="skills.json"):
    """Loads the default skills taxonomy (only used for the background DB scrape)."""
    with open(path, "r") as f:
        data = json.load(f)
    return [s["name"] for s in data["skills"]]

def score_job(title, description, skills, threshold=90, max_expected_matches=4):
    """Scores a single job based on how many skills it contains."""
    text = f"{title or ''} {description or ''}".lower()
    if not text.strip():
        return 0, []

    matched = []

    for skill in skills:
        skill_lower = skill.lower()

        if re.search(r"[^\w]", skill_lower):
            # Skill contains punctuation (e.g. "Node.js", "C++")
            is_match = skill_lower in text
        else:
            # Standard word boundary matching
            is_match = re.search(rf"\b{re.escape(skill_lower)}\b", text) is not None

        if is_match:
            matched.append(skill)
            continue

        # Fuzzy matching for longer terms (e.g., "Workflow Automation")
        if len(skill_lower) >= 5 and fuzz.partial_ratio(skill_lower, text) >= threshold:
            matched.append(skill)

    score = min(len(matched) / max_expected_matches, 1.0)
    return round(score, 3), matched

def score_all_jobs(jobs, skills):
    """
    Scores a list of job dictionaries against a list of skills.
    Returns only the jobs that have at least one matched skill.
    """
    scored = []
    for job in jobs:
        # Ensure we are working with a dictionary
        job_dict = dict(job)
        
        score, matched = score_job(job_dict.get("title", ""), job_dict.get("description", ""), skills)
        
        job_dict["match_score"] = score
        job_dict["matched_skills"] = matched
        
        # Only keep jobs that actually match the user's skills
        if matched:
            scored.append(job_dict)
            
    return scored