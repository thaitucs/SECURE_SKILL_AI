#!/usr/bin/env python3
"""SECURE_CHECK - secret scanner.

Finds hard-coded keys, tokens, passwords and private keys in source, config and build
output. Values are always masked in the output. Hits are LEADS: confirm each one by
reading the code before reporting it as a finding.

Usage:
  python scan_secrets.py <project_dir> [--out DIR] [--fail-on critical|high|medium|low]
  python scan_secrets.py --files a.js b.py ...   (e.g. from a pre-commit hook)
"""
import argparse
import base64
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    guess_label, in_build_dir, in_public_dir, iter_files, make_finding, mask, read_text,
    setup_console, severity_at_least, shannon_entropy, write_json, SEVERITY_ORDER,
)

# (name, regex, severity, group index holding the secret value or 0 for whole match)
PATTERNS = [
    ("Private key block", r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY-----", "critical", 0),
    ("AWS access key id", r"\b((?:AKIA|ASIA)[0-9A-Z]{16})\b", "high", 1),
    ("AWS secret access key", r"(?i)aws.{0,20}(?:secret|private).{0,20}['\"=:\s]([0-9a-zA-Z/+]{40})\b", "critical", 1),
    ("Google OAuth client secret", r"\b(GOCSPX-[0-9A-Za-z_\-]{28})\b", "critical", 1),
    ("GCP/Firebase service account", r"\"type\"\s*:\s*\"service_account\"", "critical", 0),
    ("GitHub token", r"\b((?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{60,})\b", "critical", 1),
    ("GitLab token", r"\b(glpat-[A-Za-z0-9_\-]{20,})\b", "critical", 1),
    ("Slack token", r"\b(xox[baprs]-[A-Za-z0-9-]{10,})\b", "high", 1),
    ("Slack webhook", r"(https://hooks\.slack\.com/services/[A-Za-z0-9/]+)", "medium", 1),
    ("Discord webhook", r"(https://(?:discord|discordapp)\.com/api/webhooks/\d+/[\w-]+)", "medium", 1),
    ("Stripe live secret/restricted key", r"\b((?:sk|rk)_live_[0-9a-zA-Z]{20,})\b", "critical", 1),
    ("Stripe test secret key", r"\b(sk_test_[0-9a-zA-Z]{20,})\b", "high", 1),
    ("Stripe webhook secret", r"\b(whsec_[0-9a-zA-Z]{20,})\b", "high", 1),
    ("Anthropic API key", r"\b(sk-ant-[A-Za-z0-9_\-]{20,})\b", "critical", 1),
    ("OpenAI API key", r"\b(sk-(?:proj-|svcacct-|admin-)?[A-Za-z0-9_\-]{20,})\b", "critical", 1),
    ("Hugging Face token", r"\b(hf_[A-Za-z0-9]{30,})\b", "high", 1),
    ("Twilio API key", r"\b(SK[0-9a-fA-F]{32})\b", "high", 1),
    ("SendGrid API key", r"\b(SG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43})\b", "critical", 1),
    ("Mailgun API key", r"\b(key-[0-9a-zA-Z]{32})\b", "critical", 1),
    ("Mailchimp API key", r"\b([0-9a-f]{32}-us\d{1,2})\b", "high", 1),
    ("Telegram bot token", r"\b(\d{8,10}:AA[A-Za-z0-9_\-]{33})\b", "high", 1),
    ("npm token", r"\b(npm_[A-Za-z0-9]{36})\b", "critical", 1),
    ("PyPI token", r"\b(pypi-AgEIcHlwaS5vcmc[A-Za-z0-9_\-]{50,})\b", "critical", 1),
    ("Shopify token", r"\b(shp(?:at|ca|pa|ss)_[a-fA-F0-9]{32})\b", "critical", 1),
    ("Square token", r"\b(EAAA[A-Za-z0-9_\-]{60}|sq0csp-[0-9A-Za-z_\-]{43})\b", "critical", 1),
    ("Braintree/PayPal token", r"(access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32})", "critical", 1),
    ("Azure storage account key", r"(AccountKey=[A-Za-z0-9+/=]{80,})", "critical", 1),
    ("Mapbox secret token", r"\b(sk\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+)", "high", 1),
    ("Cloudinary URL with secret", r"(cloudinary://\d+:[A-Za-z0-9_\-]+@[\w-]+)", "critical", 1),
    ("Database URL with password",
     r"((?:postgres(?:ql)?|mysql|mariadb|mongodb(?:\+srv)?|redis|rediss|amqps?|mssql|sqlserver)://[^:\s/'\"]+:([^@\s'\"]+)@[^\s'\"]+)", "critical", 2),
    ("Credentials in URL", r"(https?://[^:\s/'\"@]+:([^@\s'\"]{3,})@[\w.-]+)", "high", 2),
    ("Google API key", r"\b(AIza[0-9A-Za-z_\-]{35})\b", "medium", 1),
    ("JWT", r"\b(eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,})\b", "medium", 1),
]
COMPILED = [(n, re.compile(p), s, g) for n, p, s, g in PATTERNS]

RE_GENERIC = re.compile(
    r"""(?i)\b([a-z0-9_.-]*(?:password|passwd|pwd|secret|token|api[_-]?key|apikey|access[_-]?key|private[_-]?key|client[_-]?secret|auth[_-]?key|credential|smtp[_-]?pass|db[_-]?pass)[a-z0-9_.-]*)\b["']?\s*(?:=|:|=>|:=)\s*["']([^"'\s]{8,})["']"""
)

PLACEHOLDER = re.compile(
    r"(?i)^(?:x+|\*+|\.+|0+|<.*>|\{\{.*\}\}|\$\{.*\}|%\(.*\)s|your[_-].*|change[_-]?me.*|example.*|sample.*|dummy.*|test(?:ing)?|placeholder.*|todo.*|fake.*|none|null|undefined|secret|password|redacted|replace.*|insert.*|enter.*|process\.env.*|env\(.*\)|os\.environ.*|getenv.*)$"
)
CODE_VALUE = re.compile(r"^(?:[A-Za-z_][\w.]*\(.*\)?|[A-Za-z_][\w]*\.[\w.]+)$")  # looks like code, not a literal

PUBLIC_BY_DESIGN_HINT = {
    "Google API key": "Google/Firebase browser keys are public by design - check API & referrer restrictions and Firebase rules.",
    "JWT": "Decode the payload: a Supabase anon key is public, a service_role key is critical.",
}

SKIP_ENV_NAMES = re.compile(r"^\.env(\.[\w-]+)?$")
ENV_EXAMPLE = {".env.example", ".env.sample", ".env.template", ".env.dist"}


def jwt_role(token):
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload.encode()).decode("utf-8", "replace"))
        return data.get("role") or data.get("roles")
    except Exception:
        return None


def context_of(rel, text):
    label, _signals, _flags = guess_label(rel, text)
    where = []
    if in_build_dir(rel):
        where.append("build output (shipped to users if deployed)")
    if in_public_dir(rel):
        where.append("public folder")
    if label == "FE":
        where.append("frontend code")
    return label, where


def bump(severity, steps=1):
    order = ["info", "low", "medium", "high", "critical"]
    return order[min(len(order) - 1, order.index(severity) + steps)]


def scan_text(rel, text):
    hits = []
    seen = set()
    label, where = context_of(rel, text)
    is_test = label == "TEST"
    lines = text.splitlines()
    for lineno, line in enumerate(lines, 1):
        if len(line) > 5000:
            line = line[:5000]
        for name, rx, sev, group in COMPILED:
            for m in rx.finditer(line):
                value = m.group(group) if group else m.group(0)
                if not value or PLACEHOLDER.match(value) or "****" in value:
                    continue
                severity = sev
                note = PUBLIC_BY_DESIGN_HINT.get(name)
                if name == "JWT":
                    role = jwt_role(value)
                    if role == "service_role":
                        severity, note = "critical", "Supabase service_role key - full database access, server only."
                    elif role == "anon":
                        severity, note = "info", "Supabase anon key - public by design; make sure RLS is enabled."
                if name == "OpenAI API key" and value.startswith("sk-ant-"):
                    continue
                if where and severity in ("high", "medium") and name not in PUBLIC_BY_DESIGN_HINT:
                    severity = bump(severity)
                if is_test and severity == "critical":
                    severity = "high"
                key = (name, mask(value), lineno)
                if key in seen:
                    continue
                seen.add(key)
                hits.append((severity, name, lineno, mask(value), where, note))
        for m in RE_GENERIC.finditer(line):
            var, value = m.group(1), m.group(2)
            if PLACEHOLDER.match(value) or CODE_VALUE.match(value) or "..." in value or "****" in value:
                continue
            if any(k[2] == lineno for k in seen):
                continue  # already matched by a provider pattern
            ent = shannon_entropy(value)
            if ent < 3.0 and len(value) < 12:
                continue
            severity = "high" if ent >= 3.5 else "medium"
            if where:
                severity = bump(severity)
            if is_test:
                severity = "low"
            seen.add(("generic", mask(value), lineno))
            hits.append((severity, "Hard-coded value for '%s'" % var, lineno, mask(value), where,
                         "Generic match - confirm it is a real secret."))
    return hits


def scan_paths(items):
    findings, skipped_env = [], []
    counter = 0
    for rel, path in items:
        name = rel.rsplit("/", 1)[-1]
        if SKIP_ENV_NAMES.match(name) and name.lower() not in ENV_EXAMPLE:
            skipped_env.append(rel)
            continue
        if name.endswith(".lock") or name in ("package-lock.json", "yarn.lock", "pnpm-lock.yaml"):
            continue
        text = read_text(path)
        if text is None:
            continue
        for severity, title, lineno, masked, where, note in scan_text(rel, text):
            counter += 1
            full_title = title + (" in " + ", ".join(where) if where else "")
            findings.append(make_finding(
                "SCAN-SEC-%03d" % counter, severity, "secrets", full_title, file=rel, line=lineno,
                evidence=masked, source="scan_secrets", confidence="high" if not title.startswith("Hard-coded") else "medium",
                note=note,
            ))
    findings.sort(key=lambda f: (-SEVERITY_ORDER[f["severity"]], f["file"], f["line"] or 0))
    return findings, skipped_env


def run(root=None, files=None):
    if files:
        items = [(Path(f).as_posix(), Path(f)) for f in files if Path(f).is_file()]
    else:
        items = [(rel, p) for rel, p, _b in iter_files(root, include_build=True)]
    findings, skipped_env = scan_paths(items)
    return {
        "scanner": "scan_secrets",
        "root": str(root) if root else None,
        "skipped_env_files": skipped_env,
        "skipped_env_note": ".env files are expected to hold secrets; scan_exposure checks they are not tracked or public.",
        "findings": findings,
    }


def print_report(result, limit=60):
    f = result["findings"]
    print("== SECURE_CHECK scan_secrets: %d lead(s) ==" % len(f))
    for item in f[:limit]:
        print("  [%-8s] %s:%s  %s  (%s)" % (item["severity"].upper(), item["file"], item["line"],
                                           item["title"], item.get("evidence", "")))
        if item.get("note"):
            print("             note: " + item["note"])
    if len(f) > limit:
        print("  ... %d more in JSON output" % (len(f) - limit))
    if result["skipped_env_files"]:
        print("  (i) .env files not scanned line by line: " + ", ".join(result["skipped_env_files"][:10]))


def main(argv=None):
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", help="project directory")
    ap.add_argument("--files", nargs="+", help="scan only these files")
    ap.add_argument("--out", help="directory for secrets.json")
    ap.add_argument("--fail-on", choices=["critical", "high", "medium", "low"], help="exit 1 if a lead of this severity or higher exists")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    if not args.root and not args.files:
        ap.error("give a project directory or --files")
    result = run(root=Path(args.root).resolve() if args.root else None, files=args.files)
    if args.out:
        write_json(Path(args.out) / "secrets.json", result)
    if not args.quiet:
        print_report(result)
    if args.fail_on and any(severity_at_least(x["severity"], args.fail_on) for x in result["findings"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
