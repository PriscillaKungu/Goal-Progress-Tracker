"""
Goal Progress Tracker — UI/UX v2
--------------------------------
A refactored Streamlit entrypoint designed around:

PLAN → DO → REVIEW

It keeps the existing database/calendar functions used by the original app,
but reorganizes the UI into a Today-first productivity experience.

Expected companion files:
    database.py
    calendar_sync.py

Run:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta

from database import (
    init_db,
    add_entry,
    get_all_entries,
    add_application,
    get_all_applications,
    update_application_status,
    add_win,
    get_all_wins,
    get_all_goal_names,
    get_all_goals,
    add_goal,
    set_goal_target,
    add_subtopic,
    get_subtopics,
    update_subtopic_status,
    delete_subtopic,
    goal_progress,
    add_deadline,
    get_all_deadlines,
    delete_deadline,
    save_reflection,
    get_reflection,
    get_all_reflections,
)
from calendar_sync import fetch_today_events


# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="Goal Tracker",
    page_icon=":material/track_changes:",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()


# ---------------------------------------------------------------------
# DESIGN SYSTEM
# ---------------------------------------------------------------------

st.html(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@600;700&display=swap');

    :root {
        --bg: #F7F6F2;
        --surface: #FFFFFF;
        --surface-2: #F1F4F1;
        --text: #17211D;
        --muted: #6B746F;
        --primary: #0F6466;
        --primary-soft: #E1F0EC;
        --accent: #C8872D;
        --accent-soft: #F9EBD7;
        --success: #227A58;
        --success-soft: #E2F1E9;
        --danger: #B84B3D;
        --danger-soft: #F8E5E1;
        --border: #E4E7E3;
        --shadow: 0 1px 2px rgba(23,33,29,.04), 0 8px 24px rgba(23,33,29,.04);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: var(--bg);
    }

    h1, h2, h3 {
        font-family: 'Sora', sans-serif !important;
        color: var(--text) !important;
        letter-spacing: -0.02em;
    }

    h1 { font-size: 2.15rem !important; }
    h2 { font-size: 1.55rem !important; }
    h3 { font-size: 1.15rem !important; }

    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: var(--shadow);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: var(--text) !important;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 600;
        border: 1px solid var(--border);
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        border-color: var(--primary);
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--border);
        border-radius: 12px;
        background: var(--surface);
    }

    div[data-testid="stContainer"] {
        border-radius: 14px;
    }

    [data-testid="stProgressBar"] > div > div > div > div {
        border-radius: 999px;
    }

    .hero {
        background: linear-gradient(135deg, #E7F2EE 0%, #F7F6F2 72%);
        border: 1px solid #DCE9E3;
        border-radius: 20px;
        padding: 28px 30px;
        margin-bottom: 22px;
    }

    .eyebrow {
        color: var(--primary);
        font-size: .76rem;
        font-weight: 700;
        letter-spacing: .10em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .hero-title {
        color: var(--text);
        font-family: 'Sora', sans-serif;
        font-size: 2.0rem;
        font-weight: 700;
        line-height: 1.15;
        margin-bottom: 8px;
    }

    .hero-copy {
        color: var(--muted);
        font-size: 1rem;
    }

    .section-label {
        color: var(--muted);
        font-size: .76rem;
        font-weight: 700;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin: 18px 0 10px;
    }

    .task-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 16px 18px;
        margin-bottom: 10px;
        box-shadow: var(--shadow);
    }

    .task-title {
        color: var(--text);
        font-weight: 700;
        font-size: 1rem;
    }

    .task-meta {
        color: var(--muted);
        font-size: .86rem;
        margin-top: 4px;
    }

    .pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: .74rem;
        font-weight: 700;
        line-height: 1;
    }

    .pill-success { background: var(--success-soft); color: var(--success); }
    .pill-primary { background: var(--primary-soft); color: var(--primary); }
    .pill-warning { background: var(--accent-soft); color: #8A5A12; }
    .pill-danger { background: var(--danger-soft); color: var(--danger); }
    .pill-neutral { background: #ECEDEB; color: #626A65; }

    .goal-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: var(--shadow);
    }

    .goal-name {
        font-weight: 700;
        color: var(--text);
        margin-bottom: 7px;
    }

    .goal-stat {
        color: var(--muted);
        font-size: .82rem;
    }

    .insight-card {
        background: var(--primary);
        color: white;
        border-radius: 14px;
        padding: 18px 20px;
        margin: 10px 0;
    }

    .insight-title {
        font-weight: 700;
        margin-bottom: 5px;
    }

    .insight-copy {
        opacity: .9;
        font-size: .9rem;
    }

    .quick-action {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 14px;
        text-align: center;
    }

    @media (max-width: 900px) {
        h1 { font-size: 1.75rem !important; }
        .hero { padding: 22px; }
        .hero-title { font-size: 1.6rem; }
    }
    </style>
    """
)


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------

def safe_df(entries):
    """Return a DataFrame with the expected columns."""
    if not entries:
        return pd.DataFrame()
    df = pd.DataFrame(entries)
    if "log_date" in df.columns:
        df["log_date"] = pd.to_datetime(df["log_date"])
    if "hours_spent" in df.columns:
        df["hours_spent"] = pd.to_numeric(df["hours_spent"], errors="coerce").fillna(0)
    return df


def status_pill(status):
    labels = {
        "done": ("Done", "success"),
        "in_progress": ("In progress", "warning"),
        "skipped": ("Skipped", "neutral"),
        "applied": ("Applied", "primary"),
        "interview": ("Interview", "warning"),
        "offer": ("Offer", "success"),
        "rejected": ("Rejected", "danger"),
        "no_response": ("No response", "neutral"),
        "not_started": ("Not started", "neutral"),
    }
    label, cls = labels.get(status, (str(status).replace("_", " ").title(), "neutral"))
    return f'<span class="pill pill-{cls}">{label}</span>'


def days_left(deadline_date):
    return (date.fromisoformat(deadline_date) - date.today()).days


def deadline_label(days):
    if days < 0:
        return f"{abs(days)} days overdue"
    if days == 0:
        return "Due today"
    if days == 1:
        return "Due tomorrow"
    return f"{days} days left"


def deadline_class(days):
    if days < 0:
        return "danger"
    if days <= 2:
        return "danger"
    if days <= 7:
        return "warning"
    return "primary"


def greeting():
    hour = pd.Timestamp.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 18:
        return "Good afternoon"
    return "Good evening"


def current_streak(df):
    if df.empty:
        return 0
    logged = set(df["log_date"].dt.date.tolist())
    cursor = date.today()
    streak = 0
    while cursor in logged:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def goal_stats(df):
    goals = get_all_goals()
    output = []
    for g in goals:
        goal_name = g["name"]
        hours = round(
            df.loc[df["goal"] == goal_name, "hours_spent"].sum(), 1
        ) if not df.empty else 0
        percent, method = goal_progress(goal_name, hours)
        output.append((g, hours, percent, method))
    return output


def render_deadlines(compact=False):
    deadlines = get_all_deadlines()
    if not deadlines:
        return

    st.markdown('<div class="section-label">Coming up</div>', unsafe_allow_html=True)

    cols = st.columns(min(len(deadlines), 3))
    for i, d in enumerate(deadlines[:3]):
        days = days_left(d["deadline_date"])
        cls = deadline_class(days)
        with cols[i]:
            st.markdown(
                f"""
                <div class="goal-card">
                    <div class="goal-name">{d['name']}</div>
                    <span class="pill pill-{cls}">{deadline_label(days)}</span>
                    <div class="goal-stat" style="margin-top:8px;">
                        {date.fromisoformat(d['deadline_date']).strftime('%b %d, %Y')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_deadline_manager():
    with st.expander("Manage deadlines"):
        with st.form("deadline_form", clear_on_submit=True):
            c1, c2 = st.columns([2, 1])
            name = c1.text_input("Deadline name", placeholder="e.g. Literature review")
            deadline = c2.date_input("Due date", value=date.today())
            if st.form_submit_button("Add deadline", use_container_width=True):
                if name.strip():
                    add_deadline(name.strip(), deadline.isoformat())
                    st.rerun()
                else:
                    st.error("Enter a deadline name.")

        for d in get_all_deadlines():
            c1, c2 = st.columns([4, 1])
            c1.write(f"**{d['name']}** · {d['deadline_date']}")
            if c2.button("Remove", key=f"remove_deadline_{d['id']}", use_container_width=True):
                delete_deadline(d["id"])
                st.rerun()


def log_entry_from_event(event, index):
    with st.container(border=True):
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(f'<div class="task-title">{event["title"]}</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="task-meta">{event["goal"]} · {event["start"]} · {event["hours"]}h planned</div>',
                unsafe_allow_html=True,
            )
        with c2:
            hours = st.number_input(
                "Actual hours",
                value=float(event["hours"]),
                min_value=0.0,
                max_value=12.0,
                step=0.25,
                key=f"calendar_hours_{index}",
            )

        note = st.text_input(
            "Note",
            key=f"calendar_note_{index}",
            placeholder="Optional one-line note",
            label_visibility="collapsed",
        )

        b1, b2, b3 = st.columns(3)
        if b1.button("✓ Complete", key=f"calendar_done_{index}", use_container_width=True):
            add_entry(event["goal"], event["title"], "done", hours, note)
            st.success("Completed and logged.")
            st.rerun()

        if b2.button("▶ Continue", key=f"calendar_progress_{index}", use_container_width=True):
            add_entry(event["goal"], event["title"], "in_progress", hours, note)
            st.info("Logged as in progress.")
            st.rerun()

        if b3.button("— Skip", key=f"calendar_skip_{index}", use_container_width=True):
            add_entry(event["goal"], event["title"], "skipped", hours, note)
            st.info("Skipped and logged.")
            st.rerun()


# ---------------------------------------------------------------------
# COMMON SIDEBAR
# ---------------------------------------------------------------------

with st.sidebar:
    st.markdown("## Goal Tracker")
    st.caption("Plan → Do → Review")

    st.divider()

    df_sidebar = safe_df(get_all_entries())
    if not df_sidebar.empty:
        st.metric("Focus time", f"{df_sidebar['hours_spent'].sum():.1f}h")
        st.caption(f"{current_streak(df_sidebar)} day logging streak")
    else:
        st.caption("Start by logging today's work.")

    st.divider()
    st.caption("Your personal productivity command center")


# ---------------------------------------------------------------------
# HOME / TODAY
# ---------------------------------------------------------------------

def home_page():
    df = safe_df(get_all_entries())
    today = date.today()

    today_df = (
        df[df["log_date"].dt.date == today]
        if not df.empty
        else pd.DataFrame()
    )

    today_hours = float(today_df["hours_spent"].sum()) if not today_df.empty else 0
    today_done = int((today_df["status"] == "done").sum()) if not today_df.empty else 0

    # Calendar
    events = []
    ical_url = st.secrets.get("gcal_ical_url", "")
    calendar_error = None

    if ical_url:
        try:
            events = fetch_today_events(ical_url)
        except Exception as exc:
            calendar_error = str(exc)

    planned_hours = round(sum(float(e.get("hours", 0)) for e in events), 1)
    execution = round((today_hours / planned_hours) * 100) if planned_hours else None

    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">{today.strftime('%A · %B %d, %Y')}</div>
            <div class="hero-title">{greeting()} 👋</div>
            <div class="hero-copy">
                {'You have ' + str(len(events)) + ' scheduled focus blocks today.' if events
                 else 'Start by choosing one important thing to move forward today.'}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Top metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Planned", f"{planned_hours:.1f}h")
    c2.metric("Completed", f"{today_hours:.1f}h")
    c3.metric("Tasks done", today_done)
    c4.metric("Execution", f"{execution}%" if execution is not None else "—")

    # Today's calendar
    st.markdown('<div class="section-label">Today</div>', unsafe_allow_html=True)

    if calendar_error:
        st.error(f"Calendar could not be loaded: {calendar_error}")
    elif not ical_url:
        st.info("Connect Google Calendar to turn today's scheduled blocks into one-click work logs.")
    elif not events:
        st.info("No scheduled focus blocks found for today.")
    else:
        for i, event in enumerate(events):
            log_entry_from_event(event, i)

    # Goals
    st.markdown('<div class="section-label">Goals</div>', unsafe_allow_html=True)

    stats = goal_stats(df)
    if not stats:
        st.info("No goals yet. Create your first goal below.")
    else:
        for g, hours, percent, method in stats[:6]:
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"**{g['name']}**")
                    if percent is not None:
                        st.progress(max(0, min(percent, 100)) / 100)
                        st.caption(f"{percent}% complete · {hours:.1f}h logged")
                    else:
                        st.caption(f"{hours:.1f}h logged · no target yet")
                with c2:
                    if percent is not None:
                        st.metric("Progress", f"{percent}%")

    # Upcoming
    render_deadlines()

    # Wins
    wins = get_all_wins()
    if wins:
        st.markdown('<div class="section-label">Recent wins</div>', unsafe_allow_html=True)
        for win in wins[:3]:
            st.markdown(
                f"""
                <div class="task-card">
                    <div class="task-title">🏆 {win['win_text']}</div>
                    <div class="task-meta">{win['win_date']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    render_deadline_manager()


# ---------------------------------------------------------------------
# GOALS
# ---------------------------------------------------------------------

def goals_page():
    st.title("Goals")
    st.caption("Turn broad goals into visible, actionable progress.")

    goals = get_all_goals()
    df = safe_df(get_all_entries())

    active = len(goals)
    percentages = [
        goal_progress(g["name"], float(df.loc[df["goal"] == g["name"], "hours_spent"].sum()))[0]
        for g in goals
    ]
    percentages = [p for p in percentages if p is not None]
    avg_progress = round(sum(percentages) / len(percentages)) if percentages else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Active goals", active)
    c2.metric("Average progress", f"{avg_progress}%")
    c3.metric("Deadlines", len(get_all_deadlines()))

    with st.expander("＋ Create a new goal"):
        with st.form("new_goal_form", clear_on_submit=True):
            name = st.text_input("Goal name", placeholder="e.g. Become job-ready in data science")
            target = st.number_input(
                "Optional target hours",
                min_value=0.0,
                step=0.5,
                help="Use this only if you are not defining subtopics.",
            )
            if st.form_submit_button("Create goal", use_container_width=True):
                if name.strip():
                    add_goal(name.strip(), target or None)
                    st.success("Goal created.")
                    st.rerun()
                else:
                    st.error("Enter a goal name.")

    for g in goals:
        hours = round(
            df.loc[df["goal"] == g["name"], "hours_spent"].sum(), 1
        ) if not df.empty else 0
        percent, method = goal_progress(g["name"], hours)
        subtopics = get_subtopics(g["name"])

        with st.container(border=True):
            st.markdown(f"### {g['name']}")

            if percent is not None:
                st.progress(max(0, min(percent, 100)) / 100)
                st.caption(f"{percent}% complete · {hours:.1f}h logged")
            else:
                st.caption(f"{hours:.1f}h logged · no target yet")

            if subtopics:
                done = sum(s["status"] == "done" for s in subtopics)
                st.markdown(f"**Next actions · {done}/{len(subtopics)} complete**")

                for s in subtopics:
                    c1, c2, c3 = st.columns([4, 1.4, .5])
                    with c1:
                        icon = {"done": "✓", "in_progress": "▶", "not_started": "○"}.get(
                            s["status"], "○"
                        )
                        st.write(f"{icon} {s['subtopic_name']}")
                    with c2:
                        options = ["not_started", "in_progress", "done"]
                        new_status = st.selectbox(
                            "Status",
                            options,
                            index=options.index(s["status"]),
                            key=f"goal_status_{s['id']}",
                            label_visibility="collapsed",
                        )
                        if new_status != s["status"]:
                            update_subtopic_status(s["id"], new_status)
                            st.rerun()
                    with c3:
                        if st.button("×", key=f"goal_delete_{s['id']}"):
                            delete_subtopic(s["id"])
                            st.rerun()

            else:
                st.caption("Add subtopics to make progress more concrete.")

                if percent is None:
                    target_value = st.number_input(
                        "Target hours",
                        min_value=0.0,
                        step=0.5,
                        key=f"target_{g['id']}",
                    )
                    if st.button("Save target", key=f"save_target_{g['id']}"):
                        if target_value > 0:
                            set_goal_target(g["name"], target_value)
                            st.rerun()

            with st.form(f"subtopic_form_{g['id']}", clear_on_submit=True):
                c1, c2 = st.columns([4, 1])
                new_sub = c1.text_input(
                    "Next action",
                    placeholder="e.g. Complete Joining Data with Pandas",
                    label_visibility="collapsed",
                )
                if c2.form_submit_button("Add next action"):
                    if new_sub.strip():
                        add_subtopic(g["name"], new_sub.strip())
                        st.rerun()


# ---------------------------------------------------------------------
# WORK LOG
# ---------------------------------------------------------------------

def work_log_page():
    st.title("Log work")
    st.caption("Capture meaningful work in seconds. Add detail only when it is useful.")

    goals = get_all_goal_names()

    with st.form("quick_work_form", clear_on_submit=True):
        task = st.text_input(
            "What did you work on?",
            placeholder="e.g. Finished the Pandas merge chapter",
        )

        c1, c2 = st.columns(2)
        goal_choice = c1.selectbox(
            "Goal",
            goals + ["Other (new goal)"],
        )
        hours = c2.number_input(
            "Duration",
            min_value=0.0,
            max_value=12.0,
            step=0.25,
            value=0.5,
        )

        status = st.radio(
            "Status",
            ["done", "in_progress", "skipped"],
            format_func=lambda x: {
                "done": "✓ Done",
                "in_progress": "▶ In progress",
                "skipped": "— Skipped",
            }[x],
            horizontal=True,
        )

        with st.expander("＋ Add details"):
            if goal_choice == "Other (new goal)":
                goal = st.text_input(
                    "New goal name",
                    placeholder="e.g. French",
                )
            else:
                goal = goal_choice

            course = st.text_input(
                "Course / topic",
                placeholder="e.g. Intermediate SQL — Window Functions",
            )
            skill = st.text_input(
                "Skill",
                placeholder="e.g. Pandas, SQL joins, XGBoost",
            )
            notes = st.text_area(
                "Notes",
                placeholder="Anything worth remembering later",
            )
            log_date = st.date_input("Date", value=date.today())

        if st.form_submit_button("Save work", type="primary", use_container_width=True):
            if not task.strip():
                st.error("Describe what you worked on.")
            elif not goal.strip():
                st.error("Enter a goal.")
            else:
                add_entry(
                    goal,
                    task,
                    status,
                    hours,
                    notes,
                    log_date.isoformat(),
                    course,
                    skill,
                )
                add_goal(goal)
                st.success("Work logged.")
                st.rerun()

    st.divider()
    st.subheader("Recent activity")

    entries = get_all_entries()
    if not entries:
        st.info("Nothing logged yet. Your activity will appear here.")
        return

    df = safe_df(entries)
    display = df.sort_values("log_date", ascending=False).copy()
    display["log_date"] = display["log_date"].dt.strftime("%b %d, %Y")

    st.dataframe(
        display[
            [
                "log_date",
                "goal",
                "task",
                "hours_spent",
                "status",
                "skill_tag",
                "notes",
            ]
        ].head(20),
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------------------
# SKILLS
# ---------------------------------------------------------------------

def skills_page():
    st.title("Skills")
    st.caption("Build career capital from the work you actually practice.")

    df = safe_df(get_all_entries())
    if df.empty or "skill_tag" not in df.columns:
        st.info("No skill evidence yet. Add a skill when logging work.")
        return

    tagged = df[df["skill_tag"].fillna("").astype(str).str.strip() != ""].copy()
    if tagged.empty:
        st.info("No skill evidence yet. Try tags such as Pandas, SQL, Python or XGBoost.")
        return

    by_skill = (
        tagged.groupby("skill_tag")["hours_spent"]
        .sum()
        .sort_values(ascending=False)
    )

    total_hours = float(tagged["hours_spent"].sum())
    practiced_this_week = tagged[
        tagged["log_date"].dt.date >= date.today() - timedelta(days=6)
    ]["skill_tag"].nunique()

    c1, c2, c3 = st.columns(3)
    c1.metric("Skills practiced", len(by_skill))
    c2.metric("Evidence hours", f"{total_hours:.1f}h")
    c3.metric("Skills this week", practiced_this_week)

    st.subheader("Skill portfolio")

    max_hours = max(by_skill.max(), 1)
    for skill, hours in by_skill.items():
        sessions = len(tagged[tagged["skill_tag"] == skill])
        last = tagged.loc[tagged["skill_tag"] == skill, "log_date"].max()

        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"**{skill}**")
                st.progress(min(hours / max_hours, 1))
                st.caption(f"{hours:.1f}h · {sessions} sessions · last practiced {last.strftime('%b %d')}")
            with c2:
                st.metric("Hours", f"{hours:.1f}")

    st.subheader("Evidence")
    for skill, group in tagged.groupby("skill_tag"):
        with st.expander(f"{skill} · {len(group)} sessions"):
            for _, row in group.sort_values("log_date", ascending=False).iterrows():
                st.markdown(
                    f"**{row['log_date'].strftime('%b %d, %Y')}** — {row['task']} "
                    f"({row['hours_spent']:.1f}h)"
                )


# ---------------------------------------------------------------------
# CAREER
# ---------------------------------------------------------------------

def career_page():
    st.title("Career")
    st.caption("Track the job-search funnel, not just the number of applications.")

    applications = get_all_applications()

    with st.form("application_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        company = c1.text_input("Company")
        role = c2.text_input("Role")
        c3, c4 = st.columns(2)
        applied = c3.date_input("Date applied", value=date.today())
        link = c4.text_input("Job link", placeholder="Optional")

        notes = st.text_area(
            "Notes",
            placeholder="Referral, contact, follow-up plan...",
        )

        if st.form_submit_button("Add application", type="primary", use_container_width=True):
            if company.strip() and role.strip():
                add_application(
                    company,
                    role,
                    "applied",
                    link,
                    notes,
                    applied.isoformat(),
                )
                st.success("Application added.")
                st.rerun()
            else:
                st.error("Company and role are required.")

    if not applications:
        st.info("No applications yet.")
        return

    df = pd.DataFrame(applications)
    total = len(df)
    interviews = int((df["status"] == "interview").sum())
    offers = int((df["status"] == "offer").sum())
    responded = interviews + offers
    response_rate = round((responded / total) * 100, 1) if total else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Applications", total)
    c2.metric("Interviews", interviews)
    c3.metric("Offers", offers)
    c4.metric("Response rate", f"{response_rate}%")

    st.divider()

    status_options = ["applied", "interview", "offer", "rejected", "no_response"]

    for row in applications:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])

            with c1:
                st.markdown(f"**{row['role']}** · {row['company']}")
                st.caption(f"Applied {row['date_applied']}")
                st.markdown(status_pill(row["status"]), unsafe_allow_html=True)
                if row.get("notes"):
                    st.caption(row["notes"])

            with c2:
                current = status_options.index(row["status"])
                new_status = st.selectbox(
                    "Status",
                    status_options,
                    index=current,
                    key=f"career_status_{row['id']}",
                    label_visibility="collapsed",
                )
                if new_status != row["status"]:
                    update_application_status(row["id"], new_status)
                    st.rerun()


# ---------------------------------------------------------------------
# WINS
# ---------------------------------------------------------------------

def wins_page():
    st.title("Wins")
    st.caption("Make invisible progress visible.")

    with st.form("win_form", clear_on_submit=True):
        win_date = st.date_input("Date", value=date.today())
        text = st.text_area(
            "What happened?",
            placeholder="e.g. Completed the Pandas module or got an interview",
        )

        if st.form_submit_button("Record win", type="primary", use_container_width=True):
            if text.strip():
                add_win(text.strip(), win_date.isoformat())
                st.success("Win recorded.")
                st.rerun()
            else:
                st.error("Describe the win first.")

    wins = get_all_wins()
    if not wins:
        st.info("No wins yet. Small wins count.")
        return

    st.subheader("Recent wins")
    for win in wins[:30]:
        st.markdown(
            f"""
            <div class="task-card">
                <div class="task-title">🏆 {win['win_text']}</div>
                <div class="task-meta">{win['win_date']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------
# INSIGHTS / REVIEW
# ---------------------------------------------------------------------

def insights_page():
    st.title("Progress & review")
    st.caption("Use the data to decide what to change next.")

    df = safe_df(get_all_entries())
    if df.empty:
        st.info("Log a few activities first, then return here for insights.")
        return

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_df = df[df["log_date"].dt.date >= week_start]

    total_hours = round(float(week_df["hours_spent"].sum()), 1)
    done = int((week_df["status"] == "done").sum())
    entries = len(week_df)
    completion = round((done / entries) * 100) if entries else 0
    streak = current_streak(df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("This week", f"{total_hours:.1f}h")
    c2.metric("Tasks done", done)
    c3.metric("Completion", f"{completion}%")
    c4.metric("Logging streak", f"{streak}d")

    st.markdown('<div class="section-label">Where your time went</div>', unsafe_allow_html=True)

    hours_by_goal = (
        week_df.groupby("goal")["hours_spent"]
        .sum()
        .sort_values(ascending=False)
    )
    if not hours_by_goal.empty:
        st.bar_chart(hours_by_goal)

        top_goal = hours_by_goal.index[0]
        top_hours = float(hours_by_goal.iloc[0])
        share = round((top_hours / total_hours) * 100) if total_hours else 0

        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-title">Your biggest focus area</div>
                <div class="insight-copy">
                    {top_goal} accounts for {share}% of your logged time this week.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-label">Daily activity</div>', unsafe_allow_html=True)
    daily = df.groupby(df["log_date"].dt.date).size()
    st.line_chart(daily)

    st.markdown('<div class="section-label">Weekly reflection</div>', unsafe_allow_html=True)

    week_key = week_start.isoformat()
    existing = get_reflection(week_key) or ""

    reflection = st.text_area(
        "What's one thing to change next week?",
        value=existing,
        placeholder="e.g. Move DataCamp earlier because I keep skipping it later.",
        key=f"weekly_reflection_{week_key}",
    )

    if st.button("Save reflection", type="primary"):
        if reflection.strip():
            save_reflection(week_key, reflection.strip())
            st.success("Reflection saved.")
            st.rerun()
        else:
            st.error("Write one change before saving.")

    past = [r for r in get_all_reflections() if r["week_start"] != week_key]
    if past:
        with st.expander("Past reflections"):
            for r in past:
                label = date.fromisoformat(r["week_start"]).strftime("Week of %b %d, %Y")
                st.markdown(f"**{label}**")
                st.caption(r["reflection_text"])


# ---------------------------------------------------------------------
# NAVIGATION
# ---------------------------------------------------------------------

pages = {
    "PLAN": [
        st.Page(home_page, title="Today", icon=":material/today:", url_path=""),
        st.Page(goals_page, title="Goals", icon=":material/flag:"),
    ],
    "DO": [
        st.Page(work_log_page, title="Log work", icon=":material/add_task:"),
        st.Page(skills_page, title="Skills", icon=":material/school:"),
        st.Page(wins_page, title="Wins", icon=":material/emoji_events:"),
    ],
    "CAREER": [
        st.Page(career_page, title="Job search", icon=":material/work:"),
    ],
    "REVIEW": [
        st.Page(insights_page, title="Progress & review", icon=":material/insights:"),
    ],
}

pg = st.navigation(pages, position="sidebar", expanded=True)
pg.run()
