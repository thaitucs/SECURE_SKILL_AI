# Laravel

**Detect:** `laravel/framework` in `composer.json`; `artisan`, `app/Http/Controllers`,
`routes/web.php`, `routes/api.php`.

**Boundary:** `app/`, `routes/`, `config/`, `database/` = `BE`; `resources/views` = server
templates; `resources/js|css` = `FE` (compiled by Vite into `public/build`). **Only `public/`
is the web root** - if the host points to the project root, everything is exposed (Critical).

**Secrets/env:** `.env` (never commit; `APP_KEY` inside). `config/*.php` reads `env()`.
`APP_DEBUG=false`, `APP_ENV=production` in production.

**Database branch:** Eloquent models (`app/Models`), migrations/seeders (`database/`).
Watch `DB::raw`, `whereRaw`, `selectRaw`, `orderByRaw` with input; `$guarded = []`
(mass assignment) - prefer `$fillable`.

**File storage branch:** `Storage` facade, `config/filesystems.php`. User uploads on the
`local`/`s3` (private) disk, not `public` unless intended; serve private files through a
controller with policy checks or `Storage::temporaryUrl()`. Validate:
`'file' => 'required|file|mimes:jpg,png,pdf|max:5120'`.

**Top risks**
- `APP_DEBUG=true` in production (Ignition error pages leak env/secrets).
- Web root misconfigured (project root served → `.env` downloadable).
- Missing authorization: use Policies/Gates (`$this->authorize('update', $post)`),
  `can:` middleware; check ownership in every controller method.
- `{!! $var !!}` with user data (XSS); Blade `{{ }}` escapes.
- Routes without `auth`/`auth:sanctum` middleware; `throttle` missing on login/API.
- `storage/logs/laravel.log` publicly reachable; `storage/` symlink misused.
- Old Laravel/PHP versions.

**Target mapping**
```
app/Http/Controllers   thin            app/Http/Requests   validation (FormRequest)
app/Services | app/Actions   business logic
app/Policies           authorization
app/Models + database/ DATABASE branch (+ app/Repositories if the project uses them)
app/Services/Files     FILE STORAGE branch (wraps Storage facade)
```

**Verify:** `php artisan test`, `php artisan route:list` (check middleware), `composer audit`,
`php artisan config:show app` (debug off).
