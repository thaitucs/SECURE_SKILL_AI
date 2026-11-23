# Files that must never be public or deployed

"Public" = reachable by a visitor: inside the web root / deploy folder / static folder /
public bucket, bundled into the client, included in a mobile/desktop package, or committed
to a public repository.

## 1. Always private

| Pattern | Why | Default severity if public |
|---------|-----|---------------------------|
| `.env`, `.env.local`, `.env.production`, `.env.*` (not `.env.example`) | Secrets | Critical |
| `.git/` directory on the server | Full source + history download | Critical |
| `.svn/`, `.hg/`, `CVS/` | Same | Critical |
| `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.crt` with key, `id_rsa*`, `*.ppk` | Private keys | Critical |
| `*.jks`, `*.keystore`, `key.properties` (Android signing) | App signing identity | Critical |
| `service-account*.json`, `*-firebase-adminsdk-*.json`, `credentials*.json`, `gcloud*.json` | Cloud admin access | Critical |
| `*.sql` dumps, `*.dump`, `*.sqlite`, `*.db`, `*.mdb`, `*.bak`, `*.backup` | Database contents (migration `.sql` files are fine in the repo, never in the web root) | Critical |
| `*.zip`, `*.tar.gz`, `*.rar`, `*.7z` of the site/source in web root | Source/backup download | High |
| `wp-config.php.bak`, `config.php~`, `*.old`, `*.orig`, `*.swp`, `*~` | Editor/backup copies of config served as text | Critical |
| `phpinfo.php`, `info.php`, `test.php`, `adminer.php`, `phpmyadmin/` | Server info / DB admin | High-Critical |
| `*.log`, `logs/`, `npm-debug.log`, `storage/logs/` | Tokens, emails, stack traces | High |
| `*.map` (source maps) in production | Full original source | Medium (High if it reveals secrets/admin logic) |
| `docker-compose*.yml`, `Dockerfile` with secrets | Credentials | High |
| `.npmrc`, `.pypirc`, `.netrc`, `.dockercfg`, `.docker/config.json` with tokens | Registry tokens | Critical |
| `.aws/`, `.azure/`, `.kube/config`, `terraform.tfstate*`, `*.tfvars` | Cloud access / infra secrets | Critical |
| `.vscode/sftp.json`, `.ftpconfig`, `sftp-config.json`, `FileZilla.xml`, `.idea/` | FTP/SSH passwords | Critical |
| `*.har`, Postman/Insomnia exports, `*.http` with tokens | Captured auth headers | High |
| `*.ipynb` with outputs | Data and keys in outputs | High |
| Internal docs with credentials, `passwords.txt`, `accounts.xlsx`, `TODO_secret.md` | Obvious | Critical |
| `secure-check-report/`, `_quarantine/` | Vulnerability details / unreviewed files | High |
| `node_modules/`, `vendor/` in web root | Attack surface, known-vulnerable files | Medium |
| `composer.json/lock`, `package.json` in web root (PHP sites) | Version disclosure | Low |
| `uploads/` that allows executing scripts | Remote code execution | Critical |

## 2. Must not ship inside client bundles / app packages

- Any secret (see `secret-patterns.md`), service-account files, `.env` loaded as an asset
  (Flutter `assets/.env`, React Native `react-native-config` with secrets).
- Admin-only code paths that rely on secrecy ("hidden" admin routes).
- Test credentials, debug menus enabled in release builds, staging endpoints with weak auth.

## 3. How to check

1. Identify the deploy folder(s): `public/`, `dist/`, `build/`, `out/`, `www/`, `htdocs/`,
   `public_html/`, `wwwroot/`, `static/`, the repo root (for static hosts like GitHub Pages
   or "upload the whole folder by FTP"), `firebase.json` → `hosting.public`,
   `netlify.toml` → `publish`, `vercel.json` → `outputDirectory`.
2. List patterns above inside those folders.
3. Check `.gitignore` covers section 1 patterns (`templates/gitignore-template`).
4. Check tracked files: `git ls-files` for section 1 patterns (ignored-after-commit case).
5. Check web server config blocks dotfiles (`location ~ /\.` deny in nginx,
   `RedirectMatch 404 /\.` in Apache, `<hiddenSegments>` in IIS).

## 4. Actions (to propose, not to do in PLAN)

- `CFG-` add patterns to `.gitignore`, `git rm --cached` tracked secrets.
- `CFG-` add deny rules for dotfiles/backups in server config.
- `MOVE-` move needed private files outside the web root (e.g. `../private/`).
- `DEL-` quarantine junk/backups the user does not need.
- `CFG-` disable source maps in production build (`build.sourcemap: false`,
  `productionBrowserSourceMaps: false`, `GENERATE_SOURCEMAP=false`) or upload them privately
  to the error tracker.
- `YOU-` rotate anything that was exposed.
