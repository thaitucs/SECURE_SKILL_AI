# Checklist - Web application (frontend + backend)

Organised by topic. OWASP Top 10 (2021) IDs in brackets; the 2025 edition regroups the same
topics (access control, misconfiguration, supply chain, crypto, injection, insecure design,
authentication, integrity, logging, exception handling).

## 1. Access control [A01] - most common critical bug
- [ ] Every route that reads/changes data requires authentication (deny by default).
- [ ] **Ownership checks**: `/api/orders/:id` checks `order.userId === currentUser.id`
      (or tenant). Changing the id must not reveal others' data (IDOR/BOLA).
- [ ] Role checks are on the server (admin routes, admin actions). UI hiding is not security.
- [ ] Mass assignment blocked: users cannot set `role`, `isAdmin`, `balance`, `price`,
      `ownerId` via request body (allow-list fields / DTOs).
- [ ] Business values computed on the server (price, totals, discounts) - `LOGIC-IN-FE`.
- [ ] Multi-step flows enforce order (cannot skip payment step by calling the final endpoint).
- [ ] CORS allow-list; no credentials with `*`.
- [ ] Directory traversal impossible in file download (`../`).

## 2. Cryptography and sensitive data [A02]
- [ ] Passwords: bcrypt (cost ≥ 10), argon2id, or scrypt. Never MD5/SHA1/SHA256 alone,
      never reversible encryption.
- [ ] HTTPS only; secure cookies; HSTS.
- [ ] Sensitive data encrypted at rest when required (ID numbers, health data).
- [ ] No sensitive data in URLs (tokens in query strings get logged).
- [ ] Random tokens use a CSPRNG (`crypto.randomBytes`, `secrets.token_urlsafe`,
      `random_bytes`) - not `Math.random()`, `rand()`, `uniqid()`.

## 3. Injection [A03]
- [ ] SQL: parameterized queries / ORM; no string concatenation or template literals with
      input (also check ORM raw methods: `$queryRawUnsafe`, `sequelize.query`, `whereRaw`,
      `DB::raw`, `.extra()`, `text()`).
- [ ] NoSQL: no raw objects from the body in queries (`{ $ne: null }` operator injection);
      cast/validate types.
- [ ] Command: no `exec`/`system`/`shell_exec`/`child_process.exec`/`subprocess(shell=True)`
      with input.
- [ ] XSS: templates auto-escape; review `dangerouslySetInnerHTML`, `v-html`, `{@html}`,
      `[innerHTML]`, `|safe`, `{!! !!}`, `html_safe`, `raw`, `innerHTML`; sanitize with
      DOMPurify / bleach / HTML Purifier when HTML is needed.
- [ ] Template injection: no user input rendered as a template.
- [ ] Header/email injection: CR/LF rejected.
- [ ] LDAP/XPath/regex DoS (catastrophic backtracking on user input).

## 4. Insecure design [A04]
- [ ] Rate limits on login, signup, reset, OTP, search, expensive endpoints.
- [ ] Limits on business actions (coupon reuse, vote/like spam, referral abuse).
- [ ] Sensitive actions re-confirm (password for email change, 2FA for payouts).

## 5. Misconfiguration [A05]
- [ ] Debug off in production (`DEBUG=False`, `APP_DEBUG=false`, `NODE_ENV=production`,
      `app.run(debug=True)` absent).
- [ ] Error handler hides stack traces/SQL errors from users; logs them server-side.
- [ ] Default credentials changed; sample/admin panels removed or protected.
- [ ] Security headers (`security-headers.md`).
- [ ] Cookies: `HttpOnly`, `Secure`, `SameSite`.
- [ ] CSRF protection for cookie-based sessions (framework CSRF middleware or SameSite +
      token).
- [ ] GraphQL introspection/playground disabled in production (if not public API).

## 6. Components [A06]
- [ ] Dependency audit run (see workflow step 4.1); critical/high advisories listed.
- [ ] No abandoned packages for security-critical work (auth, crypto, uploads).

## 7. Authentication [A07]
- [ ] Login: generic errors, rate limit / lockout / CAPTCHA after failures.
- [ ] Sessions: regenerate on login; expire; logout invalidates server-side.
- [ ] JWT: strong secret (≥ 32 random bytes) or asymmetric keys, algorithm pinned
      (`algorithms: ['HS256']`), `exp` set and checked, no sensitive data in payload, not stored
      in `localStorage` if XSS risk is high (prefer HttpOnly cookie).
- [ ] Password reset tokens: random, single-use, short expiry, hashed in DB.
- [ ] MFA available for admin accounts.
- [ ] OAuth: `state` parameter, exact redirect URIs, PKCE for public clients.

## 8. Integrity [A08]
- [ ] No unsafe deserialization (`pickle.loads`, `unserialize`, `yaml.load` without
      SafeLoader, Java native serialization, `node-serialize`) of untrusted data.
- [ ] Webhooks verify signatures (Stripe `constructEvent`, GitHub HMAC...).
- [ ] CI/CD secrets scoped; third-party actions pinned.
- [ ] SRI on CDN scripts.

## 9. Logging and monitoring [A09]
- [ ] Auth failures, permission denials, admin actions logged (without passwords/tokens).
- [ ] Logs do not contain secrets, full card numbers, OTPs, session tokens.
- [ ] Some alerting exists (or `[YOU]` item).

## 10. SSRF [A10]
- [ ] Server-side URL fetching (link previews, webhooks, image-from-URL, PDF render) allow-
      lists hosts/schemes and blocks internal IPs (`127.0.0.0/8`, `10/8`, `172.16/12`,
      `192.168/16`, `169.254.169.254`, `::1`, `fc00::/7`).

## 11. Architecture (see `architecture-model.md`)
- [ ] Frontend has no secrets and no authoritative logic.
- [ ] Only backend `database/` talks to the DB; only backend `storage/` talks to storage.
- [ ] Files not stored in the DB; uploads private and validated.

## 12. AI/LLM features (if present)
- [ ] LLM API keys server-side only; per-user rate limits and spend caps.
- [ ] Prompt injection considered: LLM output is not executed, not trusted for authorization,
      HTML-escaped before display; tools/functions the model can call are permission-checked.
- [ ] User data sent to the LLM provider is disclosed in the privacy policy.
