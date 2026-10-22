import unittest
from datetime import datetime, timezone

from icalendar import Calendar, Event

from src.fetch_jb_ics import filter_calendar


def make_event(summary, description=""):
    event = Event()
    event.add("uid", f"{summary}@example.test")
    event.add("dtstart", datetime(2026, 10, 21, 9, tzinfo=timezone.utc))
    event.add("dtend", datetime(2026, 10, 21, 10, tzinfo=timezone.utc))
    event.add("summary", summary)
    event.add("description", description)
    event.add("location", "Clinic")
    return event


class FilterCalendarTests(unittest.TestCase):
    def test_filters_case_insensitive_jb_token_in_summary_or_description(self):
        calendar = Calendar()
        calendar.add("prodid", "-//test//EN")
        calendar.add("version", "2.0")
        calendar.add_component(make_event("Clinic (JB)"))
        calendar.add_component(make_event("Clinic", "Coverage for (jb)"))
        calendar.add_component(make_event("Clinic", "No matching marker"))

        filtered, count = filter_calendar(calendar.to_ical().decode())

        events = filtered.walk("VEVENT")
        self.assertEqual(count, 2)
        self.assertEqual(len(events), 2)
        self.assertEqual(
            {str(event["SUMMARY"]) for event in events},
            {"Clinic (JB)", "Clinic"},
        )

    def test_preserves_calendar_metadata_and_event_properties(self):
        calendar = Calendar()
        calendar.add("prodid", "-//test//EN")
        calendar.add("version", "2.0")
        calendar.add_component(make_event("Clinic (JB)"))

        filtered, _ = filter_calendar(calendar.to_ical().decode())
        event = filtered.walk("VEVENT")[0]

        self.assertEqual(str(filtered["PRODID"]), "-//test//EN")
        self.assertEqual(str(event["UID"]), "Clinic (JB)@example.test")
        self.assertEqual(str(event["LOCATION"]), "Clinic")
        self.assertEqual(str(event["DESCRIPTION"]), "")

    def test_adds_required_calendar_metadata_when_missing(self):
        filtered, count = filter_calendar("BEGIN:VCALENDAR\r\nEND:VCALENDAR\r\n")

        self.assertEqual(count, 0)
        self.assertIn("PRODID", filtered)
        self.assertEqual(str(filtered["VERSION"]), "2.0")


if __name__ == "__main__":
    unittest.main()
