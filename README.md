# Job Match Dashboard

A personal dashboard that scrapes entry-level, remote job postings from multiple sources, scores each one against my skills, and displays the results in an interactive web app.

Built as a portfolio project to practice API integration, data pipelines, and full-stack development.

## Features

- Pulls job postings from the **Adzuna API** across 6 countries (US, UK, Canada, Australia, Singapore, India) and the **RemoteOK API**
- Filters for entry-level roles automatically
- Scores each posting against a skills profile using fuzzy string matching (catches variations like "React.js" vs "React")
- Stores results in a local SQLite database, skipping duplicates on repeat runs
- Interactive Streamlit dashboard with filters by match score, source, and keyword search

## Tech Stack

- **Python** — core pipeline (`requests`, `rapidfuzz`, `sqlite3`)
- **Streamlit** — dashboard UI
- **Adzuna API** & **RemoteOK API** — job data sources

## How It Works

1. `fetch_adzuna.py` and `fetch_remoteok.py` pull raw postings from each source
2. `filters.py` keeps only entry-level roles (excludes senior/lead/manager titles)
3. `match.py` scores each posting against `skills.json` using fuzzy matching
4. `db.py` saves everything to a local SQLite database (`jobs.db`), skipping duplicates by URL
5. `dashboard.py` displays the results in a sortable, filterable Streamlit app

## Setup

```bash
# Install dependencies
python -m pip install requests python-dotenv rapidfuzz streamlit pandas

# Add your Adzuna API credentials to a .env file:
# APP_ID=your_app_id
# APP_KEY=your_app_key

# Fetch and score jobs
python main.py

# Launch the dashboard
python -m streamlit run dashboard.py
```

## Possible Next Steps

- Add more job sources (JSearch, LinkedIn via a licensed data provider)
- Automate daily refresh via a scheduled task
- Upgrade matching further with embedding-based similarity
