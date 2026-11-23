# Step 4 - Security audit

**Goal:** find real, verifiable security problems and describe how to fix each one.

## 4.1 Run the scanners (if you can run commands)

```
python scripts/run_all.py <project> --out <project>/secure-check-report/raw
```

This runs `inventory.py`, `scan_secrets.py`, `scan_exposure.py`, `scan_contacts.py`,
`scan_code_risks.py` and `find_split_candidates.py`, and writes a PRELIMINARY score from
unverified leads (`raw/score.txt`). Every hit is a **lead**, not a finding:
open the file, confirm, and drop false positives (test fixtures, placeholders like
`your-api-key-here`, public-by-design keys).

Also run the ecosystem's dependency audit if it is installed and works offline or against
the official registry only: `npm audit --omit=dev`, `pnpm audit`, `yarn npm audit`,
`pip-audit`, `composer audit`, `bundle audit`, `dotnet list package --vulnerable`,
`govulncheck ./...`, `flutter pub outdated`. If not available, list the outdated/major-risk
dependencies you can see and mark the check as "partial".

## 4.2 Review by checklist

Always:
1. `references/secret-patterns.md` - secrets in code, config, history hints, bundles.
2. `references/never-public-files.md` - what would be deployed that must not be.

Then every checklist that matches the project profile (see SKILL.md section 6).
Priority order for reading code:

1. Environment/config files and deploy config
2. Server entry, middleware (auth, CORS, headers, error handler, rate limit)
3. Authentication and session/token handling
4. Authorization on every route that reads or changes data (ownership!)
5. Data access (queries) and BaaS rules
6. File upload/download and storage config
7. Forms, email/SMS sending, contact info shown (anti-spam)
8. Frontend: secrets, dangerous HTML sinks, logic that should be server-side
9. Mobile/desktop specifics
10. Dependencies

## 4.3 Writing a finding

Each finding needs all of these. No evidence → no finding.

```
ID:          FIX-03
Severity:    Critical | High | Medium | Low | Info
Category:    secrets | auth | injection | exposure | data_storage | config | abuse | dependencies
Title:       Stripe secret key in frontend bundle
Location:    src/lib/payment.js:12  (and built file dist/assets/index-*.js)
Evidence:    const stripe = Stripe("sk_live_51H****x9Qa")      <- masked
Impact:      Anyone visiting the site can read the key and create refunds/charges.
Fix:         Move payment calls to backend endpoint POST /api/payments; read key from
             env STRIPE_SECRET_KEY on the server; use publishable key pk_live_ in client.
Fix effort:  S | M | L
You must do: Rotate the key in the Stripe dashboard (the old one is compromised).
```

## 4.4 Severity guide

| Severity | Meaning | Examples |
|----------|---------|----------|
| Critical | Exploitable now by anyone, leads to data breach, money loss or full takeover | live secret key in client/public repo, SQL injection on public endpoint, open Firebase/Supabase rules, `.env` or `.git` downloadable, admin API without auth, executable upload |
| High | Exploitable with little effort or by any logged-in user | IDOR (change id → see others' data), price trusted from client, missing auth on sensitive route, stored XSS, weak password hashing, JWT `none`/unsigned, CORS `*` with credentials |
| Medium | Needs specific conditions, or weakens defence significantly | missing rate limit on login/OTP/forms, reflected XSS needing interaction, verbose errors with stack traces, missing CSRF on cookie auth, long-lived signed URLs, file blobs in DB, missing security headers on an app with login |
| Low | Hardening / best practice | missing headers on a static brochure site, version disclosure, outdated non-vulnerable deps, email shown in plain text (spam harvesting) |
| Info | Observation, no direct risk | good practices found, notes for the future |

Adjust with context and say why (e.g. test key `sk_test_` → High, not Critical; secret in a
private repo that is never deployed → still High, rotate anyway).

## 4.5 Things the AI cannot fix by itself

Collect for "PART 8 - Only you can do this":
- Rotating/revoking leaked keys and passwords.
- Removing secrets from git history and force-pushing (and telling collaborators).
- Hosting settings (HTTPS, redirects, firewall, bucket policies in the cloud console).
- DNS email records (SPF, DKIM, DMARC).
- Store/console settings (Firebase console, Supabase dashboard, App Store/Play Console).

## Output

`SECURITY_REPORT.md` from `templates/SECURITY_REPORT.md`, plus a findings JSON for scoring
(`secure-check-report/raw/findings.json`, format in `references/scoring-rubric.md`).
