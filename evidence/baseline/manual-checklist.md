# Manual baseline checks

Perform these against the running app **before** remediation. Save screenshots under `evidence/baseline/` with clear names (include route and short description).

## Access control

- [ ] Open `/admin` while **logged out**. Expect: user list visible (including plaintext passwords in the table).
- [ ] Open `/download-backup` while **logged out**. Expect: `campus_club.db` downloads without login.
- [ ] Log in as `alice`, then open `/notes/3` (or another user id that is not alice’s own notes list from the dashboard). Expect: another user’s private notes visible (IDOR by `user_id`).
- [ ] Open `/debug-info` while **logged out** (and again while logged in if required for your report). Expect: secret key, database path, session data, debug flag exposed.

## XSS

- [ ] Create or use a post whose content includes HTML/JS-style input, e.g. `<img src=x onerror=alert('xss')>`. Expect: unsafe rendering on the home page (`index.html` uses `| safe` on content).
- [ ] On `/search`, use query input such as `<script>alert('xss')</script>`. Expect: reflected XSS via `term` and/or result rows (`| safe` in `search.html`).

## Injection

- [ ] On `/login`, username `' OR 1=1 -- ` with any password (local only). Expect: authentication bypass via SQL injection in the login query.
- [ ] On `/search`, try SQL-oriented or odd characters and observe errors or broad results. Expect: search built from string concatenation (document input and outcome).

## Evidence to pair with GitHub

For each major finding, keep a short code snippet reference (file + line range) from the repo for the report appendix.
