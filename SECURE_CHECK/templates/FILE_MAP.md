# SECURE_CHECK - File map

- **Project:** {{name}} · **Date:** {{yyyy-mm-dd}}
- Labels: `FE` `BE` `BE:DB` `BE:STORAGE` `SHARED` `CONFIG` `PRIVATE` `GENERATED` `DOCS` `TEST`
- Flags: `SECRET` `LOGIC-IN-FE` `SPLIT` `MOVE` `DELETE?` `PUBLIC-EXPOSED` `CONTACT` `CONFIRM?`

## Totals

| Label | Files | With flags |
|-------|-------|------------|
| FE | {{n}} | {{n}} |
| BE | {{n}} | {{n}} |
| BE:DB | {{n}} | {{n}} |
| BE:STORAGE | {{n}} | {{n}} |
| SHARED | {{n}} | {{n}} |
| CONFIG | {{n}} | {{n}} |
| PRIVATE | {{n}} | {{n}} |
| GENERATED | {{n}} | {{n}} |
| DOCS / TEST | {{n}} | {{n}} |
| CONFIRM? | {{n}} | - |

## Files needing action

| Path | Label | Flags | Reason (evidence) | Action | Item |
|------|-------|-------|-------------------|--------|------|
| `src/lib/payment.js` | FE | SECRET, MOVE | imports `stripe` with `sk_live_` literal; bundled by Vite | MOVE SECRET TO ENV, move call to backend | FIX-01 |
| `src/pages/Checkout.jsx` | FE | LOGIC-IN-FE, SPLIT | computes `total = price * qty - discount` sent to `/api/orders` | SPLIT, move formula to `backend/src/services/pricing.service.js` | SPLIT-01, MOVE-02 |
| `public/backup.sql` | PRIVATE | PUBLIC-EXPOSED | DB dump inside deploy folder | move outside web root / quarantine | CFG-02 |
| `old/utils_copy.js` | FE | DELETE? | not imported (searched `utils_copy`, exports `formatX`) | QUARANTINE | DEL-01 |

## Groups without action

| Path pattern | Label | Files | Note |
|--------------|-------|-------|------|
| `src/components/**` | FE | {{n}} | KEEP |
| `backend/src/database/migrations/**` | BE:DB | {{n}} | KEEP |

## Need your answer (CONFIRM?)

| Path | Question |
|------|----------|
| `scripts/sync.js` | Is this run on a server (cron) or by developers locally? |
