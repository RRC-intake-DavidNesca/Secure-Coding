# Campus Club Portal (Intentionally Insecure Practice App)

This is a **small Flask + SQLite web app** for a secure-coding audit assignment. It is deliberately written with weaknesses so you can document findings, run tools, apply fixes in stages, and compare behavior before and after changes.

## Audit baseline

Treat the current application as the **vulnerable baseline** for the project: commit history should show the insecure version first, then remediation work in later commits or branches. Do not start changing security behavior until you have captured baseline evidence (manual checks, screenshots, scanner output) as required by the assignment.

## Features

- User registration and login
- Public club announcements
- Private notes for logged-in users
- Search
- Admin page
- Debug page
- Downloadable database backup route

## Prerequisites

- Python 3.x available on your PATH
- A terminal in the project root (the folder that contains `app.py`)

## Local setup

```bash
python -m venv .venv
```

Activate the virtual environment:

- **Windows (Command Prompt):** `.venv\Scripts\activate.bat`
- **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
- **macOS / Linux:** `source .venv/bin/activate`

Then install dependencies and run the app:

```bash
pip install -r requirements.txt
python app.py
```

Open the app in a browser:

```text
http://127.0.0.1:5000
```

### Optional environment variables

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Signing key for sessions and CSRF tokens. If unset, a random key is generated each time the process starts (sessions reset on restart). |
| `FLASK_DEBUG` | Set to `1` or `true` to enable Flask’s debug mode and interactive debugger (do not use on a public server). Default is off. |
| `FLASK_RUN_HOST` | Bind address (default `127.0.0.1`). |
| `FLASK_RUN_PORT` | Port (default `5000`). |
| `SESSION_COOKIE_SECURE` | Set to `true` when serving the app only over HTTPS so browsers send the session cookie on secure connections only. |

## Database reset

If you need a clean database with the seeded demo users again, visit (local use only):

```text
http://127.0.0.1:5000/init-db?reset=1
```

This deletes the existing `campus_club.db` file when `reset=1` and recreates tables and seed data. The database file is listed in `.gitignore` and should not be committed.

If you already have a local database from an older version of the app (for example before passwords were stored as hashes), run a reset once so the seeded demo accounts match the current code.

## Demo accounts

| Username | Password   |
|----------|------------|
| `admin`  | `admin123` |
| `alice`  | `password123` |
| `bob`    | `qwerty`   |

## Evidence and reporting

Use the `evidence/` folder for screenshots and tool exports that support your audit report and appendix. See `evidence/README.md` for the suggested layout.

## Suggested workflow

1. Keep the vulnerable baseline in version control; push to your GitHub repository.
2. Invite a collaborator and complete the peer review requirements when the course schedule calls for it.
3. Confirm the included GitHub Action (Bandit) runs on push and pull requests; save representative run output or screenshots for the appendix.
4. Run at least one dedicated scanner locally (for example Semgrep or OWASP ZAP) and retain the output.
5. Write the audit report (OWASP mapping, risk levels, fix order, mitigation plan) and submit the **PDF** as instructed in the course shell.

## Tools referenced in the course

- **GitHub Actions:** Bandit (workflow under `.github/workflows/`)
- **Dedicated scans:** Semgrep, OWASP ZAP, or other tools your instructor accepts
- **Manual checks:** Browser and code review on GitHub

## Important

This project is for **local classroom use only**. Do not deploy it publicly in its current form.
