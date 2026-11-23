# Next.js

**Detect:** `next` in dependencies; `app/` (App Router) or `pages/` (Pages Router);
`next.config.*`.

**Boundary**
- Server (`BE`): `app/**/route.ts`, Server Components without `'use client'`, Server Actions
  (`'use server'`), `pages/api/**`, `getServerSideProps`/`getStaticProps`, `middleware.ts`.
- Client (`FE`): files with `'use client'` and **everything they import**.
- Shared modules imported by a client component are bundled into the client. Protect server
  modules with `import 'server-only'`.

**Secrets/env:** only `NEXT_PUBLIC_*` reach the browser. Non-public vars used in a client
component become `undefined` - developers then "fix" it by renaming to `NEXT_PUBLIC_` → leak.
Check for secrets with `NEXT_PUBLIC_` prefix.

**Database branch:** `src/server/db/` (Prisma/Drizzle client singleton) imported only from
server code; mark with `server-only`.

**File storage branch:** `src/server/storage/`; uploads via route handler or presigned URL.
Do not write uploads to `public/` (not served after build on many hosts, and public).

**Top risks**
- **Server Actions are public endpoints**: each must check auth + authorization + validate
  input (zod). Hidden buttons do not protect them.
- Route handlers missing ownership checks.
- `middleware.ts` used as the only auth layer (also check in handlers/actions).
- Returning whole DB objects to client components (leaks fields) - select fields.
- `dangerouslySetInnerHTML`, `next/image` `remotePatterns` too broad (`**`).
- `productionBrowserSourceMaps: true`.
- Keep Next.js updated (security releases are frequent).

**Target mapping**
```
src/app/...                  routes, pages, route handlers (thin)
src/components/  src/hooks/  client UI
src/server/services/         business logic       (server-only)
src/server/policies/         authorization        (server-only)
src/server/db/               DATABASE branch       (server-only)
src/server/storage/          FILE STORAGE branch   (server-only)
src/lib/validators/          zod schemas (shared)
```

**Verify:** `npm run build` (fails if server-only imported in client), `npm run lint`,
grep `.next/static` for secrets.
