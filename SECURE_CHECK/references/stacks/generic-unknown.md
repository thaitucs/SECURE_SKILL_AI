# Generic / unknown stack

Use when no other note matches (Rust web frameworks, Elixir/Phoenix, C/C++ servers, Deno,
Bun, low-code exports, legacy ASP/ColdFusion, game servers, IoT firmware...).

## Approach
1. **Find the runtime split.** Ask for every file: *where does this run - on the user's
   device, or on a machine I control?* Device → `FE`. Machine you control → `BE`.
2. **Find the entry points.** Main function, server start, route table, HTML entry, build
   config output directory.
3. **Find trust boundaries.** Where does input from users/network enter? (HTTP handlers,
   message queues, sockets, files, CLI args, deep links.) Every one needs validation and auth.
4. **Find the data sinks.** Database calls, file writes, shell commands, HTML output, HTTP
   requests to other services, email/SMS sending.
5. **Apply the universal checks** below, then the generic checklists
   (`checklist-webapp.md`, `checklist-api.md`, `checklist-database.md`,
   `checklist-file-storage.md`).

## Universal checks
- Secrets: `secret-patterns.md` across all text files.
- Exposure: `never-public-files.md` in whatever gets deployed.
- Injection: any string concatenation that builds SQL, shell commands, HTML, file paths, URLs
  from input.
- Auth: every entry point that reads/changes data checks identity and ownership.
- Crypto: standard libraries only; password hashing with bcrypt/argon2/scrypt; CSPRNG.
- Transport: TLS, certificate verification not disabled.
- Errors: no stack traces/secrets to users.
- Dependencies: list versions, flag end-of-life runtimes/frameworks.
- Architecture: business logic and permissions on the server; DB and file storage accessed
  only through their backend modules.

## Hints per ecosystem
- **Rust (Actix, Axum, Rocket):** `sqlx::query!` (checked) vs `format!` into SQL; `cargo audit`.
- **Elixir/Phoenix:** Ecto parameterized by default (watch `fragment` with interpolation);
  `raw/1` in templates; `mix sobelow`.
- **Deno/Bun:** same as Node; check permissions flags (`--allow-all`).
- **C/C++:** memory safety, format strings, `system()`; compiler hardening flags.
- **Low-code / no-code exports:** API keys often embedded in generated JS - check the export.

State in the report that the stack had no dedicated notes, so coverage relies on the
universal checks.
