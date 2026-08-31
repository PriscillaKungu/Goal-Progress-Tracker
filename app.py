"""
app.py
Streamlit dashboard for tracking year-end goal progress.

Run with:
    streamlit run app.py

Two views, chosen from the sidebar:
    1. Log Progress - a form to record what you did today
    2. Dashboard     - charts showing completion rate, hours per goal, and trend
"""

import streamlit as st
import pandas as pd
from datetime import date

from database import init_db, add_entry, get_all_entries, GOALS

st.set_page_config(page_title="Goal Progress Tracker", layout="wide")

# Make sure the database and table exist before doing anything else
init_db()

st.title("Year-end goal progress tracker")

page = st.sidebar.radio("View", ["Log progress", "Dashboard"])

# ----------------------------------------------------------------
# PAGE 1: LOG PROGRESS
# ----------------------------------------------------------------
if page == "Log progress":
    st.subheader("Log today's work")

    with st.form("log_form", clear_on_submit=True):
        log_date = st.date_input("Date", value=date.today())

        goal_choice = st.selectbox("Goal", GOALS + ["Other (new goal)"])
        if goal_choice == "Other (new goal)":
            goal = st.text_input("New goal name", placeholder="e.g. AWS certification")
        else:
            goal = goal_choice

        course = st.text_input(
            "Course / specific topic (optional)",
            placeholder="e.g. Intermediate SQL - Window Functions",
        )
        task = st.text_input("What did you work on?", placeholder="e.g. Finished pandas merge chapter")
        status = st.selectbox("Status", ["done", "in_progress", "skipped"])
        hours_spent = st.number_input("Hours spent", min_value=0.0, max_value=12.0, step=0.25)
        notes = st.text_area("Notes (optional)", placeholder="Anything worth remembering later")

        submitted = st.form_submit_button("Save entry")
        if submitted:
            if not task.strip():
                st.error("Please describe what you worked on before saving.")
            elif not goal.strip():
                st.error("Please enter a goal name before saving.")
            else:
                add_entry(goal, task, status, hours_spent, notes, log_date.isoformat(), course)
                st.success(f"Logged: {task} ({goal})")

    st.divider()
    st.subheader("Recent entries")
    entries = get_all_entries()
    if entries:
        df = pd.DataFrame(entries)
        st.dataframe(
            df[["log_date", "goal", "course", "task", "status", "hours_spent", "notes"]].head(15),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No entries yet. Log your first task above.")

# ----------------------------------------------------------------
# PAGE 2: DASHBOARD
# ----------------------------------------------------------------
else:
    st.subheader("Progress overview")

    entries = get_all_entries()
    if not entries:
        st.info("No data yet. Log a few entries first, then come back here.")
    else:
        df = pd.DataFrame(entries)
        df["log_date"] = pd.to_datetime(df["log_date"])

        # --- Top-line metrics ---
        total_tasks = len(df)
        done_tasks = (df["status"] == "done").sum()
        completion_rate = round((done_tasks / total_tasks) * 100, 1) if total_tasks else 0
        total_hours = round(df["hours_spent"].sum(), 1)

        col1, col2, col3 = st.columns(3)
        col1.metric("Tasks logged", total_tasks)
        col2.metric("Completion rate", f"{completion_rate}%")
        col3.metric("Total hours logged", total_hours)

        st.divider()

        # --- Hours per goal (bar chart) ---
        st.markdown("**Hours spent per goal**")
        hours_by_goal = df.groupby("goal")["hours_spent"].sum().sort_values(ascending=False)
        st.bar_chart(hours_by_goal)

        # --- Completion rate per goal ---
        st.markdown("**Completion rate per goal**")
        status_by_goal = (
            df.groupby("goal")["status"]
            .apply(lambda s: round((s == "done").sum() / len(s) * 100, 1))
            .sort_values(ascending=False)
        )
        st.bar_chart(status_by_goal)

        # --- Daily trend ---
        st.markdown("**Tasks logged over time**")
        daily_counts = df.groupby(df["log_date"].dt.date).size()
        st.line_chart(daily_counts)

        # --- Streak (consecutive days with at least one entry) ---
        days_logged = sorted(df["log_date"].dt.date.unique(), reverse=True)
        streak = 0
        expected = date.today()
        for d in days_logged:
            if d == expected:
                streak += 1
                expected = expected.fromordinal(expected.toordinal() - 1)
            else:
                break
        st.markdown(f"**Current daily logging streak:** {streak} day(s)")
