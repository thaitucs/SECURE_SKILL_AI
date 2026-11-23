# Plain PHP and WordPress

## Plain PHP

**Detect:** `.php` files with mixed HTML, `include 'db.php'`, `mysqli_connect`, `$_GET`.

**Boundary:** PHP executes on the server (`BE`) but files are usually inside the web root, so
**every `.php` file is a reachable URL**. `config.php`/`db.php` must not output anything and
ideally live outside the web root.

**Secrets/env:** DB credentials in `config.php` → move outside web root or use env
(`getenv`, `vlucas/phpdotenv`). Backups like `config.php.bak` are served as plain text.

**Database branch:** `mysqli`/`PDO`. Use prepared statements everywhere
(`$stmt = $pdo->prepare('... WHERE id = ?'); $stmt->execute([$id]);`).
`mysql_*` functions = removed in PHP 7 → upgrade.

**File storage branch:** `move_uploaded_file` into a folder with PHP execution disabled,
server-generated names, `finfo_file` for MIME, size limits.

**Top risks:** SQL injection; `echo $_GET[...]` (XSS → `htmlspecialchars($v, ENT_QUOTES,
'UTF-8')`); `include($_GET['page'])` (LFI/RFI); `exec/system/passthru/shell_exec` with input;
`unserialize` of user data; `md5()` passwords (use `password_hash`/`password_verify`); no
CSRF tokens; `session_regenerate_id(true)` missing after login; `display_errors=On`;
`phpinfo.php` left behind.

**Target mapping:** `public/` (only entry files + assets) · `src/Controllers` ·
`src/Services` · `src/Policies` · `src/Repositories` (DB) · `src/Storage` · `views/` ·
`config/` (outside web root).

## WordPress

**Detect:** `wp-config.php`, `wp-content/`, `wp-includes/`.

**Boundary:** core = do not edit; custom code in `wp-content/themes/<child>` and
`wp-content/plugins/<custom>`.

**Top risks**
- `wp-config.php` backups in web root; salts/keys default; `WP_DEBUG` true with
  `WP_DEBUG_DISPLAY`.
- Outdated core/plugins/themes (main cause of WP hacks) - list versions.
- `DISALLOW_FILE_EDIT` not set (admin can edit PHP).
- XML-RPC enabled without need; user enumeration (`/?author=1`, `/wp-json/wp/v2/users`).
- Custom code: missing `current_user_can()` + nonces (`wp_verify_nonce`), unescaped output
  (`esc_html`, `esc_attr`, `esc_url`), SQL without `$wpdb->prepare`.
- `wp-content/uploads` allowing PHP execution.
- Contact forms (CF7, WPForms) without anti-spam (Akismet, Turnstile, honeypot) - see
  `contact-anti-spam.md`; plain emails in footers/widgets.

**Verify:** `php -l` on changed files; WP-CLI `wp core verify-checksums`,
`wp plugin list --update=available`.
