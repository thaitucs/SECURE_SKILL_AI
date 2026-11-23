# Step 2 - Discovery

**Goal:** understand what this project is, how it runs and where it is deployed.

## 2.1 Inventory

- With commands: `python scripts/inventory.py <project> --out secure-check-report/raw`
- Without: list the tree (top 3-4 levels), then open marker files.

Record: total files, files per extension, the largest files, folders that look public
(`public/`, `static/`, `www/`, `htdocs/`, `wwwroot/`, `assets/`, `dist/`).

## 2.2 Identify the stack

Open marker files and read dependencies:

| Marker | Meaning |
|--------|---------|
| `package.json` | JS/TS. Check `dependencies` for react, next, vue, nuxt, @angular/core, svelte, @sveltejs/kit, express, @nestjs/core, fastify, koa, hono, electron, @tauri-apps, react-native, expo |
| `requirements.txt`, `pyproject.toml`, `Pipfile` | Python: django, flask, fastapi |
| `composer.json`, `*.php`, `wp-config.php` | PHP / Laravel / WordPress |
| `Gemfile` | Ruby / Rails |
| `pom.xml`, `build.gradle(.kts)` | Java/Kotlin: Spring, Android |
| `*.csproj`, `*.sln` | .NET |
| `go.mod` | Go |
| `Cargo.toml` | Rust (Tauri if `tauri.conf.json`) |
| `pubspec.yaml` | Flutter / Dart |
| `AndroidManifest.xml`, `Info.plist`, `*.xcodeproj` | Native mobile |
| `firebase.json`, `firestore.rules`, `storage.rules`, `supabase/` | BaaS |
| `vercel.json`, `netlify.toml`, `wrangler.toml`, `serverless.yml`, `Dockerfile`, `docker-compose.yml`, `.github/workflows/` | Hosting / deploy / CI |
| Only `.html/.css/.js` | Static website |

Then open the matching file(s) in `references/stacks/`.

## 2.3 Project profile

Determine and write down:

- **Type:** static website · web app · API only · mobile app · desktop app · full-stack ·
  monorepo (list each app).
- **Entry points:** server start file, frontend root, mobile main, functions.
- **Deploy target(s):** what folder is uploaded or built, where to (hosting, store, server).
- **Architecture status** against `references/architecture-model.md`:
  - Frontend: `OK` / `MIXED` (contains backend code or secrets) / `MISSING`
  - Backend: `OK` / `MIXED` / `MISSING` / `BaaS rules`
  - Database: name + how accessed (ORM, raw driver, BaaS SDK) / `NONE`
  - File storage: where files go (S3, local folder, DB blobs, public folder) / `NONE`
- **Sensitive features present:** login, roles/admin, payments, uploads, emails, SMS/OTP,
  personal data, AI APIs, webhooks, public contact info (email/phone shown).
- **Existing tooling:** tests, linters, CI, build commands (`npm run build`, etc.) - you need
  these later for verification.

## 2.4 Dependency map (lightweight)

For files you will classify or move, note who imports them. You need this to:
- detect dead files (not imported anywhere and not loaded by convention),
- update imports safely when moving or splitting.

Framework convention files are "used" even if nothing imports them (Next.js `app/**/page.tsx`,
Nuxt `pages/`, SvelteKit `+page.svelte`, Laravel routes/controllers, Django `urls.py`,
`migrations/`, test files, config files read by tools).

## Exit criteria

Profile written (goes into `SECURE_CHECK_PLAN.txt` part 1) · stack notes loaded ·
build/test commands known or marked unknown.
