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
from datetime import date, timedelta

from database import init_db, add_entry, get_all_entries, GOALS
from calendar_sync import fetch_today_events

st.set_page_config(page_title="Goal Progress Tracker", layout="wide")

# Make sure the database and table exist before doing anything else
init_db()

st.title("Year-end goal progress tracker")

page = st.sidebar.radio("View", ["Quick log (from calendar)", "Log progress", "Dashboard", "Summaries"])

# ----------------------------------------------------------------
# PAGE 0: QUICK LOG FROM CALENDAR
# ----------------------------------------------------------------
if page == "Quick log (from calendar)":
    st.subheader("Today's scheduled blocks")
    st.caption("Pulled from your Google Calendar. Tap a status for each block instead of typing it out.")

    ical_url = st.secrets.get("gcal_ical_url", "")
    if not ical_url:
        st.warning(
            "No calendar connected yet. Add your Google Calendar secret iCal URL "
            "to Streamlit secrets as `gcal_ical_url` - see the README for how to get it."
        )
    else:
        try:
            events = fetch_today_events(ical_url)
        except Exception as e:
            events = []
            st.error(f"Couldn't fetch calendar events: {e}")

        if ical_url and not events:
            st.info("No matching task blocks found on today's calendar.")

        for i, event in enumerate(events):
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{event['title']}**")
                    st.caption(f"{event['goal']} · {event['start']} · {event['hours']}h scheduled")
                with col2:
                    hours = st.number_input(
                        "Hours", value=event["hours"], min_value=0.0, max_value=12.0,
                        step=0.25, key=f"hours_{i}", label_visibility="collapsed",
                    )

                note = st.text_input("Note (optional)", key=f"note_{i}", placeholder="Optional one-liner")

                b1, b2, b3 = st.columns(3)
                if b1.button("Done", key=f"done_{i}", use_container_width=True):
                    add_entry(event["goal"], event["title"], "done", hours, note)
                    st.success("Logged as done")
                if b2.button("In progress", key=f"inprog_{i}", use_container_width=True):
                    add_entry(event["goal"], event["title"], "in_progress", hours, note)
                    st.success("Logged as in progress")
                if b3.button("Skipped", key=f"skip_{i}", use_container_width=True):
                    add_entry(event["goal"], event["title"], "skipped", hours, note)
                    st.info("Logged as skipped")

# ----------------------------------------------------------------
# PAGE 1: LOG PROGRESS
# ----------------------------------------------------------------
elif page == "Log progress":
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
elif page == "Dashboard":
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

# ----------------------------------------------------------------
# PAGE 3: SUMMARIES (day / week / month rollups + notes)
# ----------------------------------------------------------------
else:
    st.subheader("Progress summaries")

    entries = get_all_entries()
    if not entries:
        st.info("No data yet. Log a few entries first, then come back here.")
    else:
        df = pd.DataFrame(entries)
        df["log_date"] = pd.to_datetime(df["log_date"]).dt.date

        period = st.radio("Period", ["Today", "This week", "This month", "Custom range"], horizontal=True)

        today = date.today()
        if period == "Today":
            start = end = today
            label = today.strftime("%A, %B %d, %Y")
        elif period == "This week":
            start = today - timedelta(days=today.weekday())  # Monday
            end = start + timedelta(days=6)
            label = f"{start.strftime('%b %d, %Y')} - {end.strftime('%b %d, %Y')}"
        elif period == "This month":
            start = today.replace(day=1)
            next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
            end = next_month - timedelta(days=1)
            label = f"{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}"
        else:
            col_a, col_b = st.columns(2)
            start = col_a.date_input("From", value=today - timedelta(days=7))
            end = col_b.date_input("To", value=today)
            if start > end:
                st.error("'From' date must be before 'To' date.")
                st.stop()
            label = f"{start.strftime('%b %d, %Y')} - {end.strftime('%b %d, %Y')}"

        st.caption(label)

        period_df = df[(df["log_date"] >= start) & (df["log_date"] <= end)]

        if period_df.empty:
            st.info("Nothing logged in this period yet.")
        else:
            # --- Totals ---
            total_hours = round(period_df["hours_spent"].sum(), 1)
            done_count = (period_df["status"] == "done").sum()
            col1, col2, col3 = st.columns(3)
            col1.metric("Total hours", total_hours)
            col2.metric("Tasks done", done_count)
            col3.metric("Entries logged", len(period_df))

            st.divider()

            # --- Hours per goal for this period ---
            st.markdown("**Hours by goal**")
            hours_by_goal = (
                period_df.groupby("goal")["hours_spent"].sum().sort_values(ascending=False)
            )
            st.bar_chart(hours_by_goal)

            st.divider()

            # --- Notes, grouped by goal, most recent first ---
            st.markdown("**Notes from this period**")
            notes_df = period_df[period_df["notes"].astype(str).str.strip() != ""]
            if notes_df.empty:
                st.caption("No notes recorded this period.")
            else:
                for goal, group in notes_df.groupby("goal"):
                    group_hours = round(group["hours_spent"].sum(), 1)
                    with st.expander(f"{goal} - {group_hours}h logged ({len(group)} entries)"):
                        for _, row in group.sort_values("log_date", ascending=False).iterrows():
                            st.markdown(f"**{row['log_date'].strftime('%a %b %d, %Y')}** - {row['task']}")
                            st.caption(f"{row['status']} · {row['hours_spent']}h · {row['notes']}")
