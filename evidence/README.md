# Evidence

Store audit materials here so they stay next to the code and are easy to zip or reference in the report appendix.

| Folder | Use |
|--------|-----|
| `baseline/` | Screenshots and notes from the vulnerable app **before** fixes (routes, inputs, outcomes). |
| `tools/` | Exports from scanners (for example Bandit logs from CI, Semgrep output, OWASP ZAP HTML/PDF). |
| `peer-review/` | Links, PR numbers, and screenshots of review comments or merged PR pages. |
| `post-fix/` | After each fix group: retest notes, updated screenshots, and scan outputs for comparison. |

Keep filenames descriptive (for example `baseline-admin-unauthenticated.png`). The database file `campus_club.db` stays out of version control via `.gitignore`; capture behavior with screenshots instead of committing the DB.

## Root files in this folder

- `findings-list.md` — Draft table of vulnerabilities, OWASP mapping, risk, and remediation order for the report.
- `baseline/manual-checklist.md` — Step-by-step manual tests to run before fixes; pair with screenshots in `baseline/`.
- `tools/bandit-baseline.txt` — Local Bandit run (same family of checks as `.github/workflows/security-scan.yml`). A non-zero Bandit exit code usually means findings were reported, not that the scanner failed.
- `tools/semgrep-baseline.txt` — Semgrep `--config auto` output for the dedicated tooling requirement. On Windows, if Semgrep errors on encoding, set UTF-8 for the session (for example `$env:PYTHONUTF8='1'`) and rerun.
