# Vue / Nuxt

**Detect:** `vue` (+ `vite` or `@vue/cli-service`), `nuxt`; `.vue` files; `nuxt.config.*`.

**Boundary**
- Vue SPA: all `FE`.
- Nuxt: `server/` (`server/api`, `server/routes`, `server/middleware`, `server/utils`) is `BE`;
  `pages/`, `components/`, `composables/`, `plugins/` (unless `.server.ts`) are `FE`.

**Secrets/env:** Vite `VITE_*`, Vue CLI `VUE_APP_*`, Nuxt `runtimeConfig.public.*` and
`NUXT_PUBLIC_*` are public. Secrets in `runtimeConfig` (non-public) are server-only - use them
only inside `server/`.

**Database branch:** `server/db/` or `server/utils/db.ts`.

**File storage branch:** `server/storage/`; `readMultipartFormData` with size/type checks.

**Top risks**
- `v-html` with user/API data (sanitize).
- Route middleware auth only on the client - `server/api` handlers must check.
- `server/api` handlers returning raw DB rows.
- Secrets placed in `runtimeConfig.public`.
- Nuxt devtools / sourcemaps enabled in production.

**Target mapping**
```
pages/ components/ composables/ stores/ (Pinia) utils/      FE
server/api/            thin handlers
server/services/       business logic
server/policies/       authorization
server/db/             DATABASE branch
server/storage/        FILE STORAGE branch
shared/ (types, schemas)
```

**Verify:** `npm run build`, `npx nuxi typecheck`, grep `.output/public` for secrets.
