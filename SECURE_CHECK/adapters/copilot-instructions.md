<!--
GitHub Copilot (VS Code / JetBrains / github.com): save as .github/copilot-instructions.md
in your project, or merge into the existing file. Keep the SECURE_CHECK folder in the
project (e.g. tools/SECURE_CHECK) and fix the path below.
-->

# SECURE_CHECK instructions

When asked to check security, audit, find leaked secrets, sort files into frontend/backend,
reorganize the project, split code, score security, or reduce spam from displayed emails or
phone numbers, follow `tools/SECURE_CHECK/SKILL.md` step by step (open the referenced
`workflow/` and `references/` files as needed).

Rules:
1. Default is read-only PLAN mode. Produce `secure-check-report/SECURE_CHECK_PLAN.txt` (short,
   highlighted with `!!!`, `!!`, `!`, `[?]`, `[YOU]`) plus the detailed `.md` reports, then
   stop and ask for approval.
2. Apply only the item IDs the user approves. Branch/backup first. No hard deletes - move to
   `_quarantine/`.
3. Never output complete secrets; mask them.
4. Business logic, formulas and permission checks belong in the backend. The database stores
   structured data only; images/video/PDF go to file storage, with metadata in the database.
5. Code splitting must not change behaviour.
6. Generated files (`secure-check-report/`, `_quarantine/`, backups) are local-only: each folder
   gets a `.gitignore` containing `*`, is added to `.git/info/exclude`, and is never staged,
   committed or pushed.
