# React (Vite / Create React App) single-page app

**Detect:** `react`, `react-dom` + `vite` or `react-scripts`; `src/main.jsx|tsx` or
`src/index.js`.

**Boundary:** the whole app is `FE`. It must call a separate backend (or BaaS / serverless).
A "backend" folder inside `src/` is a red flag - it will be bundled.

**Secrets/env:** `VITE_*` / `REACT_APP_*` variables are **embedded in the bundle**. Only public
values (API base URL, publishable keys). Search the built `dist/`/`build/` for secrets too.

**Database branch:** must not exist in the client. Direct DB drivers or `firebase-admin` in
`src/` → Critical. Firebase/Supabase client SDKs are OK only with strict rules/RLS.

**File storage branch:** client may upload via backend or presigned URL. No storage secret
keys (e.g. AWS keys, Cloudinary secret) in the client.

**Top risks**
- Secrets in `VITE_`/`REACT_APP_` vars or hard-coded.
- `dangerouslySetInnerHTML` with API/user data (use DOMPurify).
- Route guards only in the client (`<PrivateRoute>`) - backend must enforce.
- Price/discount/permission logic in components (`LOGIC-IN-FE`).
- Tokens in `localStorage` + any XSS = account takeover (prefer HttpOnly cookies).
- Source maps in production (`build.sourcemap`, `GENERATE_SOURCEMAP`).
- `href={userInput}` allowing `javascript:` URLs.

**Target mapping:** `frontend/src/{pages,components,features,hooks,services/api,store,utils,
types,assets,styles}`.

**Verify:** `npm run build`, `npm test`, `npm run lint`; grep `dist/` for secret prefixes.
