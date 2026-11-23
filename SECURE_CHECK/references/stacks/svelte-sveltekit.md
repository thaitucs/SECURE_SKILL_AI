# Svelte / SvelteKit

**Detect:** `svelte`, `@sveltejs/kit`, `svelte.config.js`, `src/routes/**/+page.svelte`.

**Boundary**
- `BE`: `+server.ts`, `+page.server.ts`, `+layout.server.ts`, `hooks.server.ts`,
  `src/lib/server/**` (SvelteKit refuses to import it from client code - use it).
- `FE`: `.svelte` components, `+page.ts` (runs on both!), `src/lib/**` outside `server/`.

**Secrets/env:** `$env/static/private` and `$env/dynamic/private` are server-only;
`$env/*/public` and `PUBLIC_*` are public.

**Database branch:** `src/lib/server/db/`.

**File storage branch:** `src/lib/server/storage/`.

**Top risks**
- Form actions (`export const actions`) are public endpoints: auth + validate.
- `load` functions returning sensitive fields to the page.
- `{@html ...}` with untrusted content.
- Auth only in `+layout.ts` (client) instead of `hooks.server.ts` / server loads.
- CSRF: SvelteKit checks origin for form posts - do not disable `csrf.checkOrigin`.

**Target mapping**
```
src/routes/                 pages + thin server handlers
src/lib/components/         UI
src/lib/server/services/    business logic
src/lib/server/policies/    authorization
src/lib/server/db/          DATABASE branch
src/lib/server/storage/     FILE STORAGE branch
```

**Verify:** `npm run build`, `npm run check`.
