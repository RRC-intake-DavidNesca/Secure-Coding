# Security findings (baseline draft)

Use this table in your final report; adjust wording to match your screenshots and retest results. One OWASP category per row is enough if you explain the choice.

| # | Title | Affected route / file | OWASP Top 10 (2021) | Risk | Notes |
|---|--------|------------------------|---------------------|------|--------|
| 1 | SQL injection in login | `POST /login` — `app.py` | A03 Injection | Critical | Login builds SQL with string interpolation of username and password. |
| 2 | SQL injection in search | `GET /search?q=...` — `app.py`, `templates/search.html` | A03 Injection | High | Search query concatenates user input into SQL `LIKE` clauses. |
| 3 | Missing authorization on admin | `GET /admin` — `app.py`, `templates/admin.html` | A01 Broken Access Control | High | No session or role check; user list and password column exposed. |
| 4 | Unauthenticated database download | `GET /download-backup` — `app.py` | A01 Broken Access Control / A05 Security Misconfiguration | Critical | Sends SQLite file without authentication. |
| 5 | IDOR / horizontal access on notes by user | `GET /notes/<user_id>` — `app.py` | A01 Broken Access Control | High | Any logged-in user can open another user’s notes by changing `user_id`. |
| 6 | Stored and reflected XSS (unsafe rendering) | `templates/index.html`, `templates/search.html` | A03 Injection | High | `| safe` on post content and search term/results bypasses escaping. |
| 7 | Plaintext password storage and display | `users` table; `GET /admin` | A02 Cryptographic Failures | High | Passwords stored and shown in plaintext. |
| 8 | Hard-coded secret and debug exposure | `app.py`, `GET /debug-info`, `templates/debug.html` | A05 Security Misconfiguration | High | Fixed `SECRET_KEY`, session details, DB path, debug flag exposed. |
| 9 | Weak session cookies | `app.py` Flask config | A05 Security Misconfiguration / A07 Identification and Authentication Failures | Medium | `SESSION_COOKIE_HTTPONLY` and `SESSION_COOKIE_SECURE` disabled. |
| 10 | Missing CSRF protection | Forms (register, login, posts, notes, etc.) | A01 Broken Access Control | Medium | No CSRF tokens on state-changing requests. |
| 11 | Weak demo credentials and no rate limiting | Seed users; login route | A07 Identification and Authentication Failures | Medium | Predictable passwords; no lockout or throttling. |

## Suggested remediation order (for the report)

1. Lock down sensitive routes: `/admin`, `/download-backup`, `/debug-info`, and enforce ownership on `/notes/<user_id>`.
2. Replace dynamic SQL with parameterized queries on `/login` and `/search`.
3. Hash passwords (e.g. suitable KDF) and remove plaintext from UI and admin views.
4. Remove `| safe` where inappropriate; escape or sanitize output consistently.
5. Set secure session defaults; add CSRF tokens on forms.
6. Externalize secrets; disable debug leakage in production-style config.
7. Strengthen authentication policy (password rules, lockout or rate limiting) as feasible for the assignment scope.
