# Evidence

Store audit materials here so they stay next to the code and are easy to zip or reference in the report appendix.

| Folder | Use |
|--------|-----|
| `baseline/` | Screenshots and notes from the vulnerable app **before** fixes (routes, inputs, outcomes). |
| `tools/` | Exports from scanners (for example Bandit logs from CI, Semgrep output, OWASP ZAP HTML/PDF). |
| `peer-review/` | Links, PR numbers, and screenshots of review comments or merged PR pages. |
| `post-fix/` | After each fix group: retest notes, updated screenshots, and scan outputs for comparison. |

Keep filenames descriptive (for example `baseline-admin-unauthenticated.png`). The database file `campus_club.db` stays out of version control via `.gitignore`; capture behavior with screenshots instead of committing the DB.
