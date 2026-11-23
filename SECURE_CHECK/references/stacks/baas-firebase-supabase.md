# BaaS - Firebase, Supabase, Appwrite, PocketBase

**Detect:** `firebase.json`, `firestore.rules`, `database.rules.json`, `storage.rules`,
`functions/`; `supabase/` (migrations, `config.toml`, `functions/`), `@supabase/supabase-js`;
`appwrite`; `pocketbase`.

**Boundary:** the client talks to the database/storage directly, so **rules / RLS policies /
edge functions are the backend**. Label rules files `BE:DB` / `BE:STORAGE`; Cloud Functions /
Edge Functions `BE`.

**Secrets/env:** Firebase web config and Supabase `anon` key are public by design. Secret:
Firebase **Admin SDK service account**, Supabase **`service_role` key**, third-party keys used
in functions (use `firebase functions:secrets:set`, Supabase secrets).

## Firebase
- Firestore rules: deny by default; per-document ownership
  (`allow read, update: if request.auth.uid == resource.data.ownerId;`); validate fields on
  write (`request.resource.data.keys().hasOnly([...])`, types, sizes); no
  `allow read, write: if true;` and no `if request.auth != null;` alone for private data.
- Test-mode rules with expiry date (`request.time < timestamp.date(...)`) left in place.
- RTDB `".read": true` / `".write": true` at root.
- Storage rules: path by uid, `request.resource.size < 5 * 1024 * 1024`,
  `request.resource.contentType.matches('image/.*')`.
- App Check enabled for production (`[YOU]`).
- Business logic (prices, credits, roles) in Cloud Functions, not client writes. Users must
  not be able to write their own `role`/`credits` fields.
- Custom claims for roles, set only from Admin SDK.

## Supabase
- **RLS enabled on every table** in `public` (and any exposed schema); policies using
  `auth.uid()`; separate `select/insert/update/delete` policies; `with check` on writes.
- `service_role` key never in client/bundle.
- `security definer` functions: set `search_path`, check permissions inside.
- Storage: buckets private unless intended; policies on `storage.objects` by
  `(storage.foldername(name))[1] = auth.uid()::text`.
- Edge Functions verify JWT (do not disable `verify_jwt` without reason).

## Appwrite / PocketBase
- Collection/document permissions not `any`/empty rules; API keys with minimal scopes, server
  only.

**Target mapping**
```
firebase/  or supabase/
  rules/ (firestore.rules, storage.rules)  or  migrations/ (RLS policies in SQL)
  functions/src/{handlers, services, policies, db, storage}
web/ or mobile/   (client, public config only)
```

**Verify:** Firebase emulator + rules unit tests (`@firebase/rules-unit-testing`);
`supabase db lint`, `supabase test db` if configured; review the security advisors in the
Supabase dashboard (`[YOU]`).
