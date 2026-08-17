"""
db.py
Handles saving and reading job postings from a local SQLite database.
"""

import sqlite3

DB_FILE = "jobs.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS postings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            description TEXT,
            url TEXT UNIQUE,
            posted_date TEXT,
            source TEXT,
            match_score REAL,
            matched_skills TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_postings(jobs):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    new_count = 0

    for job in jobs:
        try:
            cursor.execute("""
                INSERT INTO postings
                (title, company, location, description, url, posted_date, source, match_score, matched_skills)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.get("title"),
                job.get("company"),
                job.get("location"),
                job.get("description"),
                job.get("url"),
                job.get("posted_date"),
                job.get("source"),
                job.get("match_score", 0),
                ", ".join(job.get("matched_skills", [])),
            ))
            new_count += 1
        except sqlite3.IntegrityError:
            # URL already exists, skip duplicate
            pass

    conn.commit()
    conn.close()
    return new_count


def get_all_postings():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM postings ORDER BY match_score DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
