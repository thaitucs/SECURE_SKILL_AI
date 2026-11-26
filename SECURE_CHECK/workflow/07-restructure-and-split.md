# Step 7 - Apply approved items (fixes, moves, splits, quarantine)

**Goal:** apply exactly the approved items, safely, one group at a time, keeping the app
working.

## 7.1 Before the first change

1. Re-read the approved IDs. List them back to the user in one line.
2. Create the branch / backup (step 1.3). If not possible, stop and ask.
   Make sure the backup copy is outside the project and outside any repo (step 1.5).
3. Record the baseline: does the project build/test **before** changes? Save the output.
   If it already fails, tell the user - later failures must be compared with this baseline.

## 7.2 Order of execution

1. `FIX-*` Critical, then High - security first.
2. `CFG-*` - `.gitignore`, `.env.example`, headers, debug flags, CORS.
3. `MOVE-*` - files to the right layer/folder.
4. `SPLIT-*` - one file at a time.
5. `DEL-*` - move to `_quarantine/`.
6. `SPAM-*` - see `workflow/08-contact-anti-spam.md`.
7. Remaining `FIX-*` (Medium/Low).

After **each group** (and after each SPLIT): build / run tests / start the app if possible.
If it breaks and you cannot fix it quickly within the scope of the item, revert that item and
report it.

## 7.3 Moving secrets out of code (typical FIX)

1. Create/extend the backend env loading (`config/`), validate required variables at start.
2. Replace the literal with `process.env.X` / `os.environ["X"]` / `env('X')` etc. on the
   **backend**.
3. Add `X=` (empty or placeholder) to `.env.example`. Never write the real value there.
4. Make sure `.env*` (except `.env.example`) is in `.gitignore`.
5. If the secret was used in the frontend: create a backend endpoint that does the privileged
   action and call it from the frontend.
6. Do **not** write the real secret into a new `.env` unless the user asked; tell them which
   variables to fill.
7. Add a `YOU-` reminder: rotate the old key - it is compromised.

## 7.4 Moving logic to the backend (LOGIC-IN-FE)

1. Copy the calculation/permission logic into a backend `services/` (logic) or `policies/`
   (permission) module. Same inputs, same outputs.
2. The backend loads authoritative data itself (e.g. product price from DB), never trusts
   price/role/total sent by the client.
3. The frontend calls the endpoint. It may keep a *display-only* preview if the plan said so.
4. Add/adjust a test if a test framework exists.

## 7.5 Moving files (MOVE)

1. Use `git mv` when in git (keeps history).
2. Update **every** import/require/include path. Search the whole project for the old path
   and the old module name, including dynamic imports, config files, tests, docs, CI.
3. Respect path aliases (`@/`, `~/`, `tsconfig paths`, webpack/vite aliases).
4. Framework convention files (routes by filename) must keep the name/location the framework
   needs - move logic out of them instead of moving them.

## 7.6 Splitting (SPLIT)

Follow `references/splitting-patterns.md`. Core rules:

- No fixed line limit. Split by **responsibility**: each new file has one clear job and a name
  that says it.
- Keep the public API: the original module re-exports the new parts (or an `index` barrel)
  so existing imports keep working, unless the plan said to update all imports.
- Move code verbatim first, then adjust imports. No "improvements" in the same step.
- Keep comments and license headers with the code they belong to.
- One file per step → build/test → next.

## 7.7 Quarantine (DEL)

```
_quarantine/
  .gitignore                 <- "*" : the folder is LOCAL-ONLY (step 1.5), never committed
  README.txt                 <- list: original path, reason, date, item ID, how to restore
  <original/relative/path>   <- same relative path as before
```

- Create `_quarantine/.gitignore` (same content as in step 1.5) **before** moving anything in,
  and check `/_quarantine/` is in `.git/info/exclude`.
- Move with a normal file move, **not** `git mv` - `git mv` would track the quarantined copy
  and it would be pushed. Git then records only the removal of the original path; the copy
  stays on disk, untracked and ignored.
- Restore: move the file back to its original path (it is tracked again as before), or
  `git checkout <commit-before-change> -- <path>`. Write the restore command for each file in
  `README.txt` and the log.
- Make sure `_quarantine/` is also excluded from deploy/build (note this in the log).
- Files that must not be public but are still needed (e.g. a DB dump the user wants to keep)
  go outside the deploy folder, not into quarantine - follow the item's wording.

## 7.8 Log everything - `CHANGES_LOG.md`

For each item: ID · what changed · files · verification result · how to undo.
Template: `templates/CHANGES_LOG.md`.

## Exit criteria

All approved items applied or explicitly reported as not applied (with reason) · build/test
status compared with baseline · log written.
