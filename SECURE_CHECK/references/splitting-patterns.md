# Splitting patterns

**There is no fixed line limit.** A 600-line file with one clear job can stay; a 120-line
file mixing UI, API calls, a pricing formula and SQL should be split. Split so that each
part serves one specific purpose and a future developer knows where to add the next feature.

## 1. When to split - signals

Score each candidate on these signals (`scripts/find_split_candidates.py` estimates them):

1. **Mixed layers** - the file contains two or more of: UI/markup, HTTP handling, business
   logic, DB queries, storage calls, email/SMS sending, config/secrets. (Strongest signal.)
2. **Several reasons to change** - e.g. "change the discount rule" and "change the button
   color" would both edit this file.
3. **Hard to name** - the honest name would contain "and" (`UserProfileAndOrdersAndUpload`).
4. **Size relative to the project** - much larger than the project's typical file, or has
   functions/components far longer than the rest.
5. **Duplication** - the same block appears in several files.
6. **God files** - `utils.js`, `helpers.php`, `functions.php`, `common.py` with unrelated
   functions used everywhere.
7. **Deep nesting / long conditionals** that encode business rules inline.
8. **Many unrelated exports** or many unrelated imports.

Split if signal 1 is present, or if 2+ other signals are strong. Otherwise leave it and say why.

## 2. How to split - rules

1. **Behaviour stays identical.** Move code verbatim first; refactor nothing else.
2. **Name by responsibility**, using the project's existing naming style
   (`pricing.service.ts`, `useCart.ts`, `OrderRepository.php`).
3. **Dependency direction:** UI → api client → (HTTP) → controller → service → repository /
   storage. Never the reverse. Services do not import controllers; repositories do not import
   services.
4. **Keep the public surface**: the original file can re-export the moved parts, or update
   every import in the same step. Pick one, write it in the plan.
5. **One split per step**, then build/test.
6. **Keep tests next to their code** if the project does that; move tests along.
7. **Don't over-split**: no one-function-per-file explosion, no layers the project does not
   need. A small app may need `services/` but not `policies/` - then put permission checks in
   the service and say so.

## 3. Common patterns

### 3.1 React/Vue/Svelte component doing everything

Before: `CheckoutPage.jsx` - JSX + `fetch('/api/...')` + price/discount formula + form
validation + localStorage.

After:
```
pages/CheckoutPage.jsx          # layout and composition only
components/checkout/CartTable.jsx
components/checkout/CouponForm.jsx
hooks/useCart.js                # state, calls the api client
services/api/orders.api.js      # fetch calls only
utils/format-money.js           # display formatting
backend/src/services/pricing.service.js   # ← the price/discount formula MOVES to backend
```

### 3.2 Express/Fastify route file with everything

Before: `routes/orders.js` - router + validation + SQL + pricing + email.

After:
```
routes/orders.routes.js          # router.post('/', auth, validate(createOrder), ctrl.create)
controllers/orders.controller.js # req → service → res
validators/orders.validator.js   # schema
services/orders.service.js       # business rules, totals, state changes
services/notification.service.js # email sending
policies/orders.policy.js        # canView(user, order), canCancel(user, order)
database/repositories/orders.repository.js  # all SQL/ORM calls
```

### 3.3 PHP page mixing HTML and SQL

Before: `product.php` - `mysqli_query` with `$_GET['id']` + HTML output.

After:
```
public/product.php               # thin entry: load controller, render view
src/Controllers/ProductController.php
src/Repositories/ProductRepository.php   # PDO prepared statements
src/Services/PriceService.php
views/product.view.php           # HTML only, escape with htmlspecialchars()
```
(Laravel/WordPress: use their structures - see stack notes.)

### 3.4 Django/Flask/FastAPI fat views

Move logic into `services.py` (writes/workflows) and `selectors.py`/`repositories.py`
(reads). Views/routers only parse input, call services, return responses.

### 3.5 Upload handling spread around

Before: each controller writes files with `fs.writeFile('public/uploads/...')`.

After:
```
storage/storage.service.js       # save(buffer, meta) -> key ; getSignedUrl(key) ; remove(key)
storage/adapters/local.js | s3.js
storage/file-rules.js            # allowed mime types, max size, key naming
modules/files/files.service.js   # check permission, call storage, write metadata via repo
database/repositories/files.repository.js
```

### 3.6 God utils file

Split by domain: `utils/date.js`, `utils/money.js`, `utils/string.js`, `utils/validation.js`.
Server-only helpers (crypto, env, DB) move to `backend/src/utils/`; client-safe ones to
`frontend/src/utils/` or `shared/`.

### 3.7 Config and constants scattered

Collect env access into one `config/env` module that validates required variables at start-up
(fail fast). Magic numbers that are business rules (tax rate, free-shipping threshold) go to
backend config or DB settings - not hard-coded in the frontend.

### 3.8 Mobile screens (Flutter / React Native / native)

`screen` (layout) · `widgets/components` (pieces) · `state` (bloc/provider/riverpod/redux/
viewmodel) · `services/api` (HTTP) · `models` (data classes) · `repositories` (cache + API).
Business rules that matter for money/access go to the backend.

### 3.9 CSS

Split giant stylesheets by component/page or move to the project's existing approach (CSS
modules, SCSS partials, Tailwind components). Pure moves - no visual changes.

## 4. Plan entry format (REFACTOR_PLAN.md)

```
SPLIT-02  backend/routes/orders.js  (412 lines, mixes: HTTP + SQL + pricing + email)
  -> backend/src/routes/orders.routes.js        router + middleware
  -> backend/src/controllers/orders.controller.js
  -> backend/src/services/orders.service.js     calculateTotal(), cancel()
  -> backend/src/policies/orders.policy.js      canView(), canCancel()
  -> backend/src/database/repositories/orders.repository.js
  Imports to update: server.js, tests/orders.test.js
  Public surface: routes/orders.js re-exports router (removed after imports updated)
  Risk: Low · Effort: M · Verify: npm test, POST /api/orders manual check
```
