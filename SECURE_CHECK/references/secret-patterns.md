# Secret patterns

Use these to find secrets in source, config, built bundles, mobile resources and notebooks.
`scripts/scan_secrets.py` implements them. Always confirm by reading the context and drop
placeholders (`xxx`, `your_key_here`, `<API_KEY>`, `changeme`, `example`, all-zero values).

**Always mask** in reports: first 4 + `****` + last 4 characters.

## 1. High-confidence provider patterns

| Provider | Pattern (regex) | Default severity |
|----------|-----------------|------------------|
| AWS access key id | `\b(AKIA\|ASIA)[0-9A-Z]{16}\b` | Critical (if secret nearby) / High |
| AWS secret key | `aws(.{0,20})?(secret\|key).{0,5}['"][0-9a-zA-Z/+]{40}['"]` | Critical |
| Google API key | `\bAIza[0-9A-Za-z_\-]{35}\b` | Medium-High (see 3) |
| Google OAuth client secret | `GOCSPX-[0-9A-Za-z_\-]{28}` | Critical |
| GCP / Firebase service account | `"type"\s*:\s*"service_account"` | Critical |
| GitHub token | `\b(ghp\|gho\|ghu\|ghs\|ghr)_[A-Za-z0-9]{36}\b`, `github_pat_[A-Za-z0-9_]{60,}` | Critical |
| GitLab token | `glpat-[A-Za-z0-9_\-]{20}` | Critical |
| Slack token | `xox[baprs]-[A-Za-z0-9-]{10,}` | High |
| Slack webhook | `https://hooks\.slack\.com/services/[A-Za-z0-9/]+` | Medium |
| Discord webhook | `https://(discord\|discordapp)\.com/api/webhooks/\d+/[\w-]+` | Medium |
| Stripe secret / restricted | `\b(sk\|rk)_live_[0-9a-zA-Z]{20,}` | Critical |
| Stripe test secret | `\bsk_test_[0-9a-zA-Z]{20,}` | High |
| Stripe webhook secret | `whsec_[0-9a-zA-Z]{20,}` | High |
| OpenAI | `\bsk-(proj-\|svcacct-\|admin-)?[A-Za-z0-9_\-]{20,}` | Critical |
| Anthropic | `\bsk-ant-[A-Za-z0-9_\-]{20,}` | Critical |
| Google Gemini / AI Studio | `AIza...` (as Google key, but server-only - Critical in client) | Critical |
| Hugging Face | `\bhf_[A-Za-z0-9]{30,}` | High |
| Twilio | `\bSK[0-9a-fA-F]{32}\b` (API key), `\bAC[0-9a-fA-F]{32}\b` + auth token | Critical |
| SendGrid | `SG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}` | Critical |
| Mailgun | `key-[0-9a-zA-Z]{32}` | Critical |
| Mailchimp | `[0-9a-f]{32}-us\d{1,2}` | High |
| Telegram bot | `\b\d{8,10}:[A-Za-z0-9_\-]{35}\b` | High |
| npm token | `\bnpm_[A-Za-z0-9]{36}\b` | Critical |
| PyPI token | `pypi-AgEIcHlwaS5vcmc[A-Za-z0-9_\-]{50,}` | Critical |
| Shopify | `shp(at\|ca\|pa\|ss)_[a-fA-F0-9]{32}` | Critical |
| Square | `EAAA[A-Za-z0-9_\-]{60}`, `sq0csp-[0-9A-Za-z_\-]{43}` | Critical |
| PayPal / Braintree | `access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32}` | Critical |
| Azure storage | `AccountKey=[A-Za-z0-9+/=]{88}` | Critical |
| Azure connection string | `DefaultEndpointsProtocol=https;AccountName=` | Critical |
| Supabase service role | JWT whose payload contains `"role":"service_role"` | Critical |
| JWT (any) | `eyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+` | decode payload, judge |
| Private key | `-----BEGIN (RSA \|EC \|DSA \|OPENSSH \|PGP \|ENCRYPTED )?PRIVATE KEY-----` | Critical |
| DB URL with password | `(postgres(ql)?\|mysql\|mariadb\|mongodb(\+srv)?\|redis\|rediss\|amqp\|mssql)://[^:\s/]+:[^@\s]+@` | Critical |
| Basic auth in URL | `https?://[^:\s/]+:[^@\s]+@` | High |
| Cloudinary URL | `cloudinary://\d+:[A-Za-z0-9_\-]+@` | Critical |
| Mapbox secret | `\bsk\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+` | High |
| Algolia admin key | `algolia.{0,20}(admin\|write).{0,10}['"][a-f0-9]{32}['"]` | High |

## 2. Generic patterns (lower confidence - verify)

- Assignment of a suspicious name to a literal:
  `(?i)(password|passwd|pwd|secret|token|api[_-]?key|apikey|access[_-]?key|private[_-]?key|client[_-]?secret|auth|credential|smtp_pass|db_pass)\s*[:=]\s*['"][^'"\s]{6,}['"]`
- High-entropy strings (Shannon entropy > 4.0 for base64-like, > 3.0 for hex) of length ≥ 20
  assigned to such names.
- Hard-coded admin credentials: `admin/admin`, `root` with literal password, default
  `SECRET_KEY = 'django-insecure-...'`, Laravel `APP_KEY=base64:...` committed, Rails
  `secret_key_base` committed, `JWT_SECRET = "secret"`.

## 3. Public by design (not secrets - but check restrictions)

| Value | Why it can be public | What to check |
|-------|----------------------|---------------|
| Firebase web `apiKey` | Identifies the project | Firestore/Storage/RTDB **rules** and App Check - that is the real protection |
| Supabase `anon` key | Designed for clients | **RLS enabled** on every table + policies; storage policies |
| Stripe `pk_live_` / `pk_test_` | Publishable | Nothing secret; make sure `sk_` is not next to it |
| Google Maps/Places browser key | Must be in the page | HTTP referrer + API restrictions in Google Cloud console (`[YOU]` item) |
| reCAPTCHA / Turnstile / hCaptcha **site** key | Public | The **secret** key must stay on the server |
| Sentry DSN (public part) | Designed for clients | Rate limits / allowed domains |
| Algolia search-only key | Designed for clients | It must be the search-only one |
| OAuth client **ID** | Public | Client **secret** must stay server-side; redirect URIs locked down |
| Mapbox `pk.` token | Public | URL restrictions |

## 4. Where to look (beyond source files)

- `.env`, `.env.*`, `config/*.json|yaml`, `appsettings*.json`, `application*.properties|yml`,
  `settings.py`, `wp-config.php`, `docker-compose*.yml`, CI files, `Dockerfile` (`ENV`, `ARG`).
- Mobile: `google-services.json`, `GoogleService-Info.plist` (public-ish), `strings.xml`,
  `Info.plist`, `gradle.properties`, `local.properties`, `*.keystore`, Flutter `assets/.env`.
- Built output: `dist/`, `build/`, `.next/static/`, `*.js.map` (source maps expose source).
- Notebooks `*.ipynb` (outputs!), `*.log`, `*.har`, Postman collections, `*.http` files.
- Git history (if allowed to run git): `git log -p -S "<prefix>"` for known prefixes, or
  `git log --all --diff-filter=D --name-only` for deleted `.env` files. Report findings as
  "in history"; the fix is rotation + `[YOU]` history cleanup.
- `.gitignore` itself: is `.env` ignored? Was it ignored **after** being committed
  (`git ls-files .env` still lists it)?

## 5. Fix pattern

1. Rotate/revoke the secret at the provider (`[YOU]`, urgent).
2. Move the value to environment / secret manager on the backend.
3. Replace the literal with an env lookup; add the name to `.env.example`.
4. Ensure `.gitignore` covers `.env*` and key files; `git rm --cached` tracked secret files
   (APPLY, approved item).
5. Clean history if the repo is or was public/shared (`[YOU]`: `git filter-repo` or BFG,
   force-push, ask collaborators to re-clone).
