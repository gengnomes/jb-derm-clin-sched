# JB calendar publisher

This project fetches the public ICS feed for `dermedteam@gmail.com`, keeps
events whose summary or description contains `(JB)` (case-insensitive), and
publishes the resulting `jb-events.ics` file to the `gh-pages` branch.

## Published feed

The GitHub Actions workflow runs every 15 minutes and can also be started
manually from the **Actions** tab. It tests the filter, fetches the source
calendar, and publishes `jb-events.ics` and `index.html`. A failed fetch,
test, or publish fails the workflow rather than publishing a stale or
incomplete result.

To enable the published page:

1. In repository **Settings → Pages**, choose **Deploy from a branch**.
2. Select the `gh-pages` branch and `/ (root)` as the folder.
3. In **Settings → Actions → General → Workflow permissions**, allow the
   workflow to have read and write permissions. The workflow's job requests
   `contents: write` so it can update the publishing branch.
4. Run **Update JB events ICS** manually once and confirm the run succeeds.

The Pages URL will be shown in repository **Settings → Pages**. The feed is
available at `<Pages URL>/jb-events.ics`.

## Local development

Python 3.11 or later is recommended.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python src/fetch_jb_ics.py
```

The fetch command writes `jb-events.ics` in the current directory. It requires
network access to the public Google Calendar ICS endpoint.
