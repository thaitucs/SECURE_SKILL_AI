# Checklist - Website (static / brochure / landing page / CMS front)

Tick each item: `PASS` / `FAIL` (→ finding) / `N/A` / `NOT CHECKED` (→ say so).

## Exposure
- [ ] Deploy folder identified; no files from `never-public-files.md` inside it.
- [ ] No `.git/`, `.env`, backups, archives, SQL dumps, drafts, `*.psd`/source design files
      with client data in the uploaded folder.
- [ ] No source maps in production unless intended.
- [ ] Directory listing disabled (`Options -Indexes`, `autoindex off`).
- [ ] No test/debug pages (`phpinfo.php`, `test.html` with internal notes).
- [ ] HTML comments contain no credentials, internal URLs, TODOs with secrets.

## Secrets
- [ ] No API secret keys in HTML/JS (maps/analytics keys are public - check restrictions).
- [ ] Form services: destination email/API key not in client code (or is a public form id).
- [ ] No hard-coded admin passwords in JS ("password-protected page" in JS = no protection).

## Transport and headers
- [ ] HTTPS everywhere, HTTP → HTTPS redirect, HSTS.
- [ ] No mixed content (`http://` scripts/images on HTTPS pages).
- [ ] Basic headers (`security-headers.md`), CSP if third-party scripts are few.

## Third-party scripts
- [ ] CDN scripts pinned to exact versions with `integrity` (SRI) + `crossorigin`.
- [ ] No abandoned/compromised CDNs (e.g. old `polyfill.io` domain).
- [ ] Analytics/chat widgets: only those actually used; consent where law requires (GDPR etc.).
- [ ] `target="_blank"` links to other sites use `rel="noopener noreferrer"` (old browsers).

## Forms and contact (see `contact-anti-spam.md`)
- [ ] Email/phone shown in page source? → SPAM items.
- [ ] Contact/newsletter forms have server-side spam protection.
- [ ] Recipient not chosen by the client; no header injection.

## Client-side code
- [ ] No `innerHTML`/`document.write`/`eval` with URL parameters, hash or user input (DOM XSS).
- [ ] No "logic that matters" in JS (prices, coupon validation, gated content). Content
      hidden with CSS/JS is still downloadable.
- [ ] Old libraries (jQuery < 3.5, Bootstrap < 3.4/4.3.1, Lodash < 4.17.21, Angular.js 1.x)
      flagged under dependencies.

## CMS front (WordPress, Joomla, Ghost...)
- See `stacks/php-plain-wordpress.md`: admin URL protection, plugin updates, XML-RPC,
  user enumeration, file editing disabled.

## Hosting (`[YOU]` items when not in code)
- [ ] DNS/hosting account has 2FA; FTP replaced by SFTP; no shared passwords in the repo.
- [ ] Domain email: SPF/DKIM/DMARC.
