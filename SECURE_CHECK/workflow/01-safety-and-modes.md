# Step 1 - Safety, mode and capabilities

**Goal:** know what you are allowed to do before touching anything.

## 1.1 Determine the mode

- Default to `PLAN` (read-only).
- `APPLY` only when the user gives approval IDs after seeing a plan in this session, or points
  to an existing `secure-check-report/SECURE_CHECK_PLAN.txt` and approves items from it.
- `QUICK` when the user asks for a fast check or the skill runs in CI.

If the user says "fix everything" before any plan exists, run `PLAN` first and explain that
approval happens on the plan. This protects the user from surprise changes.

## 1.2 Determine your capabilities

| Capability | If yes | If no |
|------------|--------|-------|
| Read files | Normal flow | Ask the user to paste the file tree and key files (configs, env examples, server entry, auth, upload code). |
| Run commands | Use `scripts/` and project build/test commands | Manual checklists only; tell the user which verifications they must run. |
| Write files | Write reports to `secure-check-report/` | Print the plan in chat. |
| Git available | Use a branch | Backup copy (APPLY only). |

## 1.3 Backup plan (needed before APPLY, prepared during PLAN)

During `PLAN`, only check and record the situation:
- Is it a git repo? Is the working tree clean (`git status --porcelain`)?
- What is the current branch?

Before the first change in `APPLY`:
- **Git, clean tree:** `git switch -c secure-check/<yyyy-mm-dd>`.
- **Git, dirty tree:** stop and ask: commit, stash, or continue on top of the uncommitted work.
- **No git:** propose `git init` + an initial commit, or a full copy of the folder to
  `<project>_backup_<yyyy-mm-dd>/` outside the project. Wait for the answer.

Never run `git push`, `git reset --hard`, `git clean`, force operations, or history rewriting
(`filter-repo`, BFG) yourself. If history contains secrets, explain the procedure in the
plan as a "You must do" item.

## 1.4 Scope

- Ignore: `node_modules/`, `vendor/`, `.venv/`, `venv/`, `__pycache__/`, `dist/`, `build/`,
  `.next/`, `.nuxt/`, `out/`, `target/`, `bin/`, `obj/`, `Pods/`, `.gradle/`, `.dart_tool/`,
  `coverage/`, `.git/` (but **do** note if `.git/` would be deployed).
- Build output folders are ignored for code review but **checked** for leaked secrets and
  source maps when they are committed or deployed.
- Lock files are read for dependency review, not for code review.

## Exit criteria

Mode known · capabilities known · git status recorded · scope defined.
