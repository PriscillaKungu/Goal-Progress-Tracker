"""
database.py
Handles all SQLite database logic for the progress tracker.
Keeping this separate from app.py is good practice: it means you can
swap the storage layer later (e.g. to Postgres) without touching the UI.
"""

import sqlite3
from datetime import date

DB_PATH = "progress.db"

# The six goals from your year-end plan. Edit this list any time.
GOALS = [
    "DataCamp Python",
    "DataCamp SQL",
    "Project 1: Battery Life",
    "Job search",
    "Literature review",
    "YouTube learning",
]


def get_connection():
    """Open a connection to the SQLite database file."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create all tables if they don't already exist. Safe to call every run."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date TEXT NOT NULL,
            goal TEXT NOT NULL,
            course TEXT,
            task TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('done', 'in_progress', 'skipped')),
            hours_spent REAL DEFAULT 0,
            notes TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_applied TEXT NOT NULL,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL CHECK (
                status IN ('applied', 'interview', 'offer', 'rejected', 'no_response')
            ),
            job_link TEXT,
            notes TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS wins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            win_date TEXT NOT NULL,
            win_text TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def add_entry(goal, task, status, hours_spent=0.0, notes="", log_date=None, course=""):
    """Insert one task log entry. log_date defaults to today."""
    if log_date is None:
        log_date = date.today().isoformat()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO tasks (log_date, goal, course, task, status, hours_spent, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (log_date, goal, course, task, status, hours_spent, notes),
    )
    conn.commit()
    conn.close()


def get_all_entries():
    """Return every logged entry as a list of dicts, most recent first."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY log_date DESC, id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def delete_entry(entry_id):
    """Delete a single entry by its id, in case you log something by mistake."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()


# ----------------------------------------------------------------
# APPLICATIONS (job search tracker)
# ----------------------------------------------------------------

def add_application(company, role, status="applied", job_link="", notes="", date_applied=None):
    """Log a new job application."""
    if date_applied is None:
        date_applied = date.today().isoformat()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO applications (date_applied, company, role, status, job_link, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (date_applied, company, role, status, job_link, notes),
    )
    conn.commit()
    conn.close()


def get_all_applications():
    """Return every logged application, most recent first."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications ORDER BY date_applied DESC, id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def update_application_status(application_id, new_status):
    """Update the status of an existing application (e.g. after hearing back)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE applications SET status = ? WHERE id = ?", (new_status, application_id)
    )
    conn.commit()
    conn.close()


def delete_application(application_id):
    """Delete an application entry, in case you logged one by mistake."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM applications WHERE id = ?", (application_id,))
    conn.commit()
    conn.close()


# ----------------------------------------------------------------
# WINS (short log of things worth being proud of)
# ----------------------------------------------------------------

def add_win(win_text, win_date=None):
    """Log a short win - something worth remembering, regardless of outcome."""
    if win_date is None:
        win_date = date.today().isoformat()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO wins (win_date, win_text) VALUES (?, ?)", (win_date, win_text)
    )
    conn.commit()
    conn.close()


def get_all_wins():
    """Return every logged win, most recent first."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wins ORDER BY win_date DESC, id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def delete_win(win_id):
    """Delete a win entry, in case you logged one by mistake."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wins WHERE id = ?", (win_id,))
    conn.commit()
    conn.close()
