# Calendar subscription publisher

This project fetches the public ICS feed for `dermedteam@gmail.com`, discovers
parenthesized two-letter identifiers such as `(JB)` in event summaries and
descriptions, and publishes one filtered ICS feed and subscription page for
each identifier. Matching is case-insensitive. Events with more than one
identifier appear in each corresponding feed; tags with other than two letters
are ignored.

## Published feeds and pages

The GitHub Actions workflow runs every 15 minutes and can also be started
manually from the **Actions** tab. It tests the filters, fetches the source
calendar, generates the pages and feeds, then publishes them to `gh-pages`.
A failed fetch, test, or publish fails the workflow rather than publishing
stale or incomplete output.

The homepage lists each discovered identifier. For example, `(JB)` produces
the page `<Pages URL>/jb/` and the feed `<Pages URL>/jb-events.ics`. Each
calendar page displays its full feed URL and provides a copy button with
instructions for adding it as a URL subscription in a calendar app.

To enable the published page:

1. In repository **Settings → Pages**, choose **Deploy from a branch**.
2. Select the `gh-pages` branch and `/ (root)` as the folder.
3. In **Settings → Actions → General → Workflow permissions**, allow the
   workflow to have read and write permissions. The workflow's job requests
   `contents: write` so it can update the publishing branch.
4. Run **Update calendar subscription feeds** manually once and confirm the
   run succeeds.

## Local development

Python 3.11 or later is recommended.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python src/fetch_jb_ics.py
```

The fetch command writes generated files to the `site/` directory. It requires
network access to the public Google Calendar ICS endpoint.
