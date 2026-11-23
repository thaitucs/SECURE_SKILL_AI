#!/usr/bin/env python3
"""SECURE_CHECK - security score (0-100, grade A-F).

Implements references/scoring-rubric.md exactly. Input: one or more findings JSON files
({"findings": [...], "not_applicable": [...], "partial": bool}). Prints the score box and
category bars used in SECURE_CHECK_PLAN.txt, plus the projected score after proposed fixes.

Usage:
  python score.py findings.json [more.json ...] [--out DIR] [--include-unverified]
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import setup_console, write_json  # noqa: E402

CATEGORIES = [
    ("secrets", "Secrets & credentials", 20),
    ("auth", "Authentication & authz", 20),
    ("injection", "Input handling & injection", 15),
    ("exposure", "Public exposure", 10),
    ("data_storage", "Database & file storage", 10),
    ("config", "Configuration & transport", 10),
    ("abuse", "Abuse & spam protection", 10),
    ("dependencies", "Dependencies", 5),
]
ALWAYS_APPLICABLE = {"secrets", "exposure", "config", "dependencies"}
DEDUCT = {"critical": 20, "high": 10, "medium": 4, "low": 1, "info": 0}
OPEN_STATUSES = {"open"}


def grade(score):
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def bar(value, maximum, width=10):
    filled = int(round((value / float(maximum)) * width)) if maximum else 0
    return "#" * filled + "-" * (width - filled)


def compute(findings, not_applicable, assume_fixed=False):
    na = {c for c in not_applicable if c not in ALWAYS_APPLICABLE}
    per_cat = {}
    worst = {}
    open_crit = open_high = 0
    for f in findings:
        status = f.get("status", "open")
        if status not in OPEN_STATUSES:
            continue
        if assume_fixed and f.get("proposed_fix"):
            continue
        cat = f.get("category")
        sev = (f.get("severity") or "info").lower()
        if cat not in dict((c[0], 1) for c in CATEGORIES):
            continue
        if cat in na:
            na.discard(cat)  # a finding proves the category applies
        per_cat[cat] = per_cat.get(cat, 0) + DEDUCT.get(sev, 0)
        rank = ["info", "low", "medium", "high", "critical"].index(sev) if sev in DEDUCT else 0
        worst[cat] = max(worst.get(cat, 0), rank)
        open_crit += sev == "critical"
        open_high += sev == "high"
    cats = []
    raw = maximum = 0
    for key, label, weight in CATEGORIES:
        if key in na:
            cats.append({"key": key, "label": label, "weight": weight, "score": None, "applicable": False})
            continue
        s = max(0, weight - per_cat.get(key, 0))
        raw += s
        maximum += weight
        marker = {4: "!!!", 3: "!!", 2: "!"}.get(worst.get(key, 0), "")
        cats.append({"key": key, "label": label, "weight": weight, "score": s, "applicable": True, "marker": marker})
    score = int(round(raw / float(maximum) * 100)) if maximum else 100
    cap = None
    if open_crit:
        cap = 49
    elif open_high:
        cap = 79
    if cap is not None and score > cap:
        capped = True
        score = cap
    else:
        capped = False
    return {"score": score, "grade": grade(score), "cap": cap if capped else None,
            "open_critical": open_crit, "open_high": open_high, "categories": cats}


def load(paths, include_unverified):
    findings, na, partial = [], set(), False
    for p in paths:
        data = json.loads(Path(p).read_text(encoding="utf-8"))
        items = data.get("findings", data if isinstance(data, list) else [])
        for f in items:
            if not include_unverified and f.get("verified") is False:
                continue
            findings.append(f)
        na.update(data.get("not_applicable", []) if isinstance(data, dict) else [])
        partial = partial or bool(data.get("partial")) if isinstance(data, dict) else partial
    return findings, sorted(na), partial


def render(now, projected, partial):
    lines = []
    lines.append("#" * 66)
    lines.append("#  SECURITY SCORE:  %3d / 100      GRADE: %s" % (now["score"], now["grade"]))
    lines.append("#  [%s]" % bar(now["score"], 100, 20))
    if now["cap"] is not None:
        why = "%d CRITICAL issue(s)" % now["open_critical"] if now["open_critical"] else "%d HIGH issue(s)" % now["open_high"]
        lines.append("#  %s Capped at %d because %s are open." % ("!!!" if now["open_critical"] else "!!", now["cap"], why))
    if projected is not None:
        lines.append("#  After the proposed fixes: %d / 100 (%s)" % (projected["score"], projected["grade"]))
    if partial:
        lines.append("#  (i) partial review - see SECURITY_REPORT.md for areas not reviewed")
    lines.append("#" * 66)
    lines.append("")
    for c in now["categories"]:
        if not c["applicable"]:
            lines.append("   %-28s  n/a" % c["label"])
            continue
        lines.append("   %-28s [%s] %2d/%-2d %s" % (c["label"], bar(c["score"], c["weight"]), c["score"], c["weight"], c["marker"]))
    return "\n".join(lines)


def main(argv=None):
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out")
    ap.add_argument("--include-unverified", action="store_true",
                    help="also count raw scanner leads (verified=false) - gives a PRELIMINARY score")
    args = ap.parse_args(argv)
    findings, na, partial = load(args.files, args.include_unverified)
    now = compute(findings, na)
    projected = compute(findings, na, assume_fixed=True)
    text = render(now, projected, partial)
    if args.include_unverified:
        text = "(PRELIMINARY - includes unverified scanner leads)\n" + text
    print(text)
    if args.out:
        write_json(Path(args.out) / "score.json", {"now": now, "projected": projected, "partial": partial,
                                                    "preliminary": args.include_unverified})
        (Path(args.out) / "score.txt").write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
