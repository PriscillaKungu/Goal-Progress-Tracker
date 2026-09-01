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
            skill_tag TEXT,
            task TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('done', 'in_progress', 'skipped')),
            hours_spent REAL DEFAULT 0,
            notes TEXT
        )
        """
    )
    # If the table already existed from before this feature was added, add the column.
    cursor.execute("PRAGMA table_info(tasks)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    if "skill_tag" not in existing_columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN skill_tag TEXT")
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
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            target_hours REAL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS subtopics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_name TEXT NOT NULL,
            subtopic_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'not_started'
                CHECK (status IN ('not_started', 'in_progress', 'done')),
            order_index INTEGER
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS deadlines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            deadline_date TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_start TEXT NOT NULL UNIQUE,
            reflection_text TEXT NOT NULL
        )
        """
    )
    conn.commit()

    # Seed the goals table with the original six goals, once, if it's empty.
    cursor.execute("SELECT COUNT(*) FROM goals")
    if cursor.fetchone()[0] == 0:
        for g in GOALS:
            cursor.execute(
                "INSERT OR IGNORE INTO goals (name, target_hours) VALUES (?, NULL)", (g,)
            )
        conn.commit()

    # Seed one default deadline, once, if the table is empty.
    cursor.execute("SELECT COUNT(*) FROM deadlines")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO deadlines (name, deadline_date) VALUES (?, ?)",
            ("Year-end goals", "2026-12-31"),
        )
        conn.commit()

    conn.close()


def add_entry(goal, task, status, hours_spent=0.0, notes="", log_date=None, course="", skill_tag=""):
    """Insert one task log entry. log_date defaults to today."""
    if log_date is None:
        log_date = date.today().isoformat()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO tasks (log_date, goal, course, skill_tag, task, status, hours_spent, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (log_date, goal, course, skill_tag, task, status, hours_spent, notes),
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


# ----------------------------------------------------------------
# GOALS (custom goal list + optional overall hour targets)
# ----------------------------------------------------------------

def get_all_goal_names():
    """Return every goal name, in the order they were added."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM goals ORDER BY id ASC")
    names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return names


def get_all_goals():
    """Return every goal as a list of dicts, including target_hours."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM goals ORDER BY id ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def add_goal(name, target_hours=None):
    """Add a new goal. Safe to call even if it already exists (ignored)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO goals (name, target_hours) VALUES (?, ?)",
        (name, target_hours),
    )
    conn.commit()
    conn.close()


def set_goal_target(name, target_hours):
    """Set or update the overall target hours for a goal (used when it has no subtopics)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE goals SET target_hours = ? WHERE name = ?", (target_hours, name))
    conn.commit()
    conn.close()


# ----------------------------------------------------------------
# SUBTOPICS (e.g. individual DataCamp courses under "DataCamp Python")
# ----------------------------------------------------------------

def add_subtopic(goal_name, subtopic_name):
    """Add a new subtopic under a goal, e.g. 'Joining Data with Pandas' under 'DataCamp Python'."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(MAX(order_index), -1) + 1 FROM subtopics WHERE goal_name = ?", (goal_name,))
    next_order = cursor.fetchone()[0]
    cursor.execute(
        """
        INSERT INTO subtopics (goal_name, subtopic_name, status, order_index)
        VALUES (?, ?, 'not_started', ?)
        """,
        (goal_name, subtopic_name, next_order),
    )
    conn.commit()
    conn.close()


def get_subtopics(goal_name):
    """Return all subtopics for a goal, in the order they were added."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM subtopics WHERE goal_name = ? ORDER BY order_index ASC", (goal_name,)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_all_subtopics():
    """Return every subtopic across all goals."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subtopics ORDER BY goal_name ASC, order_index ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def update_subtopic_status(subtopic_id, new_status):
    """Mark a subtopic as not_started / in_progress / done."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE subtopics SET status = ? WHERE id = ?", (new_status, subtopic_id))
    conn.commit()
    conn.close()


def delete_subtopic(subtopic_id):
    """Delete a subtopic, in case you added one by mistake."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subtopics WHERE id = ?", (subtopic_id,))
    conn.commit()
    conn.close()


def goal_progress(goal_name, hours_logged=0.0):
    """
    Return (percent, method) for a goal's progress.
    - If the goal has subtopics, percent = done subtopics / total subtopics.
    - Else if it has a target_hours set, percent = hours_logged / target_hours.
    - Else, no target exists: percent is None.
    """
    subtopics = get_subtopics(goal_name)
    if subtopics:
        done = sum(1 for s in subtopics if s["status"] == "done")
        percent = round((done / len(subtopics)) * 100, 1)
        return percent, "subtopics"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT target_hours FROM goals WHERE name = ?", (goal_name,))
    row = cursor.fetchone()
    conn.close()
    target_hours = row[0] if row else None

    if target_hours:
        percent = round(min((hours_logged / target_hours) * 100, 100), 1)
        return percent, "hours"

    return None, None


# ----------------------------------------------------------------
# DEADLINES (countdown widget)
# ----------------------------------------------------------------

def add_deadline(name, deadline_date):
    """Add a deadline. deadline_date should be an ISO date string (YYYY-MM-DD)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO deadlines (name, deadline_date) VALUES (?, ?)", (name, deadline_date)
    )
    conn.commit()
    conn.close()


def get_all_deadlines():
    """Return every deadline, soonest first."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM deadlines ORDER BY deadline_date ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def delete_deadline(deadline_id):
    """Remove a deadline, e.g. after it's passed or been completed."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM deadlines WHERE id = ?", (deadline_id,))
    conn.commit()
    conn.close()


# ----------------------------------------------------------------
# REFLECTIONS (weekly "what's one thing to change" prompt)
# ----------------------------------------------------------------

def save_reflection(week_start, reflection_text):
    """Save or overwrite the reflection for a given week (week_start = Monday's ISO date)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO reflections (week_start, reflection_text)
        VALUES (?, ?)
        ON CONFLICT(week_start) DO UPDATE SET reflection_text = excluded.reflection_text
        """,
        (week_start, reflection_text),
    )
    conn.commit()
    conn.close()


def get_reflection(week_start):
    """Return the reflection text for a given week, or None if not yet written."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT reflection_text FROM reflections WHERE week_start = ?", (week_start,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def get_all_reflections():
    """Return every reflection, most recent week first."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reflections ORDER BY week_start DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows
