"""
calendar_sync.py
Fetches today's events from a Google Calendar "secret iCal address" and
maps them to your tracker's goal categories, so you don't have to retype
what's already scheduled.

How to get the secret iCal URL:
    Google Calendar -> Settings -> [your calendar] -> "Integrate calendar"
    -> copy the "Secret address in iCal format" link.
This URL is private (unguessable) but still sensitive - never commit it
to GitHub. It's read from Streamlit secrets instead (see README).
"""

import requests
from icalendar import Calendar
from datetime import date, datetime
import pytz

# Maps keywords found in your calendar event titles to your tracker goals.
# Edit this if you rename events or add new recurring blocks.
GOAL_KEYWORDS = {
    "literature review": "Literature review",
    "project 1": "Project 1: Battery Life",
    "battery life": "Project 1: Battery Life",
    "python": "DataCamp Python",
    "sql": "DataCamp SQL",
    "job search": "Job search",
    "youtube": "YouTube learning",
}

# Event titles that aren't loggable tasks (planning/admin blocks) - skipped.
SKIP_TITLES = {"plan the day"}


def match_goal(event_title):
    """Return the tracker goal that best matches a calendar event title, or None."""
    title_lower = event_title.lower()
    for keyword, goal in GOAL_KEYWORDS.items():
        if keyword in title_lower:
            return goal
    return None


def fetch_today_events(ical_url, timezone_name="Africa/Nairobi"):
    """
    Fetch the calendar feed and return today's loggable events as a list of dicts:
    [{"title": ..., "goal": ..., "hours": ..., "start": ...}, ...]
    Skips all-day/admin events and anything that doesn't map to a known goal.
    """
    tz = pytz.timezone(timezone_name)
    today = datetime.now(tz).date()

    response = requests.get(ical_url, timeout=10)
    response.raise_for_status()
    cal = Calendar.from_ical(response.text)

    events = []
    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        summary = str(component.get("summary", "")).strip()
        if not summary or summary.lower() in SKIP_TITLES:
            continue

        dtstart = component.get("dtstart").dt
        dtend = component.get("dtend").dt

        # Skip all-day events (dtstart is a date, not a datetime)
        if not isinstance(dtstart, datetime):
            continue

        event_date = dtstart.astimezone(tz).date()
        if event_date != today:
            continue

        goal = match_goal(summary)
        if goal is None:
            continue  # not a task block we track (e.g. a personal appointment)

        hours = round((dtend - dtstart).total_seconds() / 3600, 2)

        events.append(
            {
                "title": summary,
                "goal": goal,
                "hours": hours,
                "start": dtstart.astimezone(tz).strftime("%H:%M"),
            }
        )

    events.sort(key=lambda e: e["start"])
    return events
