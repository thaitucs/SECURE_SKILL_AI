# Serverless / edge (Vercel, Netlify, Cloudflare Workers/Pages, AWS Lambda, Azure/GCP Functions)

**Detect:** `vercel.json`, `api/` folder (Vercel), `netlify.toml`, `netlify/functions/`,
`wrangler.toml`, `functions/` (Cloudflare Pages), `serverless.yml`, `template.yaml` (SAM),
`handler.js|py` with `exports.handler`/`def handler(event, context)`.

**Boundary:** functions = `BE`. The publish/output directory = `FE` public.

**Secrets/env:** set in the platform dashboard / `wrangler secret put` / SSM / Secrets
Manager. Never in `wrangler.toml` `[vars]` (plain text, committed), `netlify.toml`, or
`serverless.yml` literals.

**Database branch:** connection reuse outside the handler; serverless-friendly drivers
(pooling via PgBouncer/Neon/PlanetScale/Data API); credentials from env.

**File storage branch:** presigned URLs to S3/R2 (functions have small body limits); R2/S3
bindings with least privilege.

**Top risks**
- Functions without auth (every function is a public URL).
- No rate limiting (cost explosion) - use platform WAF/rate-limit rules or KV/Redis counters.
- Over-privileged IAM roles (`"Action": "*"`).
- Publish directory set to repo root (`publish = "."`) → everything public.
- CORS `*` on functions with cookies.
- Environment variables printed in logs/errors.
- Preview deployments exposing staging data publicly (`[YOU]`: protect previews).

**Target mapping**
```
api/ | netlify/functions/ | functions/   thin handlers
lib/server/{services, policies, db, storage}   shared server code (not in publish dir)
```

**Verify:** local emulators (`vercel dev`, `netlify dev`, `wrangler dev`, `sam local`);
check publish dir contents after build.
