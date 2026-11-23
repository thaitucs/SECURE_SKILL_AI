# Step 3 - Classification

**Goal:** every file gets one primary label, optional flags, a reason and a proposed action.

Read `references/classification-rules.md` first. Use `scripts/inventory.py` output as a
starting guess only; confirm by reading the file.

## 3.1 Procedure

For each file (skip ignored folders from step 1):

1. Read imports/requires, environment variable usage, framework directives
   (`'use client'`, `'use server'`, `import 'server-only'`), and location (is it inside a
   public/deployable folder?).
2. Assign the **primary label** with the decision tree.
3. Add **flags** for everything that applies.
4. Write a one-line **reason** that cites evidence ("imports `mysql2`, reads
   `process.env.DB_PASSWORD`").
5. Propose an **action**: `KEEP` · `MOVE → <new path>` · `SPLIT → <parts>` ·
   `QUARANTINE` · `REMOVE FROM PUBLIC` · `MOVE SECRET TO ENV` · `CONFIRM?`.

For large projects, group identical cases ("`src/components/**` - 84 files - FE - KEEP")
and list individually only files with flags.

## 3.2 Special attention

- **`FE` + `SECRET`** → always a security finding (step 4), usually Critical.
- **`FE` + `LOGIC-IN-FE`** → finding if the backend trusts the result; otherwise a MOVE item.
- **Anything in a public folder** that is not meant for visitors → `PUBLIC-EXPOSED`.
- **`DELETE?`** requires evidence: "not imported anywhere (searched for `oldHelper`), not a
  convention file, last referenced in commented-out code". If you cannot prove it, use
  `CONFIRM?` instead.
- **`CONTACT`** → file shows an email address or phone number to visitors, or contains a
  contact/signup/OTP form. Feeds step 8.

## 3.3 Output - `FILE_MAP.md`

Use `templates/FILE_MAP.md`. Columns:

`Path | Label | Flags | Reason | Action | Item ID`

Item IDs link to the plan (`MOVE-04`, `DEL-02`, `FIX-01`). Files with `KEEP` and no flags
have no ID.

## Exit criteria

Every non-ignored file (or group) is labelled · every flag has evidence · uncertain items are
`CONFIRM?`.
