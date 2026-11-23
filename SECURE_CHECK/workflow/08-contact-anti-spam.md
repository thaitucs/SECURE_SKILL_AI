# Step 8 - Contact anti-spam (email, phone, forms, OTP)

**Goal:** reduce spam caused by email addresses and phone numbers being visible to bots, and
by unprotected forms - **only after the user approves the `SPAM-*` items**.

Knowledge base: `references/contact-anti-spam.md`.

## 8.1 During PLAN (always, when the project has `CONTACT` files)

1. List where contact data is exposed:
   - visible text, `mailto:` / `tel:` / `sms:` / WhatsApp / Zalo / Telegram links,
   - meta tags, JSON-LD / schema.org, vCards, footers, legal pages,
   - JS bundles, API responses (e.g. `/api/users` returning other users' emails/phones),
   - forms: contact, newsletter, signup, password reset, OTP/SMS verification.
2. For each, record the current protection (none / weak / good).
3. Recommend the options that fit the project (static site vs app with backend), with the
   trade-off: protection level · effort · effect on users (accessibility, SEO, conversion).
4. Create `SPAM-*` items. Mark one combination as **Recommended**, e.g.:
   - `SPAM-01` Replace visible email with a contact form (backend/serverless send) [Recommended]
   - `SPAM-02` Add honeypot + time-trap + rate limit to contact form [Recommended]
   - `SPAM-03` Add Cloudflare Turnstile / hCaptcha / reCAPTCHA (needs a site key - `[YOU]`)
   - `SPAM-04` If email must stay visible: JS-assembled, click-to-reveal link
   - `SPAM-05` Phone: click-to-reveal + business/virtual number advice
   - `SPAM-06` OTP/SMS: rate limit + CAPTCHA before sending (SMS pumping protection)
   - `YOU-xx` Set up SPF, DKIM, DMARC; use an alias address
5. In `SECURE_CHECK_PLAN.txt` part 7 explain in plain words why it matters
   (bots read page source, not the screen).

## 8.2 During APPLY (only approved SPAM items)

- Implement with the project's existing tools and style. Prefer no new dependencies;
  CAPTCHA widgets need a provider key the user must create - leave placeholders in
  `.env.example` and a `[YOU]` note.
- **Server-side checks are mandatory.** Honeypot, time-trap, CAPTCHA token verification and
  rate limits must be enforced on the backend/serverless function. Client-only checks are
  decoration.
- Keep accessibility: revealed email/phone must become a real, clickable link with readable
  text; use buttons with clear labels ("Show email"), not images of text.
- Do not put the destination email in a hidden form field or client config.
- Protect email sending from header injection (reject CR/LF in name/subject/email fields) and
  from becoming a spam relay (no auto-reply that echoes user content to arbitrary addresses).
- Remove contact data from places that do not need it (JSON-LD, meta, comments, API
  responses) only if the approved item says so - SEO/local-business markup is a trade-off the
  user decides.

## 8.3 Verify

- View page source / built HTML / JS bundle: the plain address and number should no longer
  appear (search for `@domain` and the digits).
- Submit the form normally → works. Submit with honeypot filled / too fast / without CAPTCHA
  token → rejected by the server.
- Screen reader / keyboard: reveal button reachable and labelled.

Log results in `CHANGES_LOG.md`.
