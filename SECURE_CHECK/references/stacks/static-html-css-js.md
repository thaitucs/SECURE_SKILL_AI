# Static website (HTML / CSS / JS)

**Detect:** `.html` files, `assets/`, no `package.json` framework, or a simple bundler only.
Hosted on GitHub Pages, Netlify, Vercel, Cloudflare Pages, shared hosting (FTP/cPanel).

**Boundary:** everything is `FE` and public. There is no backend unless you add serverless
functions. Anything "secret" in this project is already leaked.

**Secrets/env:** none allowed in files. Form services: use a public form id, keep the
destination address in the provider dashboard. API calls needing a key → serverless function.

**Database branch:** none. If data is needed (e.g. bookings), add a backend or BaaS with rules.

**File storage branch:** only app-owned assets (`assets/img`). Never accept uploads without a
backend.

**Top risks**
- The whole repo folder uploaded by FTP → `.git/`, `.env`, drafts, `*.zip` backups public.
- "Password protected" pages in JS → no protection.
- Email/phone in plain HTML → harvesting (`contact-anti-spam.md`).
- Old jQuery/Bootstrap from CDNs without SRI.
- DOM XSS from `location.hash`/`location.search` into `innerHTML`.
- Missing HTTPS/headers (configure via `_headers`, `.htaccess`, `vercel.json`).

**Target mapping:** `references/target-structures.md` section 4. Optional `functions/`
folder for a contact form.

**Verify:** open pages locally; search the deploy folder for `@` + domain and phone digits;
check that only the site folder is deployed.
