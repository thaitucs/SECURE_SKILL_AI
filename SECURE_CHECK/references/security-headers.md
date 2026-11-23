# Security headers and server hardening

## 1. Recommended headers

| Header | Value (starting point) | Purpose |
|--------|------------------------|---------|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` (add `preload` only when sure) | Force HTTPS |
| `Content-Security-Policy` | Start with `default-src 'self'; img-src 'self' data: https:; object-src 'none'; base-uri 'self'; frame-ancestors 'self'; form-action 'self'` then add needed sources | Limit XSS impact |
| `X-Content-Type-Options` | `nosniff` | Stop MIME sniffing |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Limit URL leakage |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` (allow what you use) | Limit browser features |
| `X-Frame-Options` | `SAMEORIGIN` (or CSP `frame-ancestors`) | Clickjacking |
| `Cross-Origin-Opener-Policy` | `same-origin` | Isolation |
| Remove `X-Powered-By`, `Server` versions | - | Less fingerprinting |

**CSP**: roll out with `Content-Security-Policy-Report-Only` first if the site has many
third-party scripts. Never add `'unsafe-inline'`/`'unsafe-eval'` without saying it weakens
XSS protection; prefer nonces/hashes.

## 2. Cookies (session/auth)

`Set-Cookie: session=...; HttpOnly; Secure; SameSite=Lax; Path=/` (`Strict` if possible;
`None; Secure` only for real cross-site needs, then CSRF tokens are mandatory).

## 3. CORS

- Allow-list exact origins. Never `Access-Control-Allow-Origin: *` together with
  `Access-Control-Allow-Credentials: true`, and never reflect any `Origin` blindly.
- Public, read-only, no-auth APIs may use `*`.

## 4. Snippets

### Express
```js
import helmet from 'helmet';
app.disable('x-powered-by');
app.use(helmet({ contentSecurityPolicy: { useDefaults: true } }));
app.use(cors({ origin: ['https://example.com'], credentials: true }));
```

### Next.js (`next.config.js`)
```js
async headers() {
  return [{ source: '/(.*)', headers: [
    { key: 'Strict-Transport-Security', value: 'max-age=31536000; includeSubDomains' },
    { key: 'X-Content-Type-Options', value: 'nosniff' },
    { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
    { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
    { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
  ]}];
},
poweredByHeader: false,
productionBrowserSourceMaps: false,
```

### nginx
```nginx
server_tokens off;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header X-Frame-Options "SAMEORIGIN" always;
location ~ /\.(?!well-known) { deny all; }
location ~* \.(bak|old|orig|sql|log|env|ini|sh|swp|dist)$ { deny all; }
location ^~ /uploads/ { location ~ \.(php|phtml|phar|pl|py|cgi|sh)$ { deny all; } }
autoindex off;
```

### Apache (`.htaccess`)
```apache
Options -Indexes
ServerSignature Off
<IfModule mod_headers.c>
  Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
  Header always set X-Content-Type-Options "nosniff"
  Header always set Referrer-Policy "strict-origin-when-cross-origin"
  Header always set X-Frame-Options "SAMEORIGIN"
  Header unset X-Powered-By
</IfModule>
RedirectMatch 404 /\.(?!well-known)
<FilesMatch "\.(bak|old|orig|sql|log|env|ini|sh|swp)$">
  Require all denied
</FilesMatch>
```
In an uploads folder: `php_flag engine off` (mod_php) or
`<FilesMatch "\.(php|phtml|phar)$"> Require all denied </FilesMatch>`.

### Netlify (`_headers`) / Cloudflare Pages
```
/*
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
```

### Vercel (`vercel.json`)
```json
{ "headers": [{ "source": "/(.*)", "headers": [
  { "key": "X-Content-Type-Options", "value": "nosniff" },
  { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
  { "key": "X-Frame-Options", "value": "SAMEORIGIN" } ] }] }
```

### Firebase Hosting (`firebase.json` → `hosting.headers`), Django (`SECURE_*` settings,
`SecurityMiddleware`), Laravel (middleware), Spring Security (`headers()`), ASP.NET
(`app.UseHsts()`, custom middleware) - see stack notes.

## 5. Severity defaults

| Missing | App with login / personal data | Static brochure site |
|---------|--------------------------------|----------------------|
| HTTPS / HSTS | High | Medium |
| CSP | Medium | Low |
| nosniff, Referrer-Policy, frame protection | Low | Low |
| Cookie `HttpOnly`/`Secure` on session | High | n/a |
| Directory listing on | Medium (High if sensitive files) | Medium |
