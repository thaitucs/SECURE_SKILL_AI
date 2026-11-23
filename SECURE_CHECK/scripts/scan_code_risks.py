#!/usr/bin/env python3
"""SECURE_CHECK - risky code patterns (injection, XSS, auth/crypto mistakes).

Pattern-based hints for the manual review in workflow step 4. Every hit is a LEAD with
low/medium confidence: open the file, follow the data flow, and only report it if user
input can really reach the dangerous call.

Usage:
  python scan_code_risks.py <project_dir> [--out DIR]
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    guess_label, iter_files, make_finding, read_text, setup_console, write_json, SEVERITY_ORDER,
)

CODE_EXT = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".vue", ".svelte", ".astro", ".py", ".php",
            ".rb", ".java", ".kt", ".go", ".cs", ".dart", ".html", ".htm", ".erb", ".ejs", ".hbs",
            ".twig", ".cshtml", ".jsp"}

INPUT = r"(?:req\.(?:body|query|params|headers|cookies)|request\.(?:GET|POST|args|form|json|data|query_params|body)|\$_(?:GET|POST|REQUEST|COOKIE|SERVER)|params\[|ctx\.(?:query|params|request)|searchParams|location\.(?:search|hash)|input\(|getParameter\()"

RULES = [
    # (title, regex, severity, category, confidence)
    ("SQL built by string concatenation/interpolation",
     r"""(?i)(?:query|execute|exec|raw|prepare|cursor\.execute|db\.(?:query|run|all|get))\s*\(\s*(?:f["']|["'`][^"'`]*\b(?:SELECT|INSERT|UPDATE|DELETE)\b[^"'`]*["'`]\s*(?:\+|%|\.format)|`[^`]*\b(?:SELECT|INSERT|UPDATE|DELETE)\b[^`]*\$\{)""",
     "high", "injection", "medium"),
    ("SQL with request input in the same expression",
     r"(?i)\b(?:SELECT|INSERT|UPDATE|DELETE)\b[^;\n]{0,120}(?:\+|\.|\$\{|%s|\{)\s*" + INPUT,
     "critical", "injection", "medium"),
    ("ORM raw query method (check for interpolation)",
     r"\$queryRawUnsafe|\$executeRawUnsafe|sequelize\.query\(\s*`|knex\.raw\(\s*`|whereRaw\(\s*[\"'][^\"']*[\"']\s*\.|DB::raw\(\s*[\"'][^\"']*\$|\.extra\(\s*where|RawSQL\(|FromSqlRaw\(\s*\$?\"|createNativeQuery\(\s*\"[^\"]*\"\s*\+",
     "medium", "injection", "low"),
    ("Shell command with possible user input",
     r"(?:child_process\.)?\bexec(?:Sync)?\s*\(\s*(?:`[^`]*\$\{|[^)]*\+)|subprocess\.\w+\([^)]*shell\s*=\s*True|os\.system\s*\(|\b(?:shell_exec|system|passthru|popen|proc_open)\s*\(\s*\$|Runtime\.getRuntime\(\)\.exec\(|exec\.Command\(\s*\"(?:sh|bash|cmd)\"",
     "high", "injection", "medium"),
    ("eval / dynamic code execution",
     r"(?<![\w.])eval\s*\(|new\s+Function\s*\(|setTimeout\s*\(\s*[\"'`]|vm\.runIn\w+Context\(|\bassert\s*\(\s*\$|preg_replace\s*\([^)]*/e[\"']",
     "high", "injection", "medium"),
    ("HTML injection sink (XSS risk)",
     r"dangerouslySetInnerHTML|\.innerHTML\s*=|\.outerHTML\s*=|insertAdjacentHTML\(|document\.write\(|v-html=|\{@html\s|\[innerHTML\]|bypassSecurityTrust\w+\(|\|\s*safe\b|mark_safe\(|\{!!\s*\$|\.html_safe\b|<%==|Html\.Raw\(|set:html=",
     "medium", "injection", "low"),
    ("Server-side template rendered from a string (SSTI risk)",
     r"render_template_string\s*\(|Template\s*\(\s*request\.|ejs\.render\s*\(\s*req\.|Handlebars\.compile\s*\(\s*req\.",
     "high", "injection", "medium"),
    ("Unsafe deserialization",
     r"pickle\.loads?\s*\(|cPickle\.loads?\(|yaml\.load\s*\((?![^)]*SafeLoader)|\bunserialize\s*\(\s*\$|ObjectInputStream\s*\(|BinaryFormatter|node-serialize|jsonpickle\.decode",
     "high", "injection", "medium"),
    ("File path built from request input (path traversal)",
     r"(?:sendFile|readFile|readFileSync|createReadStream|open|send_file|file_get_contents|fopen|include|require_once|include_once|File\.ReadAll\w+|http\.ServeFile)\s*\([^)]*" + INPUT,
     "high", "injection", "medium"),
    ("Server-side request to a URL from user input (SSRF)",
     r"(?:fetch|axios\.(?:get|post)|requests\.(?:get|post)|urllib\.request\.urlopen|http\.Get|file_get_contents|curl_setopt\([^,]+,\s*CURLOPT_URL)\s*\([^)]*" + INPUT,
     "high", "injection", "medium"),
    ("Open redirect from user input",
     r"(?:res\.redirect|redirect|header\(\s*[\"']Location:)\s*\(?[^)\n]*" + INPUT,
     "medium", "injection", "low"),
    ("Weak password hashing (MD5/SHA1/plain)",
     r"(?i)(?:md5|sha1)\s*\([^)]*pass|hashlib\.(?:md5|sha1)\([^)]*pass|createHash\(\s*['\"](?:md5|sha1)['\"]\)[^\n]{0,60}pass|password\s*==\s*(?:req|request|\$_POST)",
     "high", "auth", "medium"),
    ("JWT decoded without verification / algorithm not pinned",
     r"jwt\.decode\s*\([^)]*(?:verify\s*=\s*False|options\s*=\s*\{[^}]*verify_signature[^}]*False)|algorithms\s*[:=]\s*\[\s*['\"]none['\"]|jwt\.verify\s*\(\s*[^,]+,\s*[^,)]+\s*\)",
     "medium", "auth", "low"),
    ("Insecure random used for tokens/passwords",
     r"(?i)(?:token|secret|password|otp|code|nonce|salt)\w*\s*[:=][^\n]{0,40}(?:Math\.random\(\)|\brand\(\)|mt_rand\(|uniqid\(|random\.random\(|random\.randint\()",
     "medium", "auth", "medium"),
    ("Role/permission check in frontend code (must be enforced by backend)",
     r"(?:user|currentUser|session|auth)\??\.(?:role|isAdmin|is_admin|permissions)\s*(?:===?|!==?|\.includes)",
     "low", "auth", "low"),
    ("Mass assignment (whole request body saved)",
     r"(?:create|update|insert|save|findByIdAndUpdate|updateOne|fill|forceFill)\s*\(\s*(?:req\.body|request\.(?:data|json|POST)|\$request->all\(\)|\$_POST)\s*[,)]|\$guarded\s*=\s*\[\s*\]|fields\s*=\s*['\"]__all__['\"]|params\.permit!",
     "medium", "auth", "medium"),
    ("CSRF protection disabled",
     r"@csrf_exempt|csrf\(\)\.disable\(\)|csrf\s*:\s*false|verify_authenticity_token|IgnoreAntiforgeryToken|WTF_CSRF_ENABLED\s*=\s*False",
     "medium", "config", "medium"),
    ("Stack trace / error details sent to the client",
     r"res\.(?:send|json|status\(\d+\)\.(?:send|json))\s*\(\s*(?:err|error)(?:\.stack)?\s*\)|traceback\.format_exc\(\)[^\n]{0,40}(?:return|Response|jsonify)",
     "low", "config", "low"),
]
COMPILED = [(t, re.compile(rx, re.M), s, c, conf) for t, rx, s, c, conf in RULES]
FRONTEND_ONLY = {"Role/permission check in frontend code (must be enforced by backend)"}


def run(root, limit_per_rule=25):
    root = Path(root).resolve()
    findings, counts = [], {}
    n = 0
    for rel, path, _b in iter_files(root):
        ext = Path(rel).suffix.lower()
        if ext not in CODE_EXT or rel.endswith(".min.js"):
            continue
        text = read_text(path, max_bytes=2_000_000)
        if not text:
            continue
        label, _s, _f = guess_label(rel, text)
        if label in ("TEST", "GENERATED", "DOCS"):
            continue
        for title, rx, sev, cat, conf in COMPILED:
            if title in FRONTEND_ONLY and label != "FE":
                continue
            for m in rx.finditer(text):
                if counts.get(title, 0) >= limit_per_rule:
                    break
                line = text.count("\n", 0, m.start()) + 1
                snippet = text.splitlines()[line - 1].strip()[:160]
                n += 1
                counts[title] = counts.get(title, 0) + 1
                findings.append(make_finding("SCAN-CODE-%03d" % n, sev, cat, title, file=rel, line=line,
                                             evidence=snippet, source="scan_code_risks", confidence=conf))
                break  # one hit per rule per file is enough to point the reviewer
    findings.sort(key=lambda f: (-SEVERITY_ORDER[f["severity"]], f["file"], f["line"]))
    return {"scanner": "scan_code_risks", "root": str(root), "findings": findings,
            "note": "Pattern hints only. Confirm data flow from user input before reporting."}


def print_report(result, limit=60):
    f = result["findings"]
    print("== SECURE_CHECK scan_code_risks: %d lead(s) ==" % len(f))
    for item in f[:limit]:
        print("  [%-8s] %s:%s  %s" % (item["severity"].upper(), item["file"], item["line"], item["title"]))
        print("             " + item.get("evidence", "")[:110])
    if len(f) > limit:
        print("  ... %d more in JSON output" % (len(f) - limit))


def main(argv=None):
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    ap.add_argument("--out")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    result = run(args.root)
    if args.out:
        write_json(Path(args.out) / "code-risks.json", result)
    if not args.quiet:
        print_report(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
