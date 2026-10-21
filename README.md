# jb-derm-clin-sched

Generates `jb-events.ics` by fetching the public ICS for dermedteam@gmail.com and filtering events that contain "(JB)" (case-insensitive). The file is published via GitHub Pages.

Features
- Filters SUMMARY or DESCRIPTION for "(JB)" (case-insensitive)
- Preserves UID, DTSTART, DTEND, DESCRIPTION, LOCATION, and other VEVENT properties
- Scheduled run via GitHub Actions (every 15 minutes) and manual trigger
- Publishes jb-events.ics on the gh-pages branch for GitHub Pages

Quickstart
1. Create a new repository on GitHub named `jb-derm-clin-sched` (Public).
2. Locally, create the project folder and paste these files with the structure:
   - .github/workflows/update-jb-events.yml
   - src/fetch_jb_ics.py
   - requirements.txt
   - index.html (optional)
   - README.md
3. From the project root run:
   ```bash
   git init
   git branch -m main
   git add .
   git commit -m "Initial commit — jb-events exporter"
   git remote add origin https://github.com/<your-github-user>/jb-derm-clin-sched.git
   git push -u origin main