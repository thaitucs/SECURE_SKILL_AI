# Step 6 - Summary plan, then STOP

**Goal:** give the user one short, scannable file that tells them what is wrong, what you
propose, what they must decide - and then wait for their decision.

## 6.1 Build the action list

Turn every proposed change into an item with an ID:

| Prefix | Type | Source |
|--------|------|--------|
| `FIX-` | Security fix in code/config | findings (step 4) |
| `CFG-` | Config / `.gitignore` / headers / env example | findings + hygiene |
| `MOVE-` | Move files/code to the right layer or folder | classification (step 3) |
| `SPLIT-` | Split a file/module into clearer parts | `splitting-patterns.md` |
| `DEL-` | Move to `_quarantine/` (unused, junk, must-not-be-public) | classification |
| `SPAM-` | Email/phone/form anti-spam protection | `contact-anti-spam.md` |
| `YOU-` | Actions only the user can do (rotate key, DNS, console) | findings |

Each item: ID · severity or priority · one-line what · files touched · effort (S/M/L) ·
risk of change (Low/Med/High) · depends on (other IDs).

Order: Critical FIX → High FIX → CFG → MOVE → SPLIT → DEL → SPAM → Medium/Low FIX.
Mark the recommended minimum set as **"Recommended now"**.

## 6.2 Write the detailed files

- `REFACTOR_PLAN.md` (template in `templates/`): current tree vs proposed tree, move table
  (old path → new path), split plans (file → parts, what goes in each), quarantine list,
  import updates expected, verification commands.
- `SECURITY_REPORT.md` and `FILE_MAP.md` are already written in steps 3-4.

## 6.3 Write `SECURE_CHECK_PLAN.txt`

Use `templates/SECURE_CHECK_PLAN.txt` exactly (same parts, same markers). Rules:

- **Short:** 1-3 screens for small projects; up to ~250 lines for large ones. Details belong
  in the `.md` files - reference them by ID.
- **Highlight with markers** (plain text works in every editor and every AI chat):

  | Marker | Meaning |
  |--------|---------|
  | `!!!` | CRITICAL - real risk right now, read first |
  | `!!` | HIGH - fix soon |
  | `!` | MEDIUM / needs attention |
  | `(i)` | Info / good to know |
  | `[?]` | Your decision is needed |
  | `[YOU]` | Only you can do this (outside the code) |
  | `[DEL]` | Proposed removal (to `_quarantine/`, never hard-deleted) |
  | `>>>` | Start here / the most important line of a section |

- Box (`####`) the score and every Critical item so they cannot be missed.
- Start with **">>> READ THESE FIRST"**: the 3-5 most important lines.
- Explain each item in plain words a non-security person understands. One line of "why it
  matters" per Critical/High item.
- Never include full secrets. Never include exploit payloads beyond what is needed to
  understand the problem.
- Write it in the user's language; keep markers, IDs and paths unchanged.

## 6.4 STOP

End your turn with a short message in chat:

1. Score and grade, number of Critical/High issues.
2. The path: `secure-check-report/SECURE_CHECK_PLAN.txt`.
3. The 1-3 most urgent points (especially `[YOU]` items like rotating a leaked key - those are
   urgent even if they approve nothing).
4. How to reply:

```
APPROVE ALL                      -> apply every item
APPROVE RECOMMENDED              -> apply the "Recommended now" set
APPROVE FIX-01 FIX-02 SPAM-01    -> apply only these
APPROVE ALL EXCEPT DEL-03 SPLIT-02
SKIP                             -> keep the report only, change nothing
```

(Natural language in any language is fine: "đồng ý FIX-01 và SPAM-01".)

**Do not continue to step 7 in the same turn.** Do not "start with the easy ones".
