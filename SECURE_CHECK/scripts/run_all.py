#!/usr/bin/env python3
"""SECURE_CHECK - run every scanner and write raw results.

Read-only for the project: it only writes JSON/TXT into --out
(default: <project>/secure-check-report/raw). Standard library only, no network.

Local-only: the report folder gets its own `.gitignore` (`*`) and is added, with
`_quarantine/`, to `.git/info/exclude`, so generated files are never committed or pushed.

Outputs:
  inventory.json  secrets.json  exposure.json  contacts.json  code-risks.json
  split-candidates.json
  scanner-findings.json   (all leads merged, verified=false)
  score.txt / score.json  (PRELIMINARY score from unverified leads)

Usage:
  python run_all.py <project_dir> [--out DIR] [--fail-on critical|high|medium|low]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import find_split_candidates  # noqa: E402
import inventory  # noqa: E402
import scan_code_risks  # noqa: E402
import scan_contacts  # noqa: E402
import scan_exposure  # noqa: E402
import scan_secrets  # noqa: E402
import score  # noqa: E402
from _common import (  # noqa: E402
    ensure_local_only, setup_console, severity_at_least, tracked_outputs, write_json, SEVERITY_ORDER,
)


def main(argv=None):
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    ap.add_argument("--out")
    ap.add_argument("--fail-on", choices=["critical", "high", "medium", "low"])
    ap.add_argument("--quick", action="store_true", help="secrets + exposure + score only")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print("not a directory: %s" % root, file=sys.stderr)
        return 2
    out = Path(args.out).resolve() if args.out else root / "secure-check-report" / "raw"
    out.mkdir(parents=True, exist_ok=True)
    ensure_local_only(out)

    print("SECURE_CHECK scanners - project: %s" % root)
    print("results -> %s\n" % out)

    results = {}
    if not args.quick:
        results["inventory"] = inventory.run(root)
        write_json(out / "inventory.json", results["inventory"])
        inventory.print_report(results["inventory"])
        print()
    results["secrets"] = scan_secrets.run(root=root)
    write_json(out / "secrets.json", results["secrets"])
    scan_secrets.print_report(results["secrets"])
    print()
    results["exposure"] = scan_exposure.run(root)
    write_json(out / "exposure.json", results["exposure"])
    scan_exposure.print_report(results["exposure"])
    print()
    if not args.quick:
        results["contacts"] = scan_contacts.run(root)
        write_json(out / "contacts.json", results["contacts"])
        scan_contacts.print_report(results["contacts"])
        print()
        results["code"] = scan_code_risks.run(root)
        write_json(out / "code-risks.json", results["code"])
        scan_code_risks.print_report(results["code"])
        print()
        results["split"] = find_split_candidates.run(root)
        write_json(out / "split-candidates.json", results["split"])
        find_split_candidates.print_report(results["split"])
        print()

    merged = []
    for key in ("secrets", "exposure", "contacts", "code"):
        merged.extend(results.get(key, {}).get("findings", []))
    merged.sort(key=lambda f: -SEVERITY_ORDER.get(f["severity"], 0))
    write_json(out / "scanner-findings.json", {
        "note": "Raw scanner leads (verified=false). The AI must confirm each one, drop false positives, "
                "add findings from manual review, then write findings.json for the final score.",
        "findings": merged,
    })

    now = score.compute(merged, [])
    text = "(PRELIMINARY - unverified scanner leads only; manual review not included)\n" + score.render(now, None, False)
    (out / "score.txt").write_text(text + "\n", encoding="utf-8")
    write_json(out / "score.json", {"now": now, "projected": None, "preliminary": True})
    print(text)

    counts = {}
    for f in merged:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    print("\nleads: " + ", ".join("%s=%d" % (k, counts[k]) for k in ("critical", "high", "medium", "low", "info") if k in counts))
    print("(i) secure-check-report/ describes vulnerabilities - do not deploy or publish it.")
    print("(i) Generated files are LOCAL-ONLY: git ignores secure-check-report/ and _quarantine/.")
    tracked = tracked_outputs(root)
    if tracked:
        print("(!) These SECURE_CHECK files are already tracked by git and WILL be pushed:")
        for t in tracked[:20]:
            print("      " + t)
        print("    Untrack them (files stay on disk): git rm -r --cached secure-check-report _quarantine")

    if args.fail_on and any(severity_at_least(f["severity"], args.fail_on) for f in merged):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
