# Scoring rubric (0-100, grade A-F)

Deterministic: the same findings always give the same score. `scripts/score.py` implements
exactly this.

## 1. Categories and weights

| Key | Category | Weight | Covers |
|-----|----------|--------|--------|
| `secrets` | Secrets & credentials | 20 | hard-coded keys, passwords, secrets in client/bundles/history, `.env` tracked |
| `auth` | Authentication & authorization | 20 | login, sessions/JWT, password hashing, ownership/role checks, logic-in-FE trusted by server |
| `injection` | Input handling & injection | 15 | SQL/NoSQL/command injection, XSS, SSRF, path traversal, deserialization, validation |
| `exposure` | Public exposure | 10 | files that must not be public, source maps, directory listing, debug pages |
| `data_storage` | Database & file storage | 10 | DB access/rules, RLS, files in DB, upload validation, bucket privacy, signed URLs |
| `config` | Configuration & transport | 10 | HTTPS, security headers, CORS, cookies flags, debug mode, error messages, CSRF |
| `abuse` | Abuse & spam protection | 10 | rate limiting, brute force, contact email/phone harvesting, form spam, OTP/SMS pumping |
| `dependencies` | Dependencies & supply chain | 5 | known-vulnerable or abandoned packages, unpinned CDN scripts without SRI |

Total = 100.

## 2. Deductions per open finding

| Severity | Points deducted (within its category) |
|----------|---------------------------------------|
| Critical | 20 |
| High | 10 |
| Medium | 4 |
| Low | 1 |
| Info | 0 |

- `category_score = max(0, weight - sum(deductions of open findings in that category))`
- Findings with `status` = `fixed`, `accepted_risk` or `false_positive` are not deducted.
  (`accepted_risk` is listed separately in the report so it is never hidden.)

## 3. Not-applicable categories

A category is `not_applicable` only when the feature does not exist at all
(e.g. `auth` for a static brochure site with no login, no forms, no API;
`data_storage` with no DB and no uploads). Then:

```
raw = sum(category_score of applicable categories)
max = sum(weight of applicable categories)
score = round(raw / max * 100)
```

`secrets`, `exposure`, `config` and `dependencies` are **always applicable**.

## 4. Caps (applied after the calculation)

| Condition | Maximum score |
|-----------|---------------|
| ≥ 1 open Critical | 49 |
| ≥ 1 open High (and no Critical) | 79 |
| Audit was partial (some areas not reviewed) | no cap, but label "partial" |

## 5. Grades

| Score | Grade | Plain meaning |
|-------|-------|---------------|
| 90-100 | A | Strong. Keep monitoring. |
| 75-89 | B | Good. A few things to improve. |
| 60-74 | C | Fair. Important gaps. |
| 40-59 | D | Weak. Fix before handling real users' data. |
| 0-39 | F | Unsafe. Do not deploy / take offline until fixed. |

## 6. Bars for the plan file

10 characters per bar, `#` filled, `-` empty: `filled = round(score / max * 10)`.
Overall uses 20 characters.

```
Secrets & credentials      [##--------]   4/20  !!!
Authentication & authz     [######----]  12/20  !!
```

Marker after a category: `!!!` if it has an open Critical, `!!` if High, `!` if Medium.

## 7. findings.json format

```json
{
  "project": "my-shop",
  "partial": false,
  "not_applicable": ["abuse"],
  "findings": [
    {
      "id": "FIX-01",
      "severity": "critical",
      "category": "secrets",
      "title": "Stripe secret key in frontend",
      "file": "src/lib/payment.js",
      "line": 12,
      "status": "open",
      "proposed_fix": true
    }
  ]
}
```

- `severity`: `critical | high | medium | low | info`
- `status`: `open | fixed | accepted_risk | false_positive`
- `proposed_fix: true` = the plan contains a fix item for it; used for the
  **projected score** (score if all proposed fixes are applied). `[YOU]`-only fixes
  (e.g. rotate a key) count as fixable only if the plan includes the code part too.

## 8. Worked example

Findings: secrets 1 Critical; auth 1 High + 1 Medium; config 2 Low; abuse 1 Medium.

```
secrets      20 - 20      = 0
auth         20 - 10 - 4  = 6
injection    15           = 15
exposure     10           = 10
data_storage 10           = 10
config       10 - 1 - 1   = 8
abuse        10 - 4       = 6
dependencies  5           = 5
raw = 60  -> cap (Critical open) -> 49 -> Grade D
```
