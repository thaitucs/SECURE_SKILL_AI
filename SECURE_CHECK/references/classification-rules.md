# Classification rules

## 1. Primary labels (exactly one per file)

| Label | Meaning | Typical examples |
|-------|---------|------------------|
| `FE` | Runs on the user's device or is served to visitors. Public. | components, pages, screens, CSS, client JS, app-owned images/fonts, mobile UI code |
| `BE` | Runs only on a server/function you control. Business logic, auth, validation, integrations. | routes, controllers, services, policies, middlewares, server actions, cloud functions |
| `BE:DB` | Backend code that talks to the database, or database definitions. | models, entities, schemas, repositories, migrations, seeds, ORM config, SQL files, BaaS rules for the DB |
| `BE:STORAGE` | Backend code that talks to file storage, or storage rules. | upload handlers, S3/GCS/Azure/Cloudinary clients, `storage.rules`, signed URL helpers |
| `SHARED` | Used by both sides, contains no secrets and no privileged logic. | TypeScript types, enums, constants, validation schemas (zod/yup) reused on both sides |
| `CONFIG` | Build, tooling, deploy or app configuration. | `package.json`, `vite.config.*`, `next.config.*`, `tsconfig.json`, `Dockerfile`, CI files, `firebase.json` |
| `PRIVATE` | Must never be public or deployed. | `.env*` (except `.env.example`), keys/certs, DB dumps, backups, internal notes with credentials, service-account JSON |
| `GENERATED` | Produced by tools; do not edit by hand. | `dist/`, `build/`, `.next/`, lock files, generated API clients, `*.min.js` you did not write |
| `DOCS` | Documentation for developers. | `README.md`, `docs/`, ADRs |
| `TEST` | Tests and fixtures. | `*.test.*`, `*.spec.*`, `tests/`, `__tests__/`, fixtures |

## 2. Flags (zero or more)

| Flag | Meaning |
|------|---------|
| `SECRET` | Contains or reads a secret value. In an `FE` or public file this is a finding. |
| `LOGIC-IN-FE` | Frontend computes something that must be authoritative (price, total, discount, permission, score, quota). |
| `SPLIT` | Mixes several responsibilities; should be split (see `splitting-patterns.md`). |
| `MOVE` | In the wrong layer or folder. |
| `DELETE?` | Candidate for quarantine (unused, duplicate, junk). Needs evidence. |
| `PUBLIC-EXPOSED` | Sits in a folder that is served/deployed publicly but should not be. |
| `CONTACT` | Shows email/phone to visitors, or contains a contact/signup/OTP form. |
| `CONFIRM?` | You are not sure - ask the user. |

## 3. Decision tree (first match wins for the primary label)

```
1. Path inside an ignored/generated folder (dist, build, .next, out, coverage...)?
       -> GENERATED  (still scan for secrets/source maps if deployed or committed)
2. Is it a secret file? (.env*, *.pem, *.key, *.p12, *.pfx, *.jks, *.keystore,
   service-account*.json, credentials*.json, id_rsa*, SQL dumps (not migrations), *.bak, *.dump)
       -> PRIVATE   (+ PUBLIC-EXPOSED if inside a public/deploy folder or not gitignored)
3. Test file or fixture?                                   -> TEST
4. Documentation?                                          -> DOCS
5. Tool/build/deploy config?                               -> CONFIG
6. Talks to the database (driver/ORM import, SQL, schema, migration, DB rules)?
       -> BE:DB
7. Talks to file storage (S3/GCS/Azure/Cloudinary SDK, multer/busboy/formidable,
   move_uploaded_file, writes uploads to disk, storage rules)?
       -> BE:STORAGE
8. Server-only signals (see 4.1)?                          -> BE
9. Client-only signals (see 4.2)?                          -> FE
10. Pure types/constants/helpers with no I/O and no secrets, imported by both sides?
       -> SHARED
11. Otherwise                                              -> CONFIRM?
```

A file that matches both 6/7 **and** has client signals is a mixing problem:
label by its *runtime location* (where it actually runs) and add `MOVE` / `SPLIT` / `SECRET`.
Example: a React component that imports `mysql` → `FE` + `MOVE` + likely `SECRET` (Critical).

## 4. Signals

### 4.1 Server-only signals
- Imports: `fs`, `child_process`, `crypto` (Node server use), `express`, `fastify`, `koa`,
  `hono`, `@nestjs/*`, `next/server`, `server-only`, `nodemailer`, `stripe` (server SDK),
  `firebase-admin`, `@supabase/supabase-js` **with service role key**, `jsonwebtoken` (signing),
  `bcrypt`, `argon2`, DB drivers, storage SDKs.
- Python: `django`, `flask`, `fastapi`, `sqlalchemy`, `boto3`, `smtplib`, `os.environ`.
- PHP: any `.php` that is not only an HTML template; `$_POST`, `PDO`, `mysqli`, `$_ENV`.
- Directives: `'use server'`, `import 'server-only'`, files under `pages/api/`, `app/api/`,
  `server/`, `api/`, `functions/`, `netlify/functions/`, `supabase/functions/`,
  `src/routes/**/+server.ts`, `+page.server.ts`, `*.server.ts`.
- Reads non-public env vars: `process.env.X` where X lacks a public prefix (see 5).

### 4.2 Client-only signals
- Uses `window`, `document`, `localStorage`, `navigator`, DOM APIs.
- JSX/TSX components, `.vue`, `.svelte`, Angular `@Component`, React hooks, `'use client'`.
- Styles, HTML templates served as-is, files in `public/`, `static/`, `assets/`, `www/`.
- Mobile UI: Flutter widgets, React Native components, Android `Activity/Fragment`,
  SwiftUI `View`. **Note:** all mobile app code is `FE` (it ships to the device), even "logic"
  files.
- Env vars with a public prefix.

## 5. Public env prefixes (bundled into the client - anyone can read them)

| Framework | Public prefix |
|-----------|---------------|
| Next.js | `NEXT_PUBLIC_` |
| Vite (React/Vue/Svelte) | `VITE_` |
| Create React App | `REACT_APP_` |
| Nuxt | `NUXT_PUBLIC_` / `runtimeConfig.public` |
| SvelteKit | `PUBLIC_` (`$env/static/public`, `$env/dynamic/public`) |
| Expo | `EXPO_PUBLIC_` |
| Astro | `PUBLIC_` |
| Gatsby | `GATSBY_` |
| Angular | everything in `environment*.ts` |
| Flutter | everything in `--dart-define`, `.env` assets, `lib/` constants |
| Vue CLI | `VUE_APP_` |

A secret behind a public prefix is a **Critical** finding even if it is "only in .env".

## 6. Logic placement - must be in the backend

| Must be backend | Frontend may do |
|-----------------|-----------------|
| Prices, totals, tax, shipping, discounts, coupons, commissions | Show the backend's numbers, preview estimates labelled as estimates |
| Scores, grades, quiz answers checking, game results with rewards | Animate, display |
| Role/permission/ownership checks, feature flags that unlock paid features | Hide buttons for UX |
| Quotas, rate limits, usage counting | Show remaining quota from backend |
| Input validation (authoritative) | Same validation for instant feedback |
| Token/session issuing, password checks, OTP verification | Store the token securely, send it |
| Sending email/SMS/notifications, payments, webhooks | Trigger via API |
| Anything needing a secret or other users' data | Nothing |

## 7. DELETE? evidence checklist

Mark `DELETE?` only if **all** hold:
- Not imported/required/included anywhere (search by file name **and** exported symbols).
- Not a framework convention file (routing by filename, migrations, config read by tools).
- Not referenced in HTML (`<script src>`, `<link href>`), CSS (`url()`), config, CI, docs.
- Not loaded dynamically (`import(\`./${name}\`)`, `require(variable)`, reflection, plugin dirs).

Strong candidates: `* copy.*`, `*(1).*`, `*_old.*`, `*.bak`, `*_backup*`, `test123.*`,
`untitled*`, `.DS_Store`, `Thumbs.db`, `desktop.ini`, `npm-debug.log`, committed build output,
duplicate libraries (`jquery-1.7.js` next to `jquery-3.7.js`), empty files, `phpinfo.php`.

Must-not-be-public files are **not** "delete" by default - they may be needed. Action is
"remove from public / move outside deploy folder / gitignore", and the user decides.
