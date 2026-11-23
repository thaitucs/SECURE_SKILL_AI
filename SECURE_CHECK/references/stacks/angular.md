# Angular

**Detect:** `@angular/core`, `angular.json`, `src/app/**/*.component.ts`.

**Boundary:** browser app = `FE`. Angular SSR (`server.ts`, `@angular/ssr`) runs server code -
treat the Express part as `BE`, but keep business logic in a real API.

**Secrets/env:** `src/environments/environment*.ts` is **compiled into the bundle** - public.
Only API URLs and public keys there.

**Database / storage branches:** not in the client; via API.

**Top risks**
- `bypassSecurityTrustHtml/Url/ResourceUrl` with untrusted data.
- `[innerHTML]` with untrusted HTML (Angular sanitizes, but bypasses defeat it).
- Route guards (`canActivate`) as the only protection.
- HTTP interceptors attaching tokens to third-party domains (check URL before adding header).
- Old AngularJS (1.x) = end of life → dependency finding.

**Target mapping**
```
src/app/core/        singleton services, interceptors, guards (UX)
src/app/shared/      shared components/pipes
src/app/features/<feature>/  components, services (API calls), models
```

**Verify:** `ng build --configuration production`, `ng test`, `ng lint`.
