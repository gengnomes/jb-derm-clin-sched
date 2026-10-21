#!/usr/bin/env python3
"""
fetch_jb_ics.py
Fetch public Google Calendar ICS, filter events containing "(JB)" (case-insensitive),
and write jb-events.ics preserving UID, DTSTART, DTEND, SUMMARY, DESCRIPTION, LOCATION.
"""

import re
import sys
from datetime import datetime
import requests
from icalendar import Calendar, Event

# CONFIG
CALENDAR_ID = "dermedteam@gmail.com"
ICS_URL = f"https://calendar.google.com/calendar/ical/{CALENDAR_ID}/public/basic.ics"
OUTPUT_ICS = "jb-events.ics"
TOKEN_PATTERN = re.compile(r"$jb$", re.IGNORECASE)

def fetch_ics(url):
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text

def filter_calendar(ics_text):
    cal = Calendar.from_ical(ics_text)
    new_cal = Calendar()
    # copy top-level properties (preserve common metadata where present)
    for k, v in cal.items():
        new_cal.add(k, v)
    # ensure PRODID & VERSION exist
    if "PRODID" not in new_cal:
        new_cal.add('PRODID', '-//jb-events-generator//github.com//')
    if "VERSION" not in new_cal:
        new_cal.add('VERSION', '2.0')

    count = 0
    for component in cal.walk():
        if component.name == "VEVENT":
            summary = str(component.get('SUMMARY', ''))
            description = str(component.get('DESCRIPTION', ''))
            text_to_search = summary + "\n" + description
            if TOKEN_PATTERN.search(text_to_search):
                # preserve properties from original VEVENT
                ev = Event()
                for prop, val in component.items():
                    ev.add(prop, val)
                new_cal.add_component(ev)
                count += 1
    return new_cal, count

def main():
    try:
        print(f"Fetching ICS from {ICS_URL}")
        ics_text = fetch_ics(ICS_URL)
    except Exception as e:
        print("Failed to fetch calendar ICS:", e, file=sys.stderr)
        sys.exit(2)

    try:
        new_cal, count = filter_calendar(ics_text)
    except Exception as e:
        print("Failed to parse or filter ICS:", e, file=sys.stderr)
        sys.exit(3)

    with open(OUTPUT_ICS, "wb") as f:
        f.write(new_cal.to_ical())

    print(f"Wrote {OUTPUT_ICS} with {count} events.")

if __name__ == "__main__":
    main()