#!/usr/bin/env python3
"""Fetch a public Google Calendar and publish feeds for parenthesized initials."""

import html
import re
import sys
from pathlib import Path

import requests
from icalendar import Calendar, Event

CALENDAR_ID = "dermedteam@gmail.com"
ICS_URL = f"https://calendar.google.com/calendar/ical/{CALENDAR_ID}/public/basic.ics"
OUTPUT_DIR = Path("site")
IDENTIFIER_PATTERN = re.compile(r"\(([A-Z]{2})\)", re.IGNORECASE)


def fetch_ics(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def event_text(component):
    return "\n".join(
        str(component.get(property_name, ""))
        for property_name in ("SUMMARY", "DESCRIPTION")
    )


def extract_identifiers(calendar):
    identifiers = set()
    for component in calendar.walk("VEVENT"):
        identifiers.update(
            match.upper() for match in IDENTIFIER_PATTERN.findall(event_text(component))
        )
    return sorted(identifiers)


def filter_calendar(ics_text, identifier):
    cal = Calendar.from_ical(ics_text)
    new_cal = Calendar()
    for key, value in cal.items():
        new_cal.add(key, value)
    if "PRODID" not in new_cal:
        new_cal.add("PRODID", "-//calendar-feed-generator//github.com//")
    if "VERSION" not in new_cal:
        new_cal.add("VERSION", "2.0")

    token_pattern = re.compile(
        rf"\({re.escape(identifier)}\)", re.IGNORECASE
    )
    count = 0
    for component in cal.walk("VEVENT"):
        if token_pattern.search(event_text(component)):
            event = Event()
            for key, value in component.items():
                event.add(key, value)
            new_cal.add_component(event)
            count += 1
    return new_cal, count


def generate_site(ics_text, output_dir=OUTPUT_DIR):
    calendar = Calendar.from_ical(ics_text)
    identifiers = extract_identifiers(calendar)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    links = []
    for identifier in identifiers:
        slug = identifier.lower()
        feed_name = f"{slug}-events.ics"
        filtered, count = filter_calendar(ics_text, identifier)
        (output_dir / feed_name).write_bytes(filtered.to_ical())

        page_dir = output_dir / slug
        page_dir.mkdir(parents=True, exist_ok=True)
        title = html.escape(f"{identifier} Events")
        page = (
            "<!doctype html>\n"
            '<html lang="en">\n'
            "  <head>\n"
            '    <meta charset="utf-8">\n'
            f"    <title>{title}</title>\n"
            "  </head>\n"
            "  <body>\n"
            f"    <h1>{title}</h1>\n"
            "    <p>Copy this calendar URL and paste it into your calendar app's URL subscription option.</p>\n"
            '    <p><a id="calendar-url" href="../'
            f'{feed_name}"></a> '
            '      <button id="copy-calendar-url" type="button" aria-label="Copy calendar URL" '
            'title="Copy calendar URL">\n'
            '        <svg aria-hidden="true" viewBox="0 0 24 24" width="18" height="18" '
            'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round">\n'
            '          <rect x="8" y="8" width="13" height="13" rx="2"></rect>\n'
            '          <path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"></path>\n'
            "        </svg>\n"
            "      </button>\n"
            "      <span id=\"copy-status\" role=\"status\" aria-live=\"polite\"></span>\n"
            "    </p>\n"
            f"    <p>{count} matching events.</p>\n"
            '    <p><a href="../">All calendars</a></p>\n'
            "    <script>\n"
            "      const calendarUrl = document.getElementById('calendar-url');\n"
            "      const copyStatus = document.getElementById('copy-status');\n"
            "      calendarUrl.textContent = calendarUrl.href;\n"
            "      document.getElementById('copy-calendar-url').addEventListener('click', async () => {\n"
            "        try {\n"
            "          await navigator.clipboard.writeText(calendarUrl.href);\n"
            "          copyStatus.textContent = 'Copied.';\n"
            "        } catch {\n"
            "          copyStatus.textContent = 'Could not copy. Select and copy the URL above.';\n"
            "        }\n"
            "      });\n"
            "    </script>\n"
            "  </body>\n"
            "</html>\n"
        )
        (page_dir / "index.html").write_text(page, encoding="utf-8")
        links.append(
            f'      <li><a href="{slug}/">{html.escape(identifier)} Events</a> '
            f'(<a href="{feed_name}">ICS feed</a>)</li>'
        )
        print(f"Wrote {feed_name} with {count} events.")

    index = (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "  <head>\n"
        '    <meta charset="utf-8">\n'
        "    <title>Calendar subscriptions</title>\n"
        "  </head>\n"
        "  <body>\n"
        "    <h1>Calendar subscriptions</h1>\n"
        "    <ul>\n"
        + "\n".join(links)
        + "\n    </ul>\n"
        "  </body>\n"
        "</html>\n"
    )
    (output_dir / "index.html").write_text(index, encoding="utf-8")
    return identifiers


def main():
    try:
        print(f"Fetching ICS from {ICS_URL}")
        ics_text = fetch_ics(ICS_URL)
    except requests.RequestException as error:
        print("Failed to fetch calendar ICS:", error, file=sys.stderr)
        sys.exit(2)

    try:
        identifiers = generate_site(ics_text)
    except Exception as error:
        print("Failed to parse or publish calendar ICS:", error, file=sys.stderr)
        sys.exit(3)

    if not identifiers:
        print("No parenthesized identifiers found; published an empty index.")


if __name__ == "__main__":
    main()
