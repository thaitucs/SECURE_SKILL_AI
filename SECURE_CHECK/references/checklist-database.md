# Checklist - Database branch

See `architecture-model.md` section 3.

## Placement and access
- [ ] Only backend `database/` (repositories/models) talks to the DB. List every file that
      imports a DB driver/ORM - more than the database layer → `MOVE`/`SPLIT`.
- [ ] No DB connection from frontend / mobile / desktop with real credentials.
- [ ] Single connection/pool module; credentials from env.
- [ ] App uses a least-privilege DB user (no `root`, `postgres`, `sa`, Atlas admin).
- [ ] DB not exposed publicly (bind address, firewall, `0.0.0.0/0` allow-lists in Atlas/RDS
      are `[YOU]` items); TLS for remote connections.

## Queries
- [ ] Parameterized queries / ORM everywhere; raw-query APIs reviewed.
- [ ] Dynamic `ORDER BY`/column names come from allow-lists.
- [ ] NoSQL: input types validated; no `$where`/JS evaluation with input.
- [ ] Pagination limits; no unbounded `SELECT *` on large tables for public endpoints.

## Data
- [ ] **No file bytes / base64 files** in tables/documents (`BLOB`, `bytea`, `LONGBLOB`,
      `TEXT` with `data:image/...;base64`). Store in File Storage, keep metadata row.
- [ ] Passwords hashed (bcrypt/argon2id/scrypt).
- [ ] Sensitive columns encrypted if required; no raw card data.
- [ ] Soft-delete / retention policy for personal data (privacy laws).
- [ ] Tenant column + checks in every query for multi-tenant apps.

## Schema and migrations
- [ ] Migrations versioned; no manual production-only changes.
- [ ] Seeds/fixtures contain fake data only - no real customer data, no real passwords.
- [ ] SQL dumps not in repo or web root.
- [ ] Foreign keys / unique constraints enforce integrity (e.g. one account per email).

## BaaS databases
- **Firestore / RTDB**: no `allow read, write: if true;`, no `if request.auth != null` as the
  only rule for user-owned data (any logged-in user can read all) - check
  `resource.data.ownerId == request.auth.uid`; validate written fields; deny by default.
- **Supabase/Postgres RLS**: RLS enabled on **every** table in exposed schemas; policies use
  `auth.uid()`; `service_role` key only on the server; views/functions with
  `security definer` reviewed.
- **Appwrite / PocketBase**: collection permissions not "any".

## Backups
- [ ] Backups exist (`[YOU]`), encrypted, stored privately (separate bucket), restore tested.
