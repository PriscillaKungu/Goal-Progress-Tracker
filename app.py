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

        required_skills = st.text_input(
            "Required skills from the posting",
            placeholder="e.g. RUL prediction, sensor data, MATLAB, reliability engineering",
            help="Paste the 2-3 skills the posting emphasizes. Over time this shows what the market keeps asking for.",
        )

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
                    required_skills,
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

    # --- What the market keeps asking for (gap analysis) ---
    skills_series = df.get("required_skills")
    if skills_series is not None:
        all_skills = []
        for entry in skills_series.dropna():
            all_skills.extend([s.strip() for s in str(entry).split(",") if s.strip()])
        if all_skills:
            skill_counts = pd.Series(all_skills).value_counts().head(8)
            st.markdown('<div class="section-label">Most requested skills across your applications</div>', unsafe_allow_html=True)
            st.bar_chart(skill_counts)
            st.caption("Compare this against your Skills page - gaps here are your next build priorities.")

    st.divider()

    status_options = ["applied", "interview", "offer", "rejected", "no_response"]

    for row in applications:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])

            with c1:
                st.markdown(f"**{row['role']}** · {row['company']}")
                st.caption(f"Applied {row['date_applied']}")
                st.markdown(status_pill(row["status"]), unsafe_allow_html=True)
                if row.get("required_skills"):
                    st.caption(f"🔧 Required: {row['required_skills']}")
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
# REVIEWS — DAILY / WEEKLY / MONTHLY / CUSTOM
# ---------------------------------------------------------------------

def review_period(period):
    """Return start date, end date and a human-readable label."""
    today = date.today()

    if period == "Today":
        return today, today, today.strftime("%A, %B %d, %Y")

    if period == "This week":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return start, end, f"{start.strftime('%b %d')} – {end.strftime('%b %d, %Y')}"

    if period == "This month":
        start = today.replace(day=1)
        next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
        end = next_month - timedelta(days=1)
        return start, end, f"{start.strftime('%b %d')} – {end.strftime('%b %d, %Y')}"

    # Custom range is handled by the UI.
    return today - timedelta(days=7), today, "Custom range"


def review_metrics(period_df, start, end):
    """Calculate the numbers that matter for a review."""
    if period_df.empty:
        return {
            "hours": 0.0,
            "done": 0,
            "in_progress": 0,
            "skipped": 0,
            "entries": 0,
            "active_days": 0,
            "completion": 0,
        }

    entries = len(period_df)
    done = int((period_df["status"] == "done").sum())

    return {
        "hours": round(float(period_df["hours_spent"].sum()), 1),
        "done": done,
        "in_progress": int((period_df["status"] == "in_progress").sum()),
        "skipped": int((period_df["status"] == "skipped").sum()),
        "entries": entries,
        "active_days": int(period_df["log_date"].dt.date.nunique()),
        "completion": round((done / entries) * 100) if entries else 0,
    }


def render_completed_work(period_df):
    """Show the actual work completed during the selected period."""
    st.markdown('<div class="section-label">What you actually accomplished</div>', unsafe_allow_html=True)

    completed = period_df[period_df["status"] == "done"].sort_values(
        "log_date", ascending=False
    )

    if completed.empty:
        st.info("No completed work was logged in this period.")
        return

    for day, group in completed.groupby(completed["log_date"].dt.date, sort=False):
        st.markdown(f"**{day.strftime('%A, %b %d')}**")
        for _, row in group.iterrows():
            course = str(row.get("course", "") or "").strip()
            skill = str(row.get("skill_tag", "") or "").strip()
            meta = f"{row['goal']} · {row['hours_spent']:.1f}h"
            if course:
                meta += f" · {course}"
            if skill:
                meta += f" · {skill}"

            with st.container(border=True):
                st.markdown(f"**✓ {row['task']}**")
                st.caption(meta)
                notes = str(row.get("notes", "") or "").strip()
                if notes:
                    st.write(notes)


def render_goal_review(period_df):
    st.markdown('<div class="section-label">Progress by goal</div>', unsafe_allow_html=True)

    if period_df.empty:
        st.info("No activity to analyse yet.")
        return

    goal_summary = (
        period_df.groupby("goal")
        .agg(
            hours=("hours_spent", "sum"),
            tasks=("task", "count"),
            completed=("status", lambda s: int((s == "done").sum())),
        )
        .sort_values("hours", ascending=False)
    )

    for goal, row in goal_summary.iterrows():
        rate = round((row["completed"] / row["tasks"]) * 100) if row["tasks"] else 0
        with st.container(border=True):
            c1, c2, c3 = st.columns([4, 1, 1])
            c1.markdown(f"**{goal}**")
            c1.caption(f"{row['hours']:.1f}h invested · {int(row['tasks'])} tasks")
            c2.metric("Done", int(row["completed"]))
            c3.metric("Completion", f"{rate}%")


def render_skills_review(period_df):
    st.markdown('<div class="section-label">Skills developed</div>', unsafe_allow_html=True)

    if period_df.empty or "skill_tag" not in period_df.columns:
        st.info("No skills recorded in this period.")
        return

    skills = period_df[
        period_df["skill_tag"].fillna("").astype(str).str.strip() != ""
    ]
    if skills.empty:
        st.info("No skill tags recorded in this period.")
        return

    summary = (
        skills.groupby("skill_tag")["hours_spent"]
        .sum()
        .sort_values(ascending=False)
    )
    st.bar_chart(summary)
    st.caption("These are skills you can now point to with actual practice evidence.")


def render_career_review(start, end):
    """Show job-search activity in the same review window."""
    applications = get_all_applications()
    if not applications:
        return

    apps = pd.DataFrame(applications)
    apps["date_applied"] = pd.to_datetime(apps["date_applied"], errors="coerce").dt.date
    apps = apps[(apps["date_applied"] >= start) & (apps["date_applied"] <= end)]

    if apps.empty:
        return

    st.markdown('<div class="section-label">Career progress</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Applications", len(apps))
    c2.metric("Interviews", int((apps["status"] == "interview").sum()))
    c3.metric("Offers", int((apps["status"] == "offer").sum()))

    for _, row in apps.sort_values("date_applied", ascending=False).iterrows():
        st.markdown(
            f"- **{row['role']}** at **{row['company']}** — {row['status'].replace('_', ' ').title()}"
        )


def render_daily_calendar_review():
    """Compare today's calendar plan with today's logged work."""
    ical_url = st.secrets.get("gcal_ical_url", "")
    if not ical_url:
        return

    try:
        events = fetch_today_events(ical_url)
    except Exception as exc:
        st.warning(f"Calendar review unavailable: {exc}")
        return

    st.markdown('<div class="section-label">Calendar plan vs reality</div>', unsafe_allow_html=True)

    if not events:
        st.info("No scheduled focus blocks found on today's calendar.")
        return

    today = date.today()
    df = safe_df(get_all_entries())
    today_df = df[df["log_date"].dt.date == today] if not df.empty else pd.DataFrame()

    completed_count = 0
    for event in events:
        title = str(event.get("title", "")).strip().lower()
        goal = str(event.get("goal", "")).strip().lower()
        match = pd.DataFrame()

        if not today_df.empty:
            match = today_df[
                (today_df["task"].astype(str).str.lower() == title)
                & (today_df["goal"].astype(str).str.lower() == goal)
            ]

        if not match.empty:
            latest = match.sort_values("log_date").iloc[-1]
            if latest["status"] == "done":
                state = "Completed"
                completed_count += 1
            elif latest["status"] == "in_progress":
                state = "In progress"
            else:
                state = "Skipped"
        else:
            state = "Not logged"

        st.markdown(
            f"- **{event['title']}** · {event.get('hours', 0)}h planned — {state}"
        )

    adherence = round((completed_count / len(events)) * 100) if events else 0
    st.metric("Today's calendar adherence", f"{adherence}%")
    st.caption("Calendar adherence is available for today. Historical planned-vs-actual tracking requires saving calendar blocks to the database.")


def reviews_page():
    st.title("Reviews")
    st.caption("Look back, measure what happened, and decide what to do next.")

    entries = get_all_entries()
    if not entries:
        st.info("Start logging your work. Your daily, weekly and monthly history will build automatically here.")
        return

    df = safe_df(entries)

    period = st.radio(
        "Review period",
        ["Today", "This week", "This month", "Custom range"],
        horizontal=True,
    )

    start, end, label = review_period(period)

    if period == "Custom range":
        c1, c2 = st.columns(2)
        start = c1.date_input("From", value=date.today() - timedelta(days=7))
        end = c2.date_input("To", value=date.today())
        if start > end:
            st.error("The 'From' date must be before the 'To' date.")
            return
        label = f"{start.strftime('%b %d, %Y')} – {end.strftime('%b %d, %Y')}"

    period_df = df[
        (df["log_date"].dt.date >= start)
        & (df["log_date"].dt.date <= end)
    ].copy()

    st.caption(label)

    metrics = review_metrics(period_df, start, end)

    # The four questions the review must answer.
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Focus time", f"{metrics['hours']:.1f}h")
    c2.metric("Completed", metrics["done"])
    c3.metric("Completion", f"{metrics['completion']}%")
    c4.metric("Active days", metrics["active_days"])

    # DAILY REVIEW
    if period == "Today":
        render_daily_calendar_review()

    render_completed_work(period_df)
    render_goal_review(period_df)
    render_skills_review(period_df)
    render_career_review(start, end)

    # What did NOT happen is just as important as what did.
    st.markdown('<div class="section-label">What got in the way?</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric("Still in progress", metrics["in_progress"])
    c2.metric("Skipped", metrics["skipped"])

    if metrics["skipped"] or metrics["in_progress"]:
        st.warning(
            "There are unfinished or skipped items. Review them before starting the next planning cycle."
        )
        unfinished = period_df[period_df["status"] != "done"].sort_values(
            "log_date", ascending=False
        )
        for _, row in unfinished.iterrows():
            st.markdown(
                f"- {status_pill(row['status'])} **{row['task']}** · {row['goal']} · {row['log_date'].strftime('%b %d')}"
                , unsafe_allow_html=True,
            )

    # Weekly reflection remains persistent because the existing database has
    # a reflections table keyed by Monday's date.
    if period == "This week":
        st.markdown('<div class="section-label">Weekly reflection</div>', unsafe_allow_html=True)
        week_key = start.isoformat()
        existing = get_reflection(week_key) or ""
        reflection = st.text_area(
            "What should you continue, stop, or change next week?",
            value=existing,
            placeholder="Be specific. Example: Move DataCamp to 9am because I repeatedly lose the afternoon slot.",
            key=f"review_reflection_{week_key}",
        )
        if st.button("Save weekly reflection", type="primary"):
            if reflection.strip():
                save_reflection(week_key, reflection.strip())
                st.success("Weekly reflection saved.")
                st.rerun()
            else:
                st.error("Write a reflection before saving.")

    # Monthly review closes the loop against the annual objective.
    if period == "This month":
        st.markdown('<div class="section-label">Annual goal check</div>', unsafe_allow_html=True)
        stats = goal_stats(df)
        if stats:
            for g, hours, percent, method in stats:
                if percent is not None:
                    st.markdown(f"**{g['name']}** — {percent}% complete")
                    st.progress(max(0, min(percent, 100)) / 100)
                    st.caption(f"{hours:.1f}h logged overall")
        else:
            st.info("Create annual goals to see your year-to-date progress here.")

    # Trend is intentionally at the bottom: review first, chart second.
    st.markdown('<div class="section-label">Activity trend</div>', unsafe_allow_html=True)
    if not df.empty:
        daily = df.groupby(df["log_date"].dt.date)["hours_spent"].sum()
        st.line_chart(daily)

    if period in ["This week", "This month"]:
        past = [r for r in get_all_reflections() if r["week_start"] != start.isoformat()]
        if past and period == "This week":
            with st.expander("Past weekly reflections"):
                for r in past:
                    label = date.fromisoformat(r["week_start"]).strftime("Week of %b %d, %Y")
                    st.markdown(f"**{label}**")
                    st.caption(r["reflection_text"])


# ---------------------------------------------------------------------
# NAVIGATION
# ---------------------------------------------------------------------

pages = {
    "PLAN": [
        st.Page(home_page, title="Today", icon=":material/today:", default=True),
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
        st.Page(reviews_page, title="Reviews", icon=":material/insights:"),
    ],
}

pg = st.navigation(pages, position="sidebar", expanded=True)
pg.run()
