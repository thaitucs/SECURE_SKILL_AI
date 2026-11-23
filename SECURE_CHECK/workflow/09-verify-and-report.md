# Step 9 - Verify and final report

**Goal:** prove the changes work and show the user the result.

## 9.1 Verification

1. Build: the project's build command (`npm run build`, `python manage.py check`,
   `php artisan test`, `flutter build`, `go build ./...`, `dotnet build` ...).
2. Tests / lint / type-check if they exist.
3. Re-run scanners: `python scripts/run_all.py <project> --out secure-check-report/raw`.
   Fixed secrets must no longer appear (in source **and** in a fresh build output).
4. Check imports: search for every old path of moved files - no references left.
5. Check the deploy folder: none of the `never-public-files.md` items are inside it.
6. Smoke-test key flows if you can run the app (login, main page, upload, form).

Compare with the baseline from step 7.1. A failure that existed before is "pre-existing", a
new failure must be fixed or the item reverted.

## 9.2 Re-score

Mark fixed findings `"status": "fixed"` in `findings.json`, run `score.py` again, show
**before → after**.

## 9.3 Final message to the user

- Score before → after, grade.
- Applied items (IDs), skipped/failed items with reason.
- Verification results (honest - include failures and their output).
- `[YOU]` items still open - especially key rotation and history cleanup.
- Where the log is: `secure-check-report/CHANGES_LOG.md`.
- How to undo: branch name / backup path.
- Reminder: do not deploy `secure-check-report/` or `_quarantine/`.

Do not commit or push unless the user asks. If they ask, commit per group with clear messages
(`secure-check: FIX-01 move Stripe key to backend`).
