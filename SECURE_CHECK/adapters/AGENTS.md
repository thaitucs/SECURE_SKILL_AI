# AGENTS.md - SECURE_CHECK

<!--
Use with: OpenAI Codex, Gemini CLI (rename/copy to GEMINI.md), Jules, Aider, OpenCode,
Zed, Windsurf, Cline, Roo, Amp, and any agent that reads AGENTS.md.
Place at the root of the project you want to check, and keep the SECURE_CHECK folder
reachable (default path below). Merge into an existing AGENTS.md instead of overwriting.
-->

## Security check & restructuring (SECURE_CHECK)

When the user asks to check security, audit the project, find leaked keys, decide what
belongs in frontend vs backend, clean up / reorganize the project, split code, score
security, or protect displayed emails/phone numbers from spam:

1. Read `SECURE_CHECK/SKILL.md` (adjust the path if the folder lives elsewhere, e.g.
   `tools/SECURE_CHECK/SKILL.md` or `~/.skills/SECURE_CHECK/SKILL.md`).
2. Follow its workflow exactly. Load files from `SECURE_CHECK/workflow/` and
   `SECURE_CHECK/references/` only when the workflow tells you to.
3. Default mode is PLAN: read-only, write reports to `secure-check-report/`, produce
   `secure-check-report/SECURE_CHECK_PLAN.txt`, then STOP and wait for the user's approval
   (`APPROVE FIX-01 ...`).
4. Never change, move or delete project files before approval. Never print full secrets.
   Never hard-delete - use `_quarantine/`. Never push or deploy.

Optional helper scripts (Python 3 standard library only):
`python SECURE_CHECK/scripts/run_all.py . --out secure-check-report/raw`
