"""
match.py
Scores a job posting against your skills.json using fuzzy matching,
so variations like "React.js" still match "React".
"""

import json
from rapidfuzz import fuzz


def load_skills(path="skills.json"):
    with open(path, "r") as f:
        data = json.load(f)
    return [s["name"] for s in data["skills"]]


def score_job(description, skills, threshold=80):
    if not description:
        return 0, []

    description_lower = description.lower()
    matched = []

    for skill in skills:
        skill_lower = skill.lower()
        # Fast path: exact substring match
        if skill_lower in description_lower:
            matched.append(skill)
            continue
        # Fuzzy path: catches things like "React.js" vs "React", minor typos, etc.
        if fuzz.partial_ratio(skill_lower, description_lower) >= threshold:
            matched.append(skill)

    score = len(matched) / len(skills) if skills else 0
    return round(score, 3), matched


def score_all_jobs(jobs, skills):
    for job in jobs:
        score, matched = score_job(job.get("description", ""), skills)
        job["match_score"] = score
        job["matched_skills"] = matched
    return jobs
