import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from icalendar import Calendar, Event

from src.fetch_jb_ics import filter_calendar, generate_site


def make_event(summary, description=""):
    event = Event()
    event.add("uid", f"{summary}@example.test")
    event.add("dtstart", datetime(2026, 10, 21, 9, tzinfo=timezone.utc))
    event.add("dtend", datetime(2026, 10, 21, 10, tzinfo=timezone.utc))
    event.add("summary", summary)
    event.add("description", description)
    event.add("location", "Clinic")
    return event


def make_calendar(*events):
    calendar = Calendar()
    calendar.add("prodid", "-//test//EN")
    calendar.add("version", "2.0")
    for event in events:
        calendar.add_component(event)
    return calendar.to_ical().decode()


class FilterCalendarTests(unittest.TestCase):
    def test_filters_case_insensitive_identifier_in_summary_or_description(self):
        ics_text = make_calendar(
            make_event("Clinic (JB)"),
            make_event("Clinic", "Coverage for (jb)"),
            make_event("Clinic (AB)"),
        )

        filtered, count = filter_calendar(ics_text, "JB")

        events = filtered.walk("VEVENT")
        self.assertEqual(count, 2)
        self.assertEqual(len(events), 2)
        self.assertEqual(
            {str(event["SUMMARY"]) for event in events},
            {"Clinic (JB)", "Clinic"},
        )

    def test_preserves_calendar_metadata_and_event_properties(self):
        filtered, _ = filter_calendar(
            make_calendar(make_event("Clinic (JB)")), "JB"
        )
        event = filtered.walk("VEVENT")[0]

        self.assertEqual(str(filtered["PRODID"]), "-//test//EN")
        self.assertEqual(str(event["UID"]), "Clinic (JB)@example.test")
        self.assertEqual(str(event["LOCATION"]), "Clinic")
        self.assertEqual(str(event["DESCRIPTION"]), "")

    def test_adds_required_calendar_metadata_when_missing(self):
        filtered, count = filter_calendar(
            "BEGIN:VCALENDAR\r\nEND:VCALENDAR\r\n", "JB"
        )

        self.assertEqual(count, 0)
        self.assertIn("PRODID", filtered)
        self.assertEqual(str(filtered["VERSION"]), "2.0")

    def test_generates_feed_and_page_for_each_unique_identifier(self):
        ics_text = make_calendar(
            make_event("Clinic (JB)"),
            make_event("Clinic (AB)"),
            make_event("Clinic", "Also covers (jb)"),
        )
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)

            identifiers = generate_site(ics_text, output_dir)

            self.assertEqual(identifiers, ["AB", "JB"])
            self.assertTrue((output_dir / "ab-events.ics").exists())
            self.assertTrue((output_dir / "jb-events.ics").exists())
            self.assertTrue((output_dir / "ab/index.html").exists())
            self.assertTrue((output_dir / "jb/index.html").exists())
            self.assertIn("ab/", (output_dir / "index.html").read_text())
            self.assertEqual(
                len(Calendar.from_ical((output_dir / "jb-events.ics").read_bytes()).walk("VEVENT")),
                2,
            )


if __name__ == "__main__":
    unittest.main()
