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

- **Quick log (from calendar) page**: pulls today's blocks from your
  Google Calendar and shows one tap-to-log card per block, hours
  pre-filled from the event duration. See setup below.
- **Log progress page**: manual form - pick a goal, describe the task,
  mark it done / in progress / skipped, log hours. Use this for anything
  off-calendar or for a new "Other" goal.
- **Dashboard page**: shows completion rate, hours per goal, a daily trend
  chart, and your current logging streak.

## Connecting your Google Calendar (for Quick log)

1. In Google Calendar, go to **Settings** -> click your calendar under
   "Settings for my calendars" -> scroll to **"Integrate calendar"**.
2. Copy the **"Secret address in iCal format"** link. Keep this private -
   anyone with the link can read your calendar.
3. **Running locally:** copy `.streamlit/secrets.toml.example` to
   `.streamlit/secrets.toml` and paste your link in as `gcal_ical_url`.
   This file is already gitignored.
4. **On Streamlit Community Cloud:** go to your app -> Settings -> Secrets,
   and paste:
   ```
   gcal_ical_url = "https://calendar.google.com/calendar/ical/....../basic.ics"
   ```
   Save - the app restarts automatically with the secret available.

The app matches event titles to goals using keywords in
`calendar_sync.py` (e.g. "SQL" -> DataCamp SQL). If you rename an event
or add a new recurring block, add a matching keyword there.

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
