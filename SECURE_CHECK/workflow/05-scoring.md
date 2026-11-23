# Step 5 - Security score

**Goal:** a repeatable 0-100 score and A-F grade that two different AIs would compute the
same way from the same findings.

Rules: `references/scoring-rubric.md`.

## Procedure

1. Put all verified findings in `secure-check-report/raw/findings.json`.
2. Mark categories that do not apply as `not_applicable` (e.g. `auth` for a static site with
   no login and no forms) - their weight is redistributed.
3. Compute:
   - with commands: `python scripts/score.py secure-check-report/raw/findings.json`
   - without: follow the formula in the rubric by hand and show the arithmetic.
4. Record: overall score, grade, cap applied (if any), and the score per category.
5. Compute the **projected score** = the score if every proposed `FIX-*` item is applied.
   This motivates the user and shows what the plan achieves.

## Presenting the score

In `SECURE_CHECK_PLAN.txt`:

```
##############################################################
#  SECURITY SCORE:  41 / 100      GRADE: F                   #
#  [########------------]                                    #
#  !!! Capped at 49 because 2 CRITICAL issues are open.       #
#  After the proposed fixes: 88 / 100 (B)                     #
##############################################################
```

Category lines use the same bar: `Secrets & credentials   [##--------]  4/20  !!!`.

Never inflate or round up a score to be nice. Never give a score if the audit was partial
without saying "partial - based on N of M areas reviewed".
