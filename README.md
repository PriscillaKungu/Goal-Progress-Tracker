# Goal progress tracker

A small end-to-end data project: log daily task progress, store it in SQLite,
and view it on a Streamlit dashboard. Built as a learning project covering
SQL, pandas, and basic dashboarding — the same skills used in the DataCamp
tracks and portfolio projects it's meant to help you finish.

## Project structure

```
progress_tracker/
├── app.py           # Streamlit app: logging form + dashboard
├── database.py       # SQLite schema and helper functions
├── requirements.txt  # Python dependencies
└── README.md
```

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Run the app:
   ```
   streamlit run app.py
   ```
3. Your browser will open automatically at `http://localhost:8501`.

The first run creates a `progress.db` SQLite file in the same folder —
that's your whole database, no server needed.

## How it works

- **Log progress page**: pick a goal (Python, SQL, Project 1, job search,
  literature review, YouTube), describe the task, mark it done / in
  progress / skipped, and log hours spent.
- **Dashboard page**: shows completion rate, hours per goal, a daily trend
  chart, and your current logging streak.

## Ways to extend this (good next portfolio steps)

- Add a `predicted_completion_date` column and a simple linear model that
  estimates whether you're on pace to finish each goal by December 31.
- Swap the bar/line charts for Plotly for more interactive visuals.
- Add authentication and deploy it (Streamlit Community Cloud is free) so
  it's a live link you can put in your portfolio.
- Export weekly summaries to PDF or a Notion page automatically.
- Add a `goals` table with target hours/dates per goal, so the dashboard
  can show "on track" / "behind" status instead of just raw numbers.

## Why SQLite here

SQLite needs no separate server or setup — just a single file — which
makes it the easiest real database to practice SQL against locally. The
`database.py` file is deliberately separated from `app.py` so you can
later swap in Postgres or another database without touching the UI code.
