# SECURE_CHECK - Changes log

- **Project:** {{name}} · **Date:** {{yyyy-mm-dd}}
- **Approved by user:** {{exact approval text, e.g. "APPROVE RECOMMENDED"}}
- **Branch / backup:** `{{secure-check/2026-01-31}}` / `{{backup path}}`
- **Baseline before changes:** build {{pass/fail}}, tests {{x passed / y failed}}

## Applied

| ID | What changed | Files | Verification | Undo |
|----|--------------|-------|--------------|------|
| FIX-01 | Moved Stripe call to `POST /api/payments`; key read from `STRIPE_SECRET_KEY` | `src/lib/payment.js`, `backend/src/services/payment.service.js`, `.env.example` | build ok, manual checkout ok | `git revert <sha>` |

## Not applied

| ID | Reason |
|----|--------|

## Still open - only you can do this

- [ ] YOU-01 {{rotate key ...}}

## Score

Before **{{x}}/100 ({{g}})** → after **{{y}}/100 ({{g}})**

## Reminders

- Fill the new variables in your real `.env`: {{list}}
- `_quarantine/` contains {{n}} files - review and delete when sure.
- Do not deploy `secure-check-report/` or `_quarantine/`.
