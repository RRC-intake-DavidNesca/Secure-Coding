# Campus Club Portal (Intentionally Insecure Practice App)

This is a **small Flask + SQLite web app** for a secure-coding audit assignment. It is deliberately written with weaknesses so you can document findings, run tools, apply fixes in stages, and compare behavior before and after changes.

## Features

- User registration and login
- Public club announcements
- Private notes for logged-in users
- Search
- Admin page
- Debug page
- Downloadable database backup rout

```
http://127.0.0.1:5000
```

## Demo accounts

| Username | Password   |
|----------|------------|
| `admin`  | `admin123` |
| `alice`  | `password123` |
| `bob`    | `qwerty`   |


## Tools referenced from the course

- **GitHub Actions:** Bandit (workflow under `.github/workflows/`)
- **Dedicated scans:** Semgrep, OWASP ZAP, or other tools your instructor accepts
- **Manual checks:** Browser and code review on GitHub
