#!/usr/bin/env python3
"""SECURE_CHECK - code splitting candidates.

There is NO fixed line limit. A file is a candidate when it mixes responsibilities
(UI + HTTP + business logic + database + storage + messaging), or when it is much larger
than what is normal *for this project*. The output suggests which parts each file could be
split into. The AI must read the file and decide.

Usage:
  python find_split_candidates.py <project_dir> [--out DIR] [--top N]
"""
import argparse
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    RE_DB_SERVER, RE_STORAGE_SERVER, count_lines, guess_label, iter_files, read_text,
    setup_console, write_json,
)

SPLIT_EXT = {
    ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".vue", ".svelte", ".astro", ".py", ".php",
    ".rb", ".java", ".kt", ".go", ".cs", ".swift", ".dart", ".rs", ".ex", ".css", ".scss",
}

CONCERNS = {
    "ui": re.compile(r"return\s*\(\s*<|<(?:div|span|button|form|input|section|header|main|ul|table|img|View|Text)\b|<template>|@Component\s*\(|Widget\s+build\s*\(|\bsetState\s*\(|render\s*\(\s*\)\s*{|\bbody:\s*\w+\(|\bView\s*{", re.I),
    "api_client": re.compile(r"\bfetch\s*\(|\baxios\b|\$http\.|\bHttpClient\b|\buseQuery\s*\(|\buseSWR\s*\(|\bhttp\.(?:get|post)\s*\(|\bDio\s*\("),
    "http_server": re.compile(r"\b(?:app|router|server)\.(?:get|post|put|patch|delete|use|route)\s*\(|@app\.(?:route|get|post|put|delete)|@router\.(?:get|post|put|delete)|Route::(?:get|post|put|delete|resource)|\$_(?:GET|POST|REQUEST)\b|\breq\.(?:body|params|query)\b|\brequest\.(?:json|form|args|POST|GET)\b|@(?:Get|Post|Put|Delete|Patch)Mapping|@(?:Get|Post|Put|Delete|Controller)\(|\bc\.(?:JSON|Bind)\(|http\.HandleFunc"),
    "db": re.compile(RE_DB_SERVER.pattern + r"|\b(?:SELECT\s+[\w*,\s.]+\s+FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM)\b|\.(?:findMany|findUnique|findOne|findAll|findById|insertOne|insertMany|updateOne|aggregate|upsert)\s*\(|\.objects\.(?:filter|get|create|all)\s*\(", re.I | re.M),
    "storage": re.compile(RE_STORAGE_SERVER.pattern + r"|\bfs\.(?:writeFile|createWriteStream)|\bfile_put_contents\s*\(|open\([^)]*['\"]wb['\"]", re.I | re.M),
    "messaging": re.compile(r"nodemailer|sendMail\s*\(|@sendgrid|resend\.emails|smtplib|send_mail\s*\(|PHPMailer|wp_mail\s*\(|Mail::to|twilio|messages\.create\s*\(|sendSms|send_sms|firebase-admin/messaging|sendPush", re.I),
}
RE_BUSINESS = re.compile(
    r"\b(?:price|total|subtotal|discount|coupon|tax|vat|fee|shipping|commission|amount|score|grade|points|balance|quantity|qty|interest|salary|bonus)\w*\b\s*(?:[*/+-]=?|=\s*[^=;\n]*[*/+-])",
    re.I,
)
RE_AUTHZ = re.compile(
    r"\b(?:isAdmin|is_admin|hasRole|has_role|hasPermission|can[A-Z]\w+|authorize|ownerId|owner_id|role\s*===?\s*['\"]|role\s*==\s*['\"]|user\.role|userId\s*===?|user_id\s*==)",
)
RE_FUNC = re.compile(
    r"^\s*(?:export\s+)?(?:async\s+)?function\s+\w+|^\s*(?:export\s+)?(?:const|let)\s+\w+\s*=\s*(?:async\s*)?\([^)]*\)\s*=>|^\s*(?:async\s+)?def\s+\w+|^\s*func\s+|^\s*(?:public|private|protected|static|\s)*function\s+\w+|^\s*(?:public|private|protected|internal)\s+[\w<>\[\],\s]+\s+\w+\s*\([^;]*$|^\s*fun\s+\w+",
    re.M,
)

PART_FOR = {
    "ui": "UI component(s)/view (layout only)",
    "api_client": "frontend api client (services/api)",
    "http_server": "routes + thin controller",
    "business": "business-logic service (backend/services)",
    "authz": "authorization policy (backend/policies)",
    "db": "repository (backend/database)",
    "storage": "storage service (backend/storage)",
    "messaging": "notification/email service",
}


def analyse(text):
    found = []
    for name, rx in CONCERNS.items():
        if rx.search(text):
            found.append(name)
    if len(RE_BUSINESS.findall(text)) >= 2:
        found.append("business")
    if len(RE_AUTHZ.findall(text)) >= 2:
        found.append("authz")
    funcs = [m.start() for m in RE_FUNC.finditer(text)]
    longest = 0
    if funcs:
        starts = [text.count("\n", 0, s) for s in funcs] + [text.count("\n")]
        longest = max(b - a for a, b in zip(starts, starts[1:])) if len(starts) > 1 else 0
    return found, len(funcs), longest


def run(root, top=40):
    root = Path(root).resolve()
    rows = []
    for rel, path, _b in iter_files(root):
        ext = Path(rel).suffix.lower()
        if ext not in SPLIT_EXT or rel.endswith(".min.js") or rel.endswith(".d.ts"):
            continue
        text = read_text(path, max_bytes=3_000_000)
        if not text:
            continue
        label, _s, _f = guess_label(rel, text)
        if label in ("TEST", "GENERATED", "CONFIG", "DOCS"):
            continue
        lines = count_lines(text)
        concerns, nfuncs, longest = analyse(text)
        rows.append({"file": rel, "label": label, "lines": lines, "functions": nfuncs,
                     "longest_block": longest, "concerns": concerns})
    if not rows:
        return {"scanner": "find_split_candidates", "root": str(root), "baseline": {}, "candidates": []}

    sizes = sorted(r["lines"] for r in rows)
    median = statistics.median(sizes)
    p90 = sizes[int(0.9 * (len(sizes) - 1))]
    size_floor = max(200, int(p90 * 1.5), int(median * 4))
    block_sizes = sorted(r["longest_block"] for r in rows if r["longest_block"])
    block_floor = max(80, int((block_sizes[int(0.9 * (len(block_sizes) - 1))] if block_sizes else 80) * 1.5))

    candidates = []
    for r in rows:
        c = set(r["concerns"])
        reasons, score = [], 0
        layer_mix = c & {"http_server", "db", "storage", "messaging"}
        if "ui" in c and (layer_mix or "business" in c or "authz" in c):
            reasons.append("UI mixed with server-side work (%s)" % ", ".join(sorted((layer_mix | (c & {"business", "authz"})))))
            score += 6
        if "http_server" in c and ("db" in c or "storage" in c or "messaging" in c):
            reasons.append("HTTP handler also does %s directly" % ", ".join(sorted(c & {"db", "storage", "messaging"})))
            score += 4
        if "http_server" in c and "business" in c:
            reasons.append("business formulas inside the HTTP layer")
            score += 3
        if "ui" in c and "api_client" in c:
            reasons.append("UI component calls the API directly (extract api client/hook)")
            score += 1
        if r["label"] == "FE" and "business" in c:
            reasons.append("frontend computes business values (check: must the backend own this?)")
            score += 2
        if r["lines"] >= size_floor:
            reasons.append("%d lines - large for this project (median %d, p90 %d)" % (r["lines"], median, p90))
            score += 2 + (r["lines"] // size_floor)
        if r["longest_block"] >= block_floor:
            reasons.append("a single function/block of ~%d lines" % r["longest_block"])
            score += 1
        if len(c - {"api_client"}) >= 3:
            score += 2
        if score >= 3:
            parts = [PART_FOR[k] for k in ["ui", "api_client", "http_server", "business", "authz", "db", "storage", "messaging"] if k in c]
            candidates.append(dict(r, score=score, reasons=reasons, suggested_parts=parts))
    candidates.sort(key=lambda x: (-x["score"], -x["lines"]))
    return {
        "scanner": "find_split_candidates",
        "root": str(root),
        "baseline": {"files": len(rows), "median_lines": median, "p90_lines": p90,
                     "size_signal_from": size_floor, "long_block_from": block_floor,
                     "note": "Thresholds are relative to this project; mixed responsibilities matter more than size."},
        "candidates": candidates[:top],
    }


def print_report(result):
    b = result.get("baseline", {})
    print("== SECURE_CHECK find_split_candidates ==")
    if b:
        print("  %d code files, median %s lines, p90 %s lines (size signal from %s lines)" % (
            b["files"], b["median_lines"], b["p90_lines"], b["size_signal_from"]))
    for c in result["candidates"]:
        print("  - %s  [%s, %d lines, score %d]" % (c["file"], c["label"], c["lines"], c["score"]))
        for r in c["reasons"]:
            print("      * " + r)
        if c["suggested_parts"]:
            print("      -> " + " | ".join(c["suggested_parts"]))
    if not result["candidates"]:
        print("  no strong candidates")


def main(argv=None):
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    ap.add_argument("--out")
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    result = run(args.root, args.top)
    if args.out:
        write_json(Path(args.out) / "split-candidates.json", result)
    if not args.quiet:
        print_report(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
