#!/usr/bin/env python3
"""SECURE_CHECK - project inventory.

Lists files, detects the stack and deploy targets, and gives every file a FIRST-GUESS
label (FE, BE, BE:DB, BE:STORAGE, SHARED, CONFIG, PRIVATE, GENERATED, DOCS, TEST,
CONFIRM?). The AI must confirm labels by reading the files.

Usage:
  python inventory.py <project_dir> [--out DIR]
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    count_lines, guess_label, is_binary, iter_files, read_text, setup_console, write_json,
)

JS_MARKERS = [
    ("next", "Next.js"), ("nuxt", "Nuxt"), ("@sveltejs/kit", "SvelteKit"), ("svelte", "Svelte"),
    ("@angular/core", "Angular"), ("vue", "Vue"), ("astro", "Astro"), ("gatsby", "Gatsby"),
    ("@remix-run/react", "Remix"), ("react-router", "React Router"), ("react-native", "React Native"),
    ("expo", "Expo"), ("react", "React"), ("vite", "Vite"), ("react-scripts", "Create React App"),
    ("electron", "Electron"), ("@tauri-apps/api", "Tauri"), ("@nestjs/core", "NestJS"),
    ("express", "Express"), ("fastify", "Fastify"), ("koa", "Koa"), ("hono", "Hono"),
    ("@prisma/client", "Prisma"), ("drizzle-orm", "Drizzle"), ("mongoose", "Mongoose"),
    ("sequelize", "Sequelize"), ("typeorm", "TypeORM"), ("pg", "PostgreSQL driver"),
    ("mysql2", "MySQL driver"), ("firebase", "Firebase (client)"), ("firebase-admin", "Firebase Admin"),
    ("@supabase/supabase-js", "Supabase"), ("@aws-sdk/client-s3", "AWS S3"), ("cloudinary", "Cloudinary"),
    ("multer", "Multer uploads"), ("stripe", "Stripe"), ("nodemailer", "Nodemailer"),
    ("@ionic/core", "Ionic"), ("@capacitor/core", "Capacitor"),
]
PY_MARKERS = [("django", "Django"), ("djangorestframework", "Django REST Framework"), ("flask", "Flask"),
              ("fastapi", "FastAPI"), ("sqlalchemy", "SQLAlchemy"), ("boto3", "AWS SDK (boto3)"),
              ("celery", "Celery"), ("streamlit", "Streamlit")]
FILE_MARKERS = [
    ("composer.json", "PHP (Composer)"), ("artisan", "Laravel"), ("wp-config.php", "WordPress"),
    ("wp-config-sample.php", "WordPress"), ("Gemfile", "Ruby"), ("config/routes.rb", "Rails"),
    ("pom.xml", "Java (Maven)"), ("build.gradle", "Gradle"), ("build.gradle.kts", "Gradle (Kotlin)"),
    ("go.mod", "Go"), ("Cargo.toml", "Rust"), ("pubspec.yaml", "Flutter/Dart"),
    ("src-tauri/tauri.conf.json", "Tauri"), ("firebase.json", "Firebase"), ("firestore.rules", "Firestore rules"),
    ("storage.rules", "Firebase Storage rules"), ("supabase/config.toml", "Supabase"),
    ("vercel.json", "Vercel"), ("netlify.toml", "Netlify"), ("wrangler.toml", "Cloudflare Workers"),
    ("serverless.yml", "Serverless Framework"), ("Dockerfile", "Docker"), ("docker-compose.yml", "Docker Compose"),
    ("compose.yaml", "Docker Compose"), (".github/workflows", "GitHub Actions"), ("app/src/main/AndroidManifest.xml", "Android"),
    ("android/app/src/main/AndroidManifest.xml", "Android (in cross-platform app)"), ("ios", "iOS folder"),
    ("manage.py", "Django"), ("index.html", "HTML entry"), ("index.php", "PHP entry"),
]


def detect_stack(root, rels):
    stack = []
    for pkg in [root / "package.json"] + [root / p for p in rels if p.endswith("/package.json") and p.count("/") <= 2]:
        if not pkg.exists():
            continue
        try:
            data = json.loads(pkg.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        deps = {}
        for key in ("dependencies", "devDependencies", "peerDependencies"):
            deps.update(data.get(key) or {})
        where = pkg.parent.relative_to(root).as_posix()
        for dep, name in JS_MARKERS:
            if dep in deps:
                stack.append("%s%s" % (name, "" if where == "." else " (%s)" % where))
    py_text = ""
    for name in ("requirements.txt", "pyproject.toml", "Pipfile", "setup.py"):
        p = root / name
        if p.exists():
            py_text += p.read_text(encoding="utf-8", errors="replace").lower()
    for dep, name in PY_MARKERS:
        if re.search(r"(^|[\s\"'\[])" + re.escape(dep) + r"\b", py_text, re.M):
            stack.append(name)
    cs = [r for r in rels if r.endswith(".csproj")]
    if cs:
        stack.append(".NET (%s)" % cs[0])
    for marker, name in FILE_MARKERS:
        if (root / marker).exists():
            stack.append(name)
    if not stack and any(r.endswith((".html", ".htm")) for r in rels):
        stack.append("Static website")
    out, seen = [], set()
    for s in stack:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def run(root):
    root = Path(root).resolve()
    files = []
    ext_counter = Counter()
    label_counter = Counter()
    for rel, path, in_build in iter_files(root):
        ext = path.suffix.lower() or "(none)"
        ext_counter[ext] += 1
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        binary = is_binary(path)
        text = None if binary else read_text(path, max_bytes=3_000_000)
        label, signals, flags = guess_label(rel, text)
        label_counter[label] += 1
        files.append({
            "path": rel, "bytes": size, "lines": count_lines(text) if text else 0,
            "binary": binary, "label_guess": label, "signals": signals, "flags_guess": flags,
        })
    rels = [f["path"] for f in files]
    largest = sorted((f for f in files if not f["binary"]), key=lambda f: -f["lines"])[:15]
    top_dirs = Counter(r.split("/")[0] if "/" in r else "." for r in rels)
    return {
        "scanner": "inventory",
        "root": str(root),
        "total_files": len(files),
        "stack": detect_stack(root, rels),
        "top_level": dict(top_dirs.most_common()),
        "extensions": dict(ext_counter.most_common(25)),
        "labels_guess": dict(label_counter.most_common()),
        "largest_text_files": [{"path": f["path"], "lines": f["lines"]} for f in largest],
        "flagged": [f for f in files if f["flags_guess"]],
        "files": files,
    }


def print_report(result):
    print("== SECURE_CHECK inventory ==")
    print("  root : %s" % result["root"])
    print("  files: %d (dependencies, VCS and build output excluded)" % result["total_files"])
    print("  stack: %s" % (", ".join(result["stack"]) or "unknown"))
    print("  labels (first guess): " + ", ".join("%s=%d" % kv for kv in result["labels_guess"].items()))
    print("  largest files:")
    for f in result["largest_text_files"][:8]:
        print("    %6d  %s" % (f["lines"], f["path"]))
    if result["flagged"]:
        print("  flagged by heuristics:")
        for f in result["flagged"][:20]:
            print("    %-10s %-8s %s  (%s)" % (f["label_guess"], ",".join(f["flags_guess"]), f["path"], ",".join(f["signals"])))


def main(argv=None):
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    ap.add_argument("--out")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    result = run(args.root)
    if args.out:
        write_json(Path(args.out) / "inventory.json", result)
    if not args.quiet:
        print_report(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
