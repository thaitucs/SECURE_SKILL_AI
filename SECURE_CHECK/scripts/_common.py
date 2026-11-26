"""Shared helpers for SECURE_CHECK scripts.

Python 3.8+, standard library only. Nothing here sends data anywhere.
"""
import fnmatch
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

# --------------------------------------------------------------------------------------
# Folders
# --------------------------------------------------------------------------------------

# Never walked (dependencies, VCS internals, caches).
HARD_IGNORE_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "bower_components", "jspm_packages", "vendor",
    ".venv", "venv", "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox",
    "Pods", ".gradle", ".dart_tool", ".pub-cache", ".terraform", ".serverless",
    ".angular", ".expo", ".yarn", ".pnpm-store",
}

# Build output: skipped for code review, but scanned for secrets / source maps.
BUILD_DIRS = {
    "dist", "build", "out", ".next", ".nuxt", ".output", ".svelte-kit", "coverage",
    "target", ".turbo", ".parcel-cache", ".cache", ".vercel", ".netlify",
    "storybook-static", "obj",
}

# The skill itself and its reports - never scanned.
SKILL_DIRS = {"SECURE_CHECK", "secure-check", "secure-check-report"}

# Folder names that are usually served to visitors as-is.
PUBLIC_DIR_NAMES = {"public", "static", "www", "htdocs", "public_html", "wwwroot", "web"}

BINARY_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".bmp", ".ico", ".icns", ".tif",
    ".tiff", ".psd", ".ai", ".sketch", ".fig", ".mp3", ".wav", ".ogg", ".flac", ".m4a",
    ".mp4", ".mov", ".avi", ".mkv", ".webm", ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".zip", ".gz", ".tgz", ".rar", ".7z", ".tar", ".bz2", ".xz", ".pdf", ".doc", ".docx",
    ".xls", ".xlsx", ".ppt", ".pptx", ".exe", ".dll", ".so", ".dylib", ".class", ".jar",
    ".war", ".pyc", ".pyo", ".o", ".a", ".lib", ".apk", ".aab", ".ipa", ".dmg", ".msi",
    ".bin", ".dat", ".wasm", ".node", ".sqlite", ".sqlite3", ".db", ".mdb", ".jks",
    ".keystore", ".p12", ".pfx",
}

CODE_EXT = {
    ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts", ".vue", ".svelte",
    ".astro", ".py", ".php", ".rb", ".java", ".kt", ".kts", ".scala", ".go", ".rs",
    ".cs", ".fs", ".vb", ".swift", ".m", ".mm", ".dart", ".c", ".cc", ".cpp", ".h",
    ".hpp", ".ex", ".exs", ".erl", ".clj", ".lua", ".pl", ".sh", ".ps1", ".html", ".htm",
    ".css", ".scss", ".sass", ".less", ".erb", ".ejs", ".hbs", ".njk", ".twig",
    ".liquid", ".cshtml", ".razor", ".jsp", ".sql",
}

SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def setup_console():
    """Make printing safe on Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def _is_venv(path):
    return (path / "pyvenv.cfg").exists()


def iter_files(root, include_build=False, max_files=200000):
    """Yield (rel_posix, abs_path, in_build) for files under root."""
    root = Path(root).resolve()
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        rel_dir = current.relative_to(root)
        in_build = any(part in BUILD_DIRS for part in rel_dir.parts)
        keep = []
        for d in dirnames:
            if d in HARD_IGNORE_DIRS or d in SKILL_DIRS:
                continue
            if _is_venv(current / d):
                continue
            if d in BUILD_DIRS and not include_build:
                continue
            keep.append(d)
        dirnames[:] = sorted(keep)
        for name in sorted(filenames):
            path = current / name
            rel = (rel_dir / name).as_posix()
            count += 1
            if count > max_files:
                return
            yield rel, path, in_build


def is_binary(path, ext=None):
    ext = (ext or path.suffix).lower()
    if ext in BINARY_EXT:
        return True
    try:
        with open(path, "rb") as fh:
            chunk = fh.read(8192)
        return b"\x00" in chunk
    except OSError:
        return True


def read_text(path, max_bytes=5_000_000):
    try:
        if path.stat().st_size > max_bytes:
            return None
        if is_binary(path):
            return None
        with open(path, "rb") as fh:
            data = fh.read()
        return data.decode("utf-8", errors="replace")
    except OSError:
        return None


def count_lines(text):
    if not text:
        return 0
    return text.count("\n") + (0 if text.endswith("\n") else 1)


def mask(value):
    """Mask a secret: first 4 + **** + last 4 (shorter values reveal less)."""
    value = str(value)
    if len(value) <= 8:
        return value[:1] + "****"
    if len(value) <= 16:
        return value[:2] + "****" + value[-2:]
    return value[:4] + "****" + value[-4:]


def shannon_entropy(s):
    if not s:
        return 0.0
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    n = float(len(s))
    return -sum((c / n) * math.log2(c / n) for c in freq.values())


def path_parts_lower(rel):
    return [p.lower() for p in rel.split("/")]


def in_public_dir(rel):
    parts = path_parts_lower(rel)[:-1]
    return any(p in PUBLIC_DIR_NAMES for p in parts)


def in_build_dir(rel):
    parts = rel.split("/")[:-1]
    return any(p in BUILD_DIRS for p in parts)


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ensure_local_only(path.parent)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------------------
# Local-only outputs: everything SECURE_CHECK generates stays on the user's machine.
# --------------------------------------------------------------------------------------

REPORT_DIR_NAME = "secure-check-report"
QUARANTINE_DIR_NAME = "_quarantine"
LOCAL_ONLY_GITIGNORE = (
    "# SECURE_CHECK: this folder is generated and LOCAL-ONLY.\n"
    "# It must never be committed or pushed. This file makes git ignore the whole folder.\n"
    "*\n"
)
_local_only_done = set()


def _git_exclude_file(start):
    """Return <repo>/.git/info/exclude for the repo containing `start`, or None."""
    for d in [start] + list(start.parents):
        dot_git = d / ".git"
        if dot_git.is_dir():
            return d, dot_git / "info" / "exclude"
        if dot_git.is_file():  # worktree / submodule: "gitdir: <path>"
            try:
                line = dot_git.read_text(encoding="utf-8", errors="replace").strip()
            except OSError:
                return None
            if not line.startswith("gitdir:"):
                return None
            gitdir = Path(line[len("gitdir:"):].strip())
            if not gitdir.is_absolute():
                gitdir = (d / gitdir).resolve()
            common = gitdir / "commondir"
            if common.is_file():
                try:
                    gitdir = (gitdir / common.read_text(encoding="utf-8").strip()).resolve()
                except OSError:
                    pass
            return d, gitdir / "info" / "exclude"
    return None


def ensure_local_only(directory):
    """Keep SECURE_CHECK output out of git without touching tracked project files.

    1. Writes `<secure-check-report>/.gitignore` containing `*` (the folder ignores itself).
    2. Adds the report folder and `_quarantine/` to `.git/info/exclude` (local, never committed).

    Only acts when `directory` is, or is inside, a folder named `secure-check-report`, so a
    custom --out can never end up ignoring the project itself. Never raises.
    """
    try:
        directory = Path(directory).resolve()
        report = next((p for p in [directory] + list(directory.parents) if p.name == REPORT_DIR_NAME), None)
        if report is None or report in _local_only_done:
            return
        _local_only_done.add(report)
        report.mkdir(parents=True, exist_ok=True)
        gi = report / ".gitignore"
        if not gi.exists():
            gi.write_text(LOCAL_ONLY_GITIGNORE, encoding="utf-8")

        found = _git_exclude_file(report.parent)
        if not found:
            return
        repo_root, exclude = found
        project_rel = report.parent.relative_to(repo_root).as_posix()
        prefix = "/" if project_rel == "." else "/%s/" % project_rel
        wanted = [prefix + REPORT_DIR_NAME + "/", prefix + QUARANTINE_DIR_NAME + "/"]
        existing = exclude.read_text(encoding="utf-8", errors="replace").splitlines() if exclude.exists() else []
        missing = [w for w in wanted if w not in existing]
        if missing:
            exclude.parent.mkdir(parents=True, exist_ok=True)
            with open(exclude, "a", encoding="utf-8") as fh:
                if existing and existing[-1].strip():
                    fh.write("\n")
                fh.write("# SECURE_CHECK - generated, local-only (never commit or push)\n")
                fh.write("\n".join(missing) + "\n")
    except Exception as exc:  # protection is best effort; never break a scan
        print("(!) could not mark %s as local-only: %s" % (directory, exc), file=sys.stderr)


def tracked_outputs(root):
    """List SECURE_CHECK output files that git already tracks (they would be pushed)."""
    try:
        res = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--", REPORT_DIR_NAME, QUARANTINE_DIR_NAME],
            capture_output=True, text=True, timeout=30,
        )
    except Exception:
        return []
    if res.returncode != 0:
        return []
    return [line for line in res.stdout.splitlines() if line.strip()]


def make_finding(fid, severity, category, title, file=None, line=None, evidence=None,
                 source=None, confidence="medium", note=None):
    item = {
        "id": fid,
        "severity": severity,
        "category": category,
        "title": title,
        "file": file,
        "line": line,
        "status": "open",
        "source": source,
        "confidence": confidence,
        "verified": False,
    }
    if evidence:
        item["evidence"] = evidence
    if note:
        item["note"] = note
    return item


def severity_at_least(severity, threshold):
    return SEVERITY_ORDER.get(severity, 0) >= SEVERITY_ORDER.get(threshold, 99)


# --------------------------------------------------------------------------------------
# Git helpers (read-only commands only)
# --------------------------------------------------------------------------------------

def _git(root, args, stdin=None):
    try:
        res = subprocess.run(
            ["git", "-C", str(root)] + args,
            input=stdin, capture_output=True, text=True, timeout=60,
        )
        return res.returncode, res.stdout
    except (OSError, subprocess.SubprocessError):
        return 1, ""


def is_git_repo(root):
    code, out = _git(root, ["rev-parse", "--is-inside-work-tree"])
    return code == 0 and out.strip() == "true"


def git_tracked_files(root):
    code, out = _git(root, ["ls-files", "-z"])
    if code != 0:
        return set()
    return {p for p in out.split("\0") if p}


def git_ignored(root, rel_paths):
    if not rel_paths:
        return set()
    code, out = _git(root, ["check-ignore", "--stdin"], stdin="\n".join(rel_paths) + "\n")
    if code not in (0, 1):
        return set()
    return {line.strip() for line in out.splitlines() if line.strip()}


# --------------------------------------------------------------------------------------
# Classification heuristics (a first guess - the AI must confirm by reading the file)
# --------------------------------------------------------------------------------------

PRIVATE_NAME_PATTERNS = [
    ".env", ".env.*", "*.pem", "*.key", "*.p12", "*.pfx", "*.jks", "*.keystore",
    "key.properties", "id_rsa*", "id_dsa*", "id_ecdsa*", "id_ed25519*", "*.ppk",
    "service-account*.json", "*-firebase-adminsdk-*.json", "credentials*.json",
    "*.sql.gz", "*dump*.sql", "*backup*.sql", "*.dump", "*.bak", "*.backup",
    "*.sqlite", "*.sqlite3", "*.mdb", ".npmrc", ".pypirc", ".netrc", "*.tfvars",
    "terraform.tfstate*", "sftp-config.json", "sftp.json", ".ftpconfig", "master.key",
    "*.har", "passwords*", "*secret*.txt",
]
PRIVATE_EXCEPTIONS = {".env.example", ".env.sample", ".env.template", ".env.dist"}

CONFIG_NAMES = {
    "package.json", "tsconfig.json", "jsconfig.json", "composer.json", "pyproject.toml",
    "requirements.txt", "pipfile", "gemfile", "go.mod", "cargo.toml", "pubspec.yaml",
    "pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "dockerfile",
    "docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml",
    "firebase.json", "vercel.json", "netlify.toml", "wrangler.toml", "serverless.yml",
    "app.json", "app.config.js", "babel.config.js", ".babelrc", ".eslintrc", ".eslintrc.js",
    ".eslintrc.json", "eslint.config.js", ".prettierrc", "angular.json", "nx.json",
    "turbo.json", ".gitignore", ".dockerignore", ".htaccess", "web.config", "nginx.conf",
    "makefile", "procfile", "tauri.conf.json", "androidmanifest.xml", "info.plist",
    "appsettings.json", "application.properties", "application.yml", ".editorconfig",
}
CONFIG_PREFIXES = (
    "vite.config", "next.config", "nuxt.config", "svelte.config", "astro.config",
    "webpack.config", "rollup.config", "tailwind.config", "postcss.config", "jest.config",
    "vitest.config", "playwright.config", "karma.conf", "metro.config", "capacitor.config",
    "remix.config", "gatsby-config", "quasar.config", "appsettings.",
)

CLIENT_EXT = {".jsx", ".tsx", ".vue", ".svelte", ".astro", ".html", ".htm", ".css",
              ".scss", ".sass", ".less", ".dart"}

RE_DB_SERVER = re.compile(
    r"""(?:require\(|import\s[^\n]{0,80}?from\s|import\s)\s*['"](?:pg|pg-promise|postgres|mysql2?|mariadb|mongodb|mongoose|sequelize|typeorm|@prisma/client|knex|drizzle-orm[^'"]*|better-sqlite3|sqlite3|ioredis|redis|@neondatabase/serverless|@planetscale/database|firebase-admin[^'"]*)['"]"""
    r"""|^\s*(?:from|import)\s+(?:sqlalchemy|sqlmodel|django\.db|psycopg2?|psycopg|pymongo|motor|peewee|tortoise|MySQLdb|pymysql|sqlite3|asyncpg)\b"""
    r"""|\bnew\s+PDO\s*\(|\bmysqli_(?:connect|query|prepare)\b|\$wpdb->|\bDB::(?:table|select|statement|raw)\b"""
    r"""|\bextends\s+(?:Model|Eloquent)\b|@Entity\b|@Repository\b|\bDbContext\b|"database/sql"|gorm\.io/|\bCREATE\s+TABLE\b"""
    r"""|\bActiveRecord::|\bsupabase[^\n]{0,40}service_role""",
    re.IGNORECASE | re.MULTILINE,
)

RE_STORAGE_SERVER = re.compile(
    r"""['"](?:@aws-sdk/client-s3|@aws-sdk/s3-request-presigner|aws-sdk|@google-cloud/storage|@azure/storage-blob|cloudinary|multer|busboy|formidable|@fastify/multipart|express-fileupload|sharp)['"]"""
    r"""|^\s*(?:from|import)\s+(?:boto3|botocore|google\.cloud\s+import\s+storage|google\.cloud\.storage|azure\.storage\.blob|cloudinary|storages)\b"""
    r"""|\bmove_uploaded_file\s*\(|\bStorage::(?:disk|put|putFile|temporaryUrl)\b|\brequest\.files\b|\bUploadFile\b|\bIFormFile\b|\bMultipartFile\b"""
    r"""|\bgetSignedUrl\b|\bgenerate_presigned_url\b|\bcreatePresignedPost\b|\bhas_one_attached\b|\bhas_many_attached\b""",
    re.IGNORECASE | re.MULTILINE,
)

RE_SERVER = re.compile(
    r"""['"](?:express|fastify|koa|hono|@nestjs/[a-z-]+|next/server|server-only|nodemailer|jsonwebtoken|bcrypt|bcryptjs|argon2|stripe|twilio|@sendgrid/mail|firebase-functions[^'"]*|@hapi/hapi|child_process|node:child_process|fs|node:fs)['"]"""
    r"""|^\s*['"]use server['"]|^\s*(?:from|import)\s+(?:django|flask|fastapi|starlette|smtplib|subprocess)\b"""
    r"""|\bos\.environ\b|\bgetenv\s*\(|\$_(?:GET|POST|REQUEST|SERVER|COOKIE|FILES|ENV)\b|@RestController|@Controller\b|\[ApiController\]|\bhttp\.HandleFunc\b|\bgin\.Default\(|\bexports\.handler\b|\bexport\s+(?:async\s+)?function\s+(?:GET|POST|PUT|PATCH|DELETE)\b""",
    re.MULTILINE,
)

RE_CLIENT = re.compile(
    r"""^\s*['"]use client['"]|\bdocument\.(?:getElementById|querySelector|createElement|addEventListener|body)\b|\bwindow\.(?:location|addEventListener|localStorage|sessionStorage)\b|\blocalStorage\.|\buseState\s*\(|\buseEffect\s*\(|\bReactDOM\b|from\s+['"]react-native['"]|@Component\s*\(|\bdefineComponent\s*\(|\bStatelessWidget\b|\bStatefulWidget\b""",
    re.MULTILINE,
)

PUBLIC_ENV_PREFIX = r"(?:NEXT_PUBLIC_|VITE_|REACT_APP_|EXPO_PUBLIC_|NUXT_PUBLIC_|PUBLIC_|GATSBY_|VUE_APP_|NODE_ENV\b)"
RE_PRIVATE_ENV = re.compile(
    r"\bprocess\.env\.(?!" + PUBLIC_ENV_PREFIX + r")[A-Z][A-Z0-9_]*|\bprocess\.env\[['\"](?!" + PUBLIC_ENV_PREFIX + r")[A-Z][A-Z0-9_]*"
)


def is_private_name(name):
    lname = name.lower()
    if lname in PRIVATE_EXCEPTIONS:
        return False
    return any(fnmatch.fnmatch(lname, pat) for pat in PRIVATE_NAME_PATTERNS)


def is_test_path(rel):
    lrel = rel.lower()
    name = lrel.rsplit("/", 1)[-1]
    return (
        "/__tests__/" in "/" + lrel or "/tests/" in "/" + lrel or "/test/" in "/" + lrel
        or "/spec/" in "/" + lrel or "/fixtures/" in "/" + lrel or "/e2e/" in "/" + lrel
        or re.search(r"[._-](test|spec)\.[a-z]+$", name) is not None
        or name.startswith("test_") or name.endswith("_test.go") or name.endswith("_test.py")
    )


def guess_label(rel, text):
    """Return (label, signals, flags). A heuristic first guess only."""
    name = rel.rsplit("/", 1)[-1]
    lname = name.lower()
    ext = os.path.splitext(lname)[1]
    signals, flags = [], []
    text = text or ""

    if in_build_dir(rel):
        return "GENERATED", ["build-output"], flags
    if is_private_name(name):
        if in_public_dir(rel):
            flags.append("PUBLIC-EXPOSED")
        return "PRIVATE", ["private-file-name"], flags
    if is_test_path(rel):
        return "TEST", ["test-path"], flags
    if ext in {".md", ".rst", ".adoc"} or rel.lower().startswith("docs/"):
        return "DOCS", ["docs"], flags
    if lname in CONFIG_NAMES or lname.startswith(CONFIG_PREFIXES) or rel.startswith(".github/"):
        return "CONFIG", ["config-file"], flags
    if lname.endswith((".rules", "firestore.rules", "storage.rules")) or lname == "database.rules.json":
        return ("BE:STORAGE" if "storage" in lname else "BE:DB"), ["baas-rules"], flags

    db = bool(RE_DB_SERVER.search(text))
    storage = bool(RE_STORAGE_SERVER.search(text))
    server = bool(RE_SERVER.search(text))
    client = bool(RE_CLIENT.search(text)) or ext in CLIENT_EXT or in_public_dir(rel)
    private_env = bool(RE_PRIVATE_ENV.search(text))
    if db:
        signals.append("db-driver")
    if storage:
        signals.append("storage-sdk")
    if server:
        signals.append("server-api")
    if client:
        signals.append("client-code")
    if private_env:
        signals.append("private-env")

    server_path = re.search(
        r"(^|/)(server|backend|api|functions|netlify/functions|supabase/functions|app/api|pages/api|routes|controllers|services|middlewares?|models|repositories|migrations|lib/server)(/|$)",
        rel.lower(),
    )
    if ext == ".php" and not in_public_dir(rel):
        server = True

    if client and not server_path:
        if db or (private_env and not ext == ".dart"):
            flags.append("MOVE")
        if db:
            flags.append("SECRET?")
        return "FE", signals, flags
    if db or "/migrations/" in "/" + rel.lower() or ext == ".sql":
        return "BE:DB", signals, flags
    if storage:
        return "BE:STORAGE", signals, flags
    if server or server_path or private_env:
        return "BE", signals, flags
    if re.search(r"(^|/)(types?|shared|common|constants?)(/|$)", rel.lower()) or lname.endswith(".d.ts"):
        return "SHARED", signals, flags
    if ext in CODE_EXT and re.search(r"(^|/)(src|app|components|pages|views|screens|lib)(/|$)", rel.lower()):
        return "FE", signals + ["frontend-path"], flags
    return "CONFIRM?", signals, flags
