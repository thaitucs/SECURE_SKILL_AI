# Architecture model: Client → Backend → (Database | File Storage)

Every project is compared with this model. Projects do not need these exact folder names,
but every piece of code must clearly belong to one of these layers.

```
 ┌──────────────────────────────────────────────────────────────┐
 │ CLIENT (Frontend)  - public, runs on the user's device         │
 │ website, web app, mobile app, desktop app UI                   │
 │ Shows data, collects input, UX validation, calls the API       │
 └──────────────────────────────┬───────────────────────────────┘
                                │ HTTPS · API only · user token
 ┌──────────────────────────────▼───────────────────────────────┐
 │ BACKEND  - private, runs on a server / function you control    │
 │ business logic · formulas · permissions · validation ·         │
 │ secrets · payments · emails · third-party integrations         │
 └───────────────┬──────────────────────────────┬────────────────┘
                 │                              │
 ┌───────────────▼──────────────┐ ┌─────────────▼─────────────────┐
 │ DATABASE                      │ │ FILE STORAGE                  │
 │ structured data only          │ │ binary content only           │
 │ rows / documents / key-value  │ │ images, video, audio, PDF,    │
 │ + file METADATA (key, mime,   │ │ office docs, uploads, exports │
 │   size, owner, visibility)    │ │ private by default            │
 └───────────────────────────────┘ └───────────────────────────────┘
```

---

## 1. Client (Frontend)

**Belongs here**
- Pages, screens, components, layouts, styles, fonts, app-owned static assets (logo, icons).
- Display formatting (dates, currency display), client-side routing, local UI state.
- UX validation (required field, email format) - always **duplicated** on the backend.
- Calls to the backend API. Public, restricted keys that are designed to be public
  (see `secret-patterns.md` → "Public by design").

**Must NOT be here**
- Any secret: API secret keys, DB credentials, service-account files, SMTP passwords,
  JWT signing secrets, payment secret keys, admin tokens.
- Business logic that decides money, access or truth: prices, totals, discounts, tax,
  commissions, scores, grades, quotas, limits, "is this user an admin", "does this user own
  this record". The client may *preview* a calculation, but the backend must compute the
  final value and ignore any value sent by the client.
- Direct database connections. Direct privileged storage access.
- Hidden "admin" pages protected only by not linking to them or by `if (role === 'admin')`
  in the UI.

Remember: everything in the client can be read and modified by the user. Minified or
obfuscated code is still readable. A mobile APK/IPA can be unpacked.

---

## 2. Backend

**Belongs here**
- **Business logic** (`services/`): formulas, calculations, workflows, state transitions,
  rules ("order can be cancelled within 24h"), pricing, reward points, grading.
- **Authorization** (`policies/`): who may read/create/update/delete what. Ownership checks
  (`record.owner_id === currentUser.id`), role checks, tenant isolation.
- **Authentication**: login, sessions/tokens, password hashing, MFA, password reset.
- **Validation** (`validators/`): schema validation of every input (type, length, range,
  format, allow-lists).
- **Secrets and integrations**: payment, email/SMS, AI APIs, maps server keys, webhooks.
- **HTTP layer** (`routes/`, `controllers/`): map requests to services; no business logic.
- Two outbound branches only, each behind its own module:
  - `database/` → Database
  - `storage/` → File Storage

A static website with no server can still have a "backend": a serverless function
(Vercel/Netlify/Cloudflare/Firebase Functions) for forms, email or anything secret.

For BaaS projects (Firebase, Supabase, Appwrite, PocketBase) where the client talks to the
database directly, the **security rules / Row Level Security policies / edge functions ARE
the backend**. They must be reviewed as backend code.

---

## 3. Database branch (structured data)

**Stores**: data that must be there every time someone opens the app and that you query,
filter, join or aggregate: users, profiles, roles, products, orders, payments status,
settings, content text, comments, logs/audit trail, sessions (or in Redis), **file metadata**.

**Never stores**
- File bytes: no `BLOB`/`bytea`/`LONGBLOB` of images, video, PDF; no base64 strings of files
  in text/JSON columns or documents. (Tiny exceptions like a 1 KB generated thumbnail hash
  are fine; say why.)
- Plain-text passwords or reversible password encryption. Use bcrypt / argon2id / scrypt.
- Raw card numbers or CVV (use the payment provider's tokens).
- Secrets of third-party services (keep in env/secret manager), unless encrypted at rest
  with a key that is not in the database.

**Access rules**
- Only the backend's `database/` module (repositories / models / DAO) talks to the database.
- Parameterized queries or ORM only. No string-built SQL with user input.
- Least-privilege DB user for the app (no superuser / `root` / `sa`).
- DB not reachable from the public internet; TLS when it crosses networks.
- Migrations are versioned in the repo; seeds never contain real personal data or real
  passwords.

**File metadata table (recommended shape)**

```
files
  id            uuid / bigint
  owner_id      -> users.id            (who can access)
  storage_key   "users/42/avatars/7f3c....webp"   (NOT a public URL, NOT the file)
  original_name "my photo.png"         (display only, never used as a path)
  mime_type     "image/webp"           (detected server-side, not trusted from client)
  size_bytes    48211
  checksum      sha256 (optional, dedupe/integrity)
  visibility    private | public
  created_at, deleted_at
```

---

## 4. File Storage branch (binary content)

**Stores**: images, video, audio, PDF, office documents, user uploads, generated exports
and invoices, backups (in a separate, locked-down bucket).

**Options**: S3 / Cloudflare R2 / Google Cloud Storage / Azure Blob / Backblaze B2 /
Supabase Storage / Firebase Storage / Cloudinary / a disk folder **outside the web root**.

**Rules**
- Only the backend's `storage/` module talks to storage with privileged credentials.
- **Private by default.** Buckets do not allow public listing. User uploads are served
  through a backend endpoint that checks permission, or via short-lived signed URLs
  (minutes, not days).
- Public marketing assets (homepage banner) may live in a public bucket/CDN - keep them in a
  separate bucket or prefix from user uploads.
- Generate storage keys server-side (UUID). Never use the client's file name as the path.
- Validate on the backend: size limit, allow-listed types, real content type (magic bytes),
  re-encode images when possible, strip EXIF metadata (GPS) from user photos.
- Never store uploads inside the source tree or a folder the web server executes
  (`public/uploads/*.php` is a classic remote-code-execution hole).
- Direct-to-storage uploads are allowed only with a backend-issued presigned URL that
  restricts key, content type, size and expiry.

---

## 5. Standard flows

**Upload**
1. Client sends file (or asks for a presigned URL) with the user's token.
2. Backend: authenticate → authorize (may this user upload here?) → validate size/type.
3. Backend `storage/` writes the file (or issues a presigned URL with strict conditions).
4. Backend `database/` inserts the metadata row.
5. Backend returns the file `id` (not a permanent public URL for private files).

**Download / view**
1. Client requests `/files/:id`.
2. Backend loads metadata from DB, checks the user may access it.
3. Backend streams the file or redirects to a signed URL valid for a few minutes.

**Delete**
1. Backend checks permission → deletes from storage → marks/deletes DB row
   (or soft-delete then a cleanup job). Avoid orphan files and orphan rows.

---

## 6. Findings this model produces

| Situation found | Severity (default) | Category |
|-----------------|--------------------|----------|
| Secret key / DB credential in client code or bundle | Critical | secrets |
| Client computes price/total/discount and backend trusts it | High | auth |
| Permission check only in the client | High | auth |
| Client connects directly to a DB with a privileged account | Critical | data_storage |
| BaaS with open rules (`allow read, write: if true`, RLS disabled) | Critical | data_storage |
| File bytes / base64 stored in the database | Medium (High if large/user-facing) | data_storage |
| Uploads stored under the web root / source tree | High | data_storage |
| Upload type/size not validated server-side | High | data_storage |
| Public bucket with listing enabled or private files publicly readable | High | data_storage |
| Long-lived public URLs for private documents | Medium | data_storage |
| Business logic inside controllers/routes or UI components | Low (maintainability) | - (SPLIT item, not scored) |
| DB access scattered across many files instead of `database/` | Low | - (MOVE/SPLIT item) |

Maintainability items are reported in `REFACTOR_PLAN.md`, not counted in the security score.
