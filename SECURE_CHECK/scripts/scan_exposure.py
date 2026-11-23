#!/usr/bin/env python3
"""SECURE_CHECK - public exposure & misconfiguration scanner.

Finds files that must never be public (.env, keys, dumps, backups, logs, source maps),
checks .gitignore / git tracking, detects deploy folders, and flags risky configuration
(debug on, open CORS, open Firebase rules, cleartext traffic, Electron flags, uploads under
the web root, files stored in the database ...). Results are LEADS to verify.

Usage:
  python scan_exposure.py <project_dir> [--out DIR] [--fail-on critical|high|medium|low]
"""
import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    PUBLIC_DIR_NAMES, git_ignored, git_tracked_files, in_build_dir, in_public_dir, is_git_repo,
    is_private_name, iter_files, make_finding, read_text, setup_console, severity_at_least,
    write_json, SEVERITY_ORDER,
)

# (glob on file name, title, severity if public/tracked, category)
NEVER_PUBLIC = [
    (".env", "Environment file with secrets", "critical"),
    (".env.*", "Environment file with secrets", "critical"),
    ("*.pem", "Private key / certificate", "critical"),
    ("*.key", "Private key", "critical"),
    ("*.p12", "Key store", "critical"),
    ("*.pfx", "Key store", "critical"),
    ("*.jks", "Android signing key store", "critical"),
    ("*.keystore", "Android signing key store", "critical"),
    ("key.properties", "Android signing config", "critical"),
    ("id_rsa*", "SSH private key", "critical"),
    ("id_ed25519*", "SSH private key", "critical"),
    ("*.ppk", "PuTTY private key", "critical"),
    ("service-account*.json", "Cloud service account credentials", "critical"),
    ("*-firebase-adminsdk-*.json", "Firebase Admin SDK credentials", "critical"),
    ("credentials*.json", "Credentials file", "critical"),
    ("master.key", "Rails master key", "critical"),
    ("*dump*.sql", "Database dump", "critical"),
    ("*backup*.sql", "Database backup", "critical"),
    ("*.sql.gz", "Compressed database dump", "critical"),
    ("*.dump", "Database dump", "critical"),
    ("*.sqlite", "Database file", "high"),
    ("*.sqlite3", "Database file", "high"),
    ("*.mdb", "Database file", "high"),
    ("*.bak", "Backup file", "high"),
    ("*.backup", "Backup file", "high"),
    ("*.old", "Old copy of a file", "medium"),
    ("*.orig", "Original copy of a file", "medium"),
    ("*.swp", "Editor swap file", "medium"),
    ("*~", "Editor backup file", "medium"),
    ("*.log", "Log file", "high"),
    ("*.har", "HTTP archive (may contain tokens)", "high"),
    (".npmrc", "npm config (may contain tokens)", "high"),
    (".pypirc", "PyPI config (may contain tokens)", "high"),
    (".netrc", "Machine credentials", "critical"),
    ("*.tfvars", "Terraform variables", "high"),
    ("terraform.tfstate*", "Terraform state (contains secrets)", "critical"),
    ("sftp-config.json", "SFTP credentials", "critical"),
    ("sftp.json", "SFTP credentials", "critical"),
    (".ftpconfig", "FTP credentials", "critical"),
    ("phpinfo.php", "phpinfo page (server details)", "high"),
    ("info.php", "Possible phpinfo page", "medium"),
    ("adminer*.php", "Database admin tool", "critical"),
    ("*.zip", "Archive (possible source/backup)", "high"),
    ("*.tar.gz", "Archive (possible source/backup)", "high"),
    ("*.rar", "Archive (possible source/backup)", "high"),
    ("*.7z", "Archive (possible source/backup)", "high"),
    ("*.ipynb", "Notebook (outputs may contain data/keys)", "medium"),
]
ENV_OK = {".env.example", ".env.sample", ".env.template", ".env.dist"}

# (regex, title, severity, category, applies-to filename glob or None)
CONFIG_RULES = [
    (r"^\s*DEBUG\s*=\s*True\b", "Django DEBUG = True", "high", "config", "settings*.py"),
    (r"^\s*ALLOWED_HOSTS\s*=\s*\[\s*['\"]\*['\"]\s*\]", "Django ALLOWED_HOSTS = ['*']", "medium", "config", "settings*.py"),
    (r"^\s*SECRET_KEY\s*=\s*['\"]django-insecure-", "Django insecure SECRET_KEY committed", "high", "secrets", "settings*.py"),
    (r"\.run\([^)]*debug\s*=\s*True", "Flask/Werkzeug debug mode enabled", "high", "config", "*.py"),
    (r"^\s*APP_DEBUG\s*=\s*true", "Laravel APP_DEBUG=true", "high", "config", ".env*"),
    (r"^\s*APP_ENV\s*=\s*local", "Laravel APP_ENV=local (check production)", "low", "config", ".env.production*"),
    (r"define\(\s*['\"]WP_DEBUG['\"]\s*,\s*true", "WordPress WP_DEBUG true", "medium", "config", "wp-config*.php"),
    (r"display_errors\s*=\s*(On|1)", "PHP display_errors on", "medium", "config", "*.ini"),
    (r"ini_set\(\s*['\"]display_errors['\"]\s*,\s*['\"]?(1|On)", "PHP display_errors on", "medium", "config", "*.php"),
    (r"productionBrowserSourceMaps\s*:\s*true", "Next.js production source maps enabled", "medium", "exposure", "next.config.*"),
    (r"sourcemap\s*:\s*true", "Production source maps enabled (Vite/Rollup)", "medium", "exposure", "vite.config.*"),
    (r"GENERATE_SOURCEMAP\s*=\s*true", "CRA source maps enabled", "low", "exposure", ".env*"),
    (r"Access-Control-Allow-Origin['\"]?\s*[,:]\s*['\"]\*['\"]", "CORS allows any origin (*)", "medium", "config", None),
    (r"origin\s*:\s*(?:['\"]\*['\"]|true)\s*,?[^\n]{0,80}credentials\s*:\s*true", "CORS any origin WITH credentials", "high", "config", None),
    (r"allow_origins\s*=\s*\[\s*['\"]\*['\"]\s*\][^\n]{0,120}allow_credentials\s*=\s*True", "FastAPI CORS * with credentials", "high", "config", "*.py"),
    (r"AllowAnyOrigin\(\)[^\n]{0,80}AllowCredentials\(\)", ".NET CORS any origin with credentials", "high", "config", "*.cs"),
    (r"express\.static\(\s*(?:__dirname|['\"]\.\/?['\"]|process\.cwd\(\))\s*\)", "Express serves the project root as static files", "critical", "exposure", None),
    (r"allow\s+read\s*,\s*write\s*:\s*if\s+true", "Firebase rules allow anyone to read/write", "critical", "data_storage", "*.rules"),
    (r"allow\s+(?:read|write)\s*:\s*if\s+true", "Firebase rules allow public access", "high", "data_storage", "*.rules"),
    (r"request\.time\s*<\s*timestamp\.date\(", "Firebase test-mode rules (expire by date, open until then)", "high", "data_storage", "*.rules"),
    (r"['\"]\.(?:read|write)['\"]\s*:\s*(?:true|['\"]true['\"])", "Realtime Database rule open to everyone", "critical", "data_storage", "*.json"),
    (r"disable\s+row\s+level\s+security", "Supabase/Postgres RLS disabled", "high", "data_storage", "*.sql"),
    (r"android:debuggable\s*=\s*['\"]true['\"]", "Android app debuggable", "high", "config", "AndroidManifest.xml"),
    (r"android:usesCleartextTraffic\s*=\s*['\"]true['\"]", "Android cleartext HTTP allowed", "medium", "config", "AndroidManifest.xml"),
    (r"android:allowBackup\s*=\s*['\"]true['\"]", "Android allowBackup=true (app data in backups)", "low", "config", "AndroidManifest.xml"),
    (r"<key>NSAllowsArbitraryLoads</key>\s*<true\s*/>", "iOS ATS disabled (any HTTP allowed)", "medium", "config", "*.plist"),
    (r"nodeIntegration\s*:\s*true", "Electron nodeIntegration enabled", "high", "config", None),
    (r"contextIsolation\s*:\s*false", "Electron contextIsolation disabled", "high", "config", None),
    (r"webSecurity\s*:\s*false", "Electron webSecurity disabled", "high", "config", None),
    (r"rejectUnauthorized\s*:\s*false", "TLS certificate verification disabled (Node)", "high", "config", None),
    (r"NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0", "TLS verification disabled globally (Node)", "high", "config", None),
    (r"verify\s*=\s*False", "TLS certificate verification disabled (Python requests)", "medium", "config", "*.py"),
    (r"InsecureSkipVerify\s*:\s*true", "TLS verification disabled (Go)", "high", "config", "*.go"),
    (r"badCertificateCallback[^\n]{0,80}=>\s*true", "TLS verification disabled (Dart)", "high", "config", "*.dart"),
    (r"^\s*Options\s+[^\n]*\+?Indexes", "Apache directory listing enabled", "medium", "exposure", ".htaccess"),
    (r"autoindex\s+on", "nginx directory listing enabled", "medium", "exposure", "*.conf"),
    (r"management\.endpoints\.web\.exposure\.include\s*[=:]\s*['\"]?\*", "Spring Actuator exposes all endpoints", "high", "exposure", "application*"),
    (r"UseDeveloperExceptionPage\(\)", "ASP.NET developer exception page (check it is dev-only)", "low", "config", "*.cs"),
    (r"(?:BLOB|LONGBLOB|MEDIUMBLOB|bytea|VARBINARY\(MAX\))", "Binary column in database schema (files in DB?)", "medium", "data_storage", "*.sql"),
    (r"^\s*\w+\s+Bytes\b", "Prisma Bytes field (files stored in DB?)", "medium", "data_storage", "*.prisma"),
    (r"\bType\.BLOB\b|DataTypes\.BLOB|type:\s*Buffer\b|models\.BinaryField|LargeBinary", "Binary field in model (files stored in DB?)", "medium", "data_storage", None),
    (r"data:image/[a-z]+;base64,", "Base64 image literal (files stored in code/DB?)", "low", "data_storage", None),
    (r"dest\s*:\s*['\"](?:\./)?public/uploads", "Uploads stored in the public folder", "high", "data_storage", None),
    (r"move_uploaded_file\([^,]+,\s*['\"]?(?:\./)?(?:uploads|public|images)/", "PHP uploads stored in the web root", "high", "data_storage", "*.php"),
    (r"(?:cdn\.polyfill\.io|polyfill\.io/v3)", "Script from the compromised polyfill.io domain", "critical", "dependencies", None),
]
COMPILED_RULES = [(re.compile(rx, re.IGNORECASE | re.MULTILINE), t, s, c, g) for rx, t, s, c, g in CONFIG_RULES]

TEXT_CONFIG_EXT = {
    ".js", ".mjs", ".cjs", ".ts", ".py", ".php", ".rb", ".go", ".cs", ".java", ".kt", ".dart",
    ".json", ".yml", ".yaml", ".toml", ".ini", ".conf", ".xml", ".plist", ".rules", ".sql",
    ".properties", ".prisma", ".env", ".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", "",
}


def detect_deploy_dirs(root):
    dirs = set()
    notes = []
    fb = root / "firebase.json"
    if fb.exists():
        try:
            data = json.loads(fb.read_text(encoding="utf-8", errors="replace"))
            hosting = data.get("hosting")
            for h in (hosting if isinstance(hosting, list) else [hosting]):
                if isinstance(h, dict) and h.get("public"):
                    dirs.add(h["public"].strip("./") or ".")
                    notes.append("firebase.json hosting.public = %s" % h["public"])
        except Exception:
            pass
    nt = root / "netlify.toml"
    if nt.exists():
        m = re.search(r"publish\s*=\s*['\"]([^'\"]+)['\"]", nt.read_text(encoding="utf-8", errors="replace"))
        if m:
            dirs.add(m.group(1).strip("./") or ".")
            notes.append("netlify.toml publish = %s" % m.group(1))
    vj = root / "vercel.json"
    if vj.exists():
        try:
            data = json.loads(vj.read_text(encoding="utf-8", errors="replace"))
            if data.get("outputDirectory"):
                dirs.add(data["outputDirectory"].strip("./") or ".")
                notes.append("vercel.json outputDirectory = %s" % data["outputDirectory"])
        except Exception:
            pass
    has_pkg = (root / "package.json").exists() or (root / "composer.json").exists()
    if (root / "index.html").exists() and not has_pkg:
        dirs.add(".")
        notes.append("index.html at project root without a build tool: the root folder is probably uploaded as-is")
    if (root / "index.php").exists() and not (root / "public").exists():
        dirs.add(".")
        notes.append("index.php at project root: the root folder is probably the web root")
    for name in PUBLIC_DIR_NAMES:
        if (root / name).is_dir():
            dirs.add(name)
    return sorted(dirs), notes


def under(rel, deploy_dirs):
    for d in deploy_dirs:
        if d == ".":
            return True
        if rel == d or rel.startswith(d.rstrip("/") + "/"):
            return True
    return False


def run(root):
    root = Path(root).resolve()
    findings = []
    counter = [0]

    def add(sev, cat, title, rel=None, line=None, note=None, confidence="medium", evidence=None):
        counter[0] += 1
        findings.append(make_finding("SCAN-EXP-%03d" % counter[0], sev, cat, title, file=rel, line=line,
                                     source="scan_exposure", confidence=confidence, note=note, evidence=evidence))

    deploy_dirs, deploy_notes = detect_deploy_dirs(root)
    git = is_git_repo(root)
    tracked = git_tracked_files(root) if git else set()

    all_files = list(iter_files(root, include_build=True))
    candidates = []
    for rel, path, _in_build in all_files:
        name = rel.rsplit("/", 1)[-1]
        lname = name.lower()
        if lname in ENV_OK:
            continue
        for pat, title, sev in NEVER_PUBLIC:
            if fnmatch.fnmatch(lname, pat):
                candidates.append((rel, title, sev))
                break
    ignored = git_ignored(root, [c[0] for c in candidates]) if git else set()

    for rel, title, sev in candidates:
        public = under(rel, deploy_dirs) or in_public_dir(rel)
        is_tracked = rel in tracked
        is_ignored = rel in ignored
        reasons = []
        if public:
            reasons.append("inside a deployed/public folder")
        if is_tracked:
            reasons.append("tracked by git")
        if git and not is_tracked and not is_ignored:
            reasons.append("not covered by .gitignore")
        if not reasons:
            continue
        severity = sev
        if not public and not is_tracked:
            severity = "low"  # untracked and not public: hygiene only
        elif not public and is_tracked and sev == "critical":
            severity = "high"  # committed but not served: rotate + untrack
        if rel.endswith(".zip") or rel.endswith(".7z") or rel.endswith(".rar") or rel.endswith(".tar.gz"):
            if not public:
                continue
        add(severity, "exposure" if public else "secrets" if is_private_name(rel.rsplit("/", 1)[-1]) else "exposure",
            "%s: %s" % (title, ", ".join(reasons)), rel, confidence="high")

    # Source maps in build/deploy output
    maps = [rel for rel, _p, _b in all_files if rel.endswith(".map") and (in_build_dir(rel) or under(rel, deploy_dirs))]
    if maps:
        add("medium", "exposure", "%d source map file(s) in build/deploy output (original source readable)" % len(maps),
            maps[0], note="Examples: " + ", ".join(maps[:5]))

    # .gitignore coverage
    gi = root / ".gitignore"
    gi_text = gi.read_text(encoding="utf-8", errors="replace") if gi.exists() else ""
    if git or gi.exists():
        if not re.search(r"^\s*/?\.env\b|^\s*\*\.env|^\s*\.env\*", gi_text, re.MULTILINE):
            add("medium", "secrets", ".gitignore does not ignore .env files", ".gitignore" if gi.exists() else None,
                confidence="high")
    else:
        add("info", "config", "Project is not a git repository - SECURE_CHECK will need a backup copy before APPLY")

    # Config rules
    for rel, path, _in_build in all_files:
        if in_build_dir(rel):
            continue
        name = rel.rsplit("/", 1)[-1]
        ext = Path(name).suffix.lower()
        if ext not in TEXT_CONFIG_EXT and not name.startswith(".env") and name not in (".htaccess",):
            continue
        text = read_text(path, max_bytes=2_000_000)
        if not text:
            continue
        for rx, title, sev, cat, glob in COMPILED_RULES:
            if glob and not fnmatch.fnmatch(name, glob) and not fnmatch.fnmatch(name.lower(), glob.lower()):
                continue
            m = rx.search(text)
            if not m:
                continue
            line = text.count("\n", 0, m.start()) + 1
            snippet = text.splitlines()[line - 1].strip()[:140] if text.splitlines() else ""
            if name.startswith(".env"):
                snippet = snippet.split("=")[0] + "=..."
            add(sev, cat, title, rel, line, evidence=snippet)

    # Upload folders under the web root
    for rel, path, _in_build in all_files:
        parts = rel.lower().split("/")
        if "uploads" in parts[:-1] and (under(rel, deploy_dirs) or in_public_dir(rel)):
            add("high", "data_storage", "User uploads stored inside a public/web-root folder", "/".join(rel.split("/")[: parts.index("uploads") + 1]),
                note="Move uploads to private storage; disable script execution in that folder.")
            break
    for rel, path, _in_build in all_files:
        parts = rel.lower().split("/")
        if "uploads" in parts[:-1] and rel.lower().endswith((".php", ".phtml", ".phar", ".jsp", ".aspx")):
            add("critical", "data_storage", "Executable script inside an uploads folder", rel, confidence="high")

    findings.sort(key=lambda f: (-SEVERITY_ORDER[f["severity"]], f["file"] or "", f["line"] or 0))
    return {
        "scanner": "scan_exposure",
        "root": str(root),
        "git_repo": git,
        "deploy_dirs": deploy_dirs,
        "deploy_notes": deploy_notes,
        "findings": findings,
    }


def print_report(result, limit=60):
    f = result["findings"]
    print("== SECURE_CHECK scan_exposure: %d lead(s) ==" % len(f))
    print("  deploy/public folders: %s" % (", ".join(result["deploy_dirs"]) or "none detected"))
    for n in result["deploy_notes"]:
        print("  (i) " + n)
    for item in f[:limit]:
        loc = "%s:%s" % (item["file"], item["line"]) if item.get("line") else (item["file"] or "-")
        print("  [%-8s] %-40s %s" % (item["severity"].upper(), loc, item["title"]))
    if len(f) > limit:
        print("  ... %d more in JSON output" % (len(f) - limit))


def main(argv=None):
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    ap.add_argument("--out")
    ap.add_argument("--fail-on", choices=["critical", "high", "medium", "low"])
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    result = run(args.root)
    if args.out:
        write_json(Path(args.out) / "exposure.json", result)
    if not args.quiet:
        print_report(result)
    if args.fail_on and any(severity_at_least(x["severity"], args.fail_on) for x in result["findings"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
