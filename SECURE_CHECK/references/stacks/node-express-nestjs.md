# Node.js backends (Express, Fastify, Koa, Hono, NestJS)

**Detect:** `express` / `fastify` / `koa` / `hono` / `@nestjs/core`; `server.js`, `app.js`,
`main.ts`, `index.js` calling `listen()`.

**Boundary:** all `BE`. Check that no frontend build serves the backend folder statically
(`express.static('.')` or `express.static(__dirname)` = whole source public!).

**Secrets/env:** `dotenv` / `process.env`; validate at start (`envalid`, zod). `.env` ignored.

**Database branch:** Prisma, Drizzle, TypeORM, Sequelize, Mongoose, Knex, `pg`, `mysql2`.
One client module; repositories only. Watch `$queryRawUnsafe`, `sequelize.query` with
template strings, `knex.raw` with concatenation, Mongoose queries from raw `req.body`
(operator injection - use `mongo-sanitize` or schema validation).

**File storage branch:** `multer`/`busboy`/`formidable`/`@fastify/multipart` → set `limits`,
`fileFilter` by magic bytes (`file-type`), store via `storage/` adapter (S3 SDK v3,
`@google-cloud/storage`, `@azure/storage-blob`). Never `dest: 'public/uploads'`.

**Top risks**
- `express.static` on the project root; `app.use(cors())` with credentials.
- Missing `helmet`, `app.disable('x-powered-by')`.
- No rate limit (`express-rate-limit`, `@fastify/rate-limit`, Nest `ThrottlerModule`).
- JWT: `jwt.verify` without `algorithms`, weak secret, no `exp`; `jwt.decode` used as verify.
- `child_process.exec` with input; `eval`, `new Function`, `vm` with input.
- Prototype pollution (`lodash.merge` of user input, `Object.assign` deep merges).
- Error handler leaking `err.stack`.
- Path traversal in `res.sendFile(req.query.file)` - use `root` option + validated names.
- NestJS: global `ValidationPipe({ whitelist: true, forbidNonWhitelisted: true })`, guards
  on every controller (`@UseGuards`), `ClassSerializerInterceptor` + `@Exclude()` for
  sensitive fields.

**Target mapping:** `references/target-structures.md` section 2 or 3 (Nest modules map
naturally to section 3).

**Verify:** `npm test`, `npm run build` (TS), `npm audit --omit=dev`, start server and hit
`/health`.
