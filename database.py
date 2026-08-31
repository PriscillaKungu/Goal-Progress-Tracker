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
    """Create the tasks table if it doesn't already exist. Safe to call every run."""
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
