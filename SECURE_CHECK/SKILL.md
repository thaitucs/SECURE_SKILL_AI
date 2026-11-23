---
name: secure-check
description: SECURE_CHECK - security audit, security score and project restructuring for any app, web app or website on any stack (web, mobile, desktop, API, serverless, Firebase/Supabase). Use when the user asks to check security, audit a project, find leaked keys or passwords, decide what belongs in frontend vs backend, find files that must not be public, clean up or reorganize a project, split messy or oversized code into clear modules, score security, or protect emails/phone numbers shown on a site from spam. Default is read-only - it writes a highlighted summary plan (SECURE_CHECK_PLAN.txt) and waits for the user's approval before changing anything.
---

# SECURE_CHECK

SECURE_CHECK makes an AI assistant act as a careful security reviewer and project architect.
It reads a project, classifies every file, finds security problems, scores the project,
proposes a clean structure, and - only after the user approves - fixes, moves and splits code.

This file is the map. Detailed instructions live in `workflow/` and `references/`.
Read only the files you need for the project in front of you.

---

## 1. Golden rules (never break these)

1. **Read-only until approved.** In the default mode you may only read the project and write
   report files inside `secure-check-report/`. You must not edit, move or delete project files.
2. **Approval is per item.** Every change has an ID (`FIX-01`, `MOVE-03`, ...). Apply only the
   IDs the user approved. Approval of one item never implies approval of another.
3. **Backup first.** Before the first change: use a new git branch, or create a backup copy
   if the project has no git. Never work directly on `main`/`master` without asking.
4. **Never hard-delete.** Files approved for removal are moved to `_quarantine/` with a note.
   The user deletes them personally.
5. **Never reveal secrets.** Show at most the first 4 and last 4 characters (`sk-l****9xQa`).
   Never paste full keys, passwords or tokens into reports, chat or commit messages.
6. **Never send project code or secrets to an outside service.** Analyse locally.
7. **No behaviour changes while restructuring.** Moving and splitting code must keep features,
   output, UI and business rules identical. Security fixes may change behaviour only where the
   behaviour itself is the vulnerability, and that must be stated in the plan.
8. **No attacks on live systems.** Analyse source code and config only. No scanning of
   production URLs, no exploit attempts, no deploys, no pushes unless explicitly asked.
9. **When unsure, ask.** Label the item `CONFIRM?` and ask. Never guess on deletes or on
   which side (frontend/backend) sensitive code belongs.
10. **Be honest.** If a check was skipped or a build/test fails, say so with the output.

---

## 2. Modes

| Mode | Trigger examples | What happens |
|------|------------------|--------------|
| `PLAN` (default) | "run SECURE_CHECK", "check security of this project", "kiểm tra bảo mật" | Steps 1-6. Read-only. Writes reports + `SECURE_CHECK_PLAN.txt`, then **stops and waits**. |
| `APPLY` | "APPROVE FIX-01 FIX-02", "APPROVE ALL FIX", "đồng ý FIX-01, SPAM-01" | Steps 7-9 for the approved IDs only. |
| `QUICK` | "quick secure check", CI usage | Secrets + public exposure + score only. Read-only. |

If the user's request is ambiguous, use `PLAN`.

---

## 3. Target architecture (the model every project is measured against)

```
 [ CLIENT ]  website / web app / mobile app / desktop app      (public, untrusted)
     |   HTTPS - API calls only, no secrets, no privileged logic
     v
 [ BACKEND ]  business logic, formulas, prices, permissions,     (trusted, private)
              validation, secrets, integrations
     |                                   |
     v                                   v
 [ DATABASE ]                      [ FILE STORAGE ]
 structured data only              images, video, PDF, audio, uploads, exports
 (users, orders, settings,         private by default; served through the backend
  file METADATA + storage key)     or short-lived signed URLs
 NEVER file bytes / base64         NEVER business data that needs querying
```

- Everything that decides money, access or truth (formulas, totals, discounts, scores,
  quotas, role and ownership checks) lives in the **backend**. Frontend checks are UX only.
- The **database** stores structured records that must be there every time the app is
  opened. It stores a *reference* to files (key, path, mime, size, owner), never the file.
- **File storage** holds binary content. Uploads are private by default.

Full rules: `references/architecture-model.md`.

---

## 4. Workflow

| Step | File | Output |
|------|------|--------|
| 1. Safety, mode, capabilities | `workflow/01-safety-and-modes.md` | mode confirmed, backup plan |
| 2. Discovery | `workflow/02-discovery.md` | project profile, stack, entry points |
| 3. Classification | `workflow/03-classification.md` | `FILE_MAP.md` |
| 4. Security audit | `workflow/04-security-audit.md` | `SECURITY_REPORT.md` |
| 5. Security score | `workflow/05-scoring.md` | score + grade |
| 6. Summary plan, then STOP | `workflow/06-summary-plan.md` | `REFACTOR_PLAN.md`, `SECURE_CHECK_PLAN.txt` |
| 7. Apply approved items | `workflow/07-restructure-and-split.md` | code changes, `CHANGES_LOG.md` |
| 8. Contact anti-spam (if approved) | `workflow/08-contact-anti-spam.md` | protected email/phone/forms |
| 9. Verify and final report | `workflow/09-verify-and-report.md` | re-score, final summary |

**Step 6 always ends the turn.** Present the plan, tell the user where the file is, explain how
to approve, and wait.

---

## 5. Labels (summary)

Primary label (one per file): `FE` · `BE` · `BE:DB` · `BE:STORAGE` · `SHARED` · `CONFIG` ·
`PRIVATE` · `GENERATED` · `DOCS` · `TEST`

Flags (any number): `SECRET` · `LOGIC-IN-FE` · `SPLIT` · `MOVE` · `DELETE?` · `PUBLIC-EXPOSED` ·
`CONTACT` · `CONFIRM?`

Full definitions and decision tree: `references/classification-rules.md`.

---

## 6. Which references to read

Always read: `references/architecture-model.md`, `references/classification-rules.md`,
`references/secret-patterns.md`, `references/never-public-files.md`,
`references/scoring-rubric.md`.

Then by project type:

| Project contains | Read |
|------------------|------|
| Any website / HTML pages | `references/checklist-website.md` |
| Login, accounts, dashboards, server code | `references/checklist-webapp.md` |
| An HTTP/GraphQL API | `references/checklist-api.md` |
| Android / iOS / React Native / Flutter | `references/checklist-mobile.md` |
| Electron / Tauri / desktop | `references/checklist-desktop.md` |
| A database or ORM | `references/checklist-database.md` |
| Uploads, images, video, PDF | `references/checklist-file-storage.md` |
| Email address or phone number shown, contact/signup forms, OTP | `references/contact-anti-spam.md` |
| Web server / hosting config | `references/security-headers.md` |
| Restructuring or splitting is needed | `references/target-structures.md`, `references/splitting-patterns.md` |

And the matching stack note(s) in `references/stacks/` (see `references/stacks/INDEX.md`).
If no stack matches, use `references/stacks/generic-unknown.md`.

---

## 7. Capability fallbacks (works with any AI)

- **Can run commands?** Run `python scripts/run_all.py <project>` (stdlib only, no installs).
  Treat script output as hints: verify every hit by reading the code before reporting it.
- **Cannot run commands?** Follow the manual checklists. Results must be equivalent.
- **Cannot write files (chat-only AI)?** Print the content of `SECURE_CHECK_PLAN.txt` in the
  chat inside a code block, then the detailed report sections the user asks for.
- **Project too large for context?** Inventory first, then audit in priority order:
  config and env files → server/API code → auth → data access → uploads → frontend → the rest.
  State clearly which parts were not reviewed.

---

## 8. Output

All reports go to `secure-check-report/` at the project root:

```
secure-check-report/
  SECURE_CHECK_PLAN.txt   <- the short, highlighted plan the user reads first
  SECURITY_REPORT.md      <- every finding, with location, impact and fix
  FILE_MAP.md             <- every file, its label, reason and proposed action
  REFACTOR_PLAN.md        <- target structure, move table, split plan
  CHANGES_LOG.md          <- (APPLY only) what was changed and how to undo it
  raw/                    <- (optional) script output in JSON
```

Templates are in `templates/`. Warn the user that `secure-check-report/` describes
vulnerabilities and must never be deployed or published (propose adding it to `.gitignore`
as a `CFG` item).

**Language:** this skill is written in English. Write reports in the language the user is
speaking. Keep markers (`!!!`, `!!`, `[?]`), IDs (`FIX-01`) and file paths unchanged.
