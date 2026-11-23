# Target structures

Choose the structure that fits the project's size and framework. **Framework conventions win**
- map the logical layers onto them instead of forcing these exact folders.
Explain the choice in `REFACTOR_PLAN.md`.

## 1. Logical layers (always the same)

| Layer | Job | Must not |
|-------|-----|----------|
| `frontend/` (client) | UI, display, UX validation, API calls | hold secrets or authoritative logic |
| `backend/routes` | URL → handler mapping, attach middleware | contain logic |
| `backend/controllers` | Read request, call service, shape response | query DB, calculate business values |
| `backend/services` | **Business logic**: formulas, rules, workflows | know about HTTP (req/res) |
| `backend/policies` | **Authorization**: can user X do Y on Z | be skipped by any route |
| `backend/validators` | Input schemas | trust the client |
| `backend/middlewares` | auth, rate limit, CORS, headers, errors, logging | hold business logic |
| `backend/database` | **Branch 1**: models, repositories, migrations, seeds | store files |
| `backend/storage` | **Branch 2**: upload/download/delete/sign files | store business data |
| `backend/config` | load + validate env, constants per environment | contain secret values |
| `shared/` | types, enums, constants, validation schemas used on both sides | import server-only code |

## 2. Full-stack, layered (small/medium projects)

```
project/
├── frontend/                      # or client/, web/, apps/web
│   ├── public/                    # ONLY files meant for every visitor (favicon, robots.txt)
│   └── src/
│       ├── pages/ | app/ | views/ | screens/
│       ├── components/            # reusable UI pieces
│       ├── features/<feature>/    # optional: UI + hooks + api for one feature
│       ├── hooks/ | composables/
│       ├── services/api/          # functions that call the backend (fetch/axios)
│       ├── store/                 # client state
│       ├── utils/                 # formatting, pure helpers (no secrets)
│       ├── styles/
│       ├── assets/                # app-owned images/fonts
│       └── types/
├── backend/                       # or server/, api/
│   ├── src/
│   │   ├── server.(ts|js|py)      # entry: create app, mount middleware + routes
│   │   ├── config/                # env.(ts|py): load + validate required env vars
│   │   ├── routes/
│   │   ├── controllers/
│   │   ├── services/              # business logic (pricing.service, order.service ...)
│   │   ├── policies/              # authorization (order.policy ...)
│   │   ├── validators/            # input schemas
│   │   ├── middlewares/           # auth, rateLimit, securityHeaders, errorHandler
│   │   ├── database/              # ── BRANCH 1: DATABASE ──
│   │   │   ├── client.(ts|py)     # single connection/pool/ORM init
│   │   │   ├── models/            # entities / schemas
│   │   │   ├── repositories/      # all queries live here
│   │   │   ├── migrations/
│   │   │   └── seeds/             # fake data only
│   │   ├── storage/               # ── BRANCH 2: FILE STORAGE ──
│   │   │   ├── storage.service    # upload, getSignedUrl, delete, stream
│   │   │   ├── adapters/          # local.ts | s3.ts | gcs.ts | azure.ts | cloudinary.ts
│   │   │   └── file-rules         # allowed types, max sizes, key naming
│   │   ├── jobs/                  # background/cron tasks
│   │   └── utils/
│   └── tests/
├── shared/                        # types/, constants/, schemas/ (safe for both sides)
├── docs/
├── .env.example                   # names of all env vars, no values
├── .gitignore
└── README.md
```

## 3. Feature modules (larger projects)

Same layers, grouped per feature:

```
backend/src/
├── modules/
│   ├── orders/
│   │   ├── orders.routes
│   │   ├── orders.controller
│   │   ├── orders.service        # business logic
│   │   ├── orders.policy         # authorization
│   │   ├── orders.validator
│   │   └── orders.repository     # DB branch for this feature
│   ├── files/
│   │   ├── files.controller
│   │   ├── files.service         # uses storage/ + files.repository
│   │   └── files.repository      # metadata rows
│   └── users/ ...
├── database/   (client, migrations, shared models)
├── storage/    (adapters, file-rules)
├── middlewares/ config/ utils/
```

Rule of thumb: > ~5 features or > 2 developers → feature modules; otherwise layered.

## 4. Static website (no server)

```
site/
├── index.html, about.html ...
├── assets/ { css/, js/, img/, fonts/ }
├── functions/ | api/ | netlify/functions/   # optional mini-backend: contact form, email
├── .env.example                              # for the functions only
└── (deploy only the site folder - not docs, not drafts, not backups)
```

## 5. Mobile app + backend

```
mobile/                       # all code here is FE (ships to the device)
  lib/ or src/
    screens/ widgets|components/ state/ services/api/ models/ utils/ config/
backend/                      # same as section 2
```
Mobile `config/` holds only public values (API base URL, public keys).

## 6. Monorepo

```
apps/web  apps/mobile  apps/api  packages/shared  packages/ui
```
Each app follows its section above; `packages/shared` must not import server code.

## 7. Framework mapping (keep their conventions)

| Framework | Routes | Controllers | Services/logic | DB branch | Storage branch |
|-----------|--------|-------------|----------------|-----------|----------------|
| Next.js (app router) | `app/**/route.ts`, server actions | thin route handlers | `src/server/services/` + `import 'server-only'` | `src/server/db/` | `src/server/storage/` |
| Nuxt | `server/api/` | handlers | `server/services/` | `server/db/` | `server/storage/` |
| SvelteKit | `+server.ts`, `+page.server.ts` | same | `src/lib/server/services/` | `src/lib/server/db/` | `src/lib/server/storage/` |
| Express/Fastify/Koa/Hono | `routes/` | `controllers/` | `services/` | `database/` | `storage/` |
| NestJS | `*.controller.ts` | same | `*.service.ts` | `*.repository.ts`/entities | `storage/` module |
| Django | `urls.py` | `views.py` (thin) | `services.py` / `selectors.py` | `models.py`, migrations | `storage.py` + `django-storages` |
| Flask/FastAPI | blueprints / routers | handlers | `services/` | `db/`, `models/`, `repositories/` | `storage/` |
| Laravel | `routes/` | `app/Http/Controllers` | `app/Services`, `app/Actions` | `app/Models`, `database/` | `Storage` facade, `config/filesystems.php`, `app/Services/Files` |
| Rails | `config/routes.rb` | controllers | `app/services` | `app/models`, `db/` | Active Storage |
| Spring | `@RestController` | same | `@Service` | `@Repository`, entities | `storage/` service |
| ASP.NET | Controllers / Minimal APIs | same | `Services/` | `Data/` (DbContext), `Repositories/` | `Storage/` |
| Go | `internal/http/` | handlers | `internal/service/` | `internal/repository/` | `internal/storage/` |
