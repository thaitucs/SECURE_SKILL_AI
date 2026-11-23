# Ruby on Rails

**Detect:** `Gemfile` with `rails`, `config/routes.rb`, `app/controllers`.

**Boundary:** `app/` (except `app/javascript`, `app/assets`) = `BE`; views render server-side;
`app/javascript` = `FE`; `public/` = web root.

**Secrets/env:** `config/credentials.yml.enc` + `config/master.key` (**never commit
master.key**); `secret_key_base` not in repo; env via `ENV.fetch`.

**Database branch:** ActiveRecord models, `db/migrate`. Watch `where("name = '#{params[:q]}'")`,
`order(params[:sort])`, `find_by_sql` with interpolation, `pluck` with raw SQL.

**File storage branch:** Active Storage (`config/storage.yml`) with private services; use
`rails_blob_path` behind auth or signed/expiring URLs; validate content type/size
(`active_storage_validations`).

**Top risks:** strong parameters missing (`params.permit!`); `html_safe`/`raw` with user
data; `skip_before_action :verify_authenticity_token`; missing authorization (Pundit/CanCanCan
`authorize`); `send`/`constantize` with user input; `config.force_ssl` false;
`config.consider_all_requests_local = true` in production; old Rails versions.

**Target mapping:** controllers (thin) · `app/services` (logic) · `app/policies` (Pundit) ·
`app/models` + `db/` (DATABASE) · Active Storage / `app/services/files` (STORAGE).

**Verify:** `bin/rails test` / `rspec`, `brakeman`, `bundle audit`.
