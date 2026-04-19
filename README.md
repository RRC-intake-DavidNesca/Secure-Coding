# Campus Club Portal (Intentionally Insecure Practice App)

This is a **small Flask + SQLite web app** designed for a secure-coding class project.
It is intentionally written with security weaknesses so it can be reviewed, scanned, discussed,
and improved during a security audit.

## Features
- User registration and login
- Public club announcements
- Private notes area for logged-in users
- Search page
- Admin page
- Debug page
- Downloadable database backup route

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open the site at:
```text
http://127.0.0.1:5000
```

## Demo accounts
- `admin / admin123`
- `alice / password123`
- `bob / qwerty`

## Suggested project workflow
1. Push this project to a new GitHub repository.
2. Invite at least one classmate as a collaborator.
3. Ask them to leave meaningful code comments and open a pull request.
4. Add or run a security scanning tool.
5. Write the audit report with vulnerabilities, OWASP categories, risk, order to fix, and mitigation plan.

## Dedicated tools you can use later
- Bandit
- Semgrep
- OWASP ZAP (for the running app)
- Manual code review in GitHub

## Important
This project is for **local classroom use only**.
Do not deploy it publicly in its current form.
