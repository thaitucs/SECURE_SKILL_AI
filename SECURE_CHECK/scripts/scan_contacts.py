#!/usr/bin/env python3
"""SECURE_CHECK - contact exposure & form spam scanner.

Finds email addresses and phone numbers visible to visitors (page source, templates,
frontend code, JSON-LD), mailto:/tel:/WhatsApp/Zalo links, forms without visible spam
protection, and message-sending code (email/SMS/OTP) without a visible rate limit.
Results feed the SPAM-* recommendations. Nothing is changed.

Usage:
  python scan_contacts.py <project_dir> [--out DIR]
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    guess_label, in_public_dir, iter_files, make_finding, read_text, setup_console, write_json,
)

VISIBLE_EXT = {
    ".html", ".htm", ".php", ".jsx", ".tsx", ".js", ".ts", ".vue", ".svelte", ".astro",
    ".erb", ".ejs", ".hbs", ".njk", ".twig", ".liquid", ".cshtml", ".razor", ".jsp",
    ".md", ".mdx", ".json", ".xml", ".txt", ".yml", ".yaml", ".dart", ".kt", ".swift",
}
TEMPLATE_EXT = {".html", ".htm", ".php", ".erb", ".ejs", ".hbs", ".njk", ".twig", ".liquid",
                ".cshtml", ".razor", ".jsp", ".vue", ".svelte", ".astro", ".jsx", ".tsx"}

RE_EMAIL = re.compile(r"(?<![\w.+-])([A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9-]{1,63}(?:\.[A-Za-z0-9-]{1,63})*\.[A-Za-z]{2,24})(?![\w-])")
RE_MAILTO = re.compile(r"mailto:([^\"'?\s>]+)", re.IGNORECASE)
RE_TEL = re.compile(r"(?:tel|sms|callto):\s*([+\d][\d\s().-]{5,})", re.IGNORECASE)
RE_CHAT = re.compile(r"(?:wa\.me/|api\.whatsapp\.com/send\?phone=|zalo\.me/|t\.me/|viber://chat\?number=)([+\w%.-]{5,})", re.IGNORECASE)
RE_PHONE_CTX = re.compile(
    r"(?i)(phone|tel|telephone|mobile|hotline|call|fax|whatsapp|zalo|sđt|sdt|điện thoại|dien thoai|liên hệ|lien he|contact)"
    r"[^\n]{0,40}?((?:\+|00)?\d[\d\s().-]{7,18}\d)"
)
RE_JSONLD_CONTACT = re.compile(r"[\"'](email|telephone)[\"']\s*:\s*[\"']([^\"']+)[\"']", re.IGNORECASE)

EMAIL_IGNORE_DOMAINS = (
    "example.com", "example.org", "example.net", "domain.com", "email.com", "test.com",
    "yourdomain.com", "yourcompany.com", "company.com", "sentry.io", "localhost",
    "users.noreply.github.com", "noreply.github.com",
)
EMAIL_IGNORE_TLDS = {"png", "jpg", "jpeg", "gif", "svg", "webp", "avif", "js", "ts", "css", "map", "json", "vue", "jsx", "tsx", "ico"}

RE_FORM = re.compile(r"<form\b|<Form\b|useForm\(|FormData\(|onSubmit\s*=|@submit", re.IGNORECASE)
RE_FORM_PROTECT = re.compile(
    r"cf-turnstile|turnstile|hcaptcha|h-captcha|g-recaptcha|recaptcha|grecaptcha|honeypot|honey_pot|data-netlify-honeypot|netlify-honeypot|friendly-?captcha|altcha|captcha",
    re.IGNORECASE,
)
RE_SENDER = re.compile(
    r"nodemailer|sendMail\(|@sendgrid/mail|resend\.emails\.send|mailgun|postmark|smtplib|send_mail\(|EmailMessage\(|PHPMailer|wp_mail\(|\bmail\(\s*\$|Mail::to|ActionMailer|twilio|messages\.create\(|sendSms|send_sms|verify\.v2|otp|one[_-]?time[_-]?password",
    re.IGNORECASE,
)
RE_RATE_LIMIT = re.compile(
    r"rate[-_ ]?limit|ratelimit|throttle|limiter|slowapi|RateLimiter|express-rate-limit|@fastify/rate-limit|ThrottlerModule|AddRateLimiter|Upstash|rack-attack",
    re.IGNORECASE,
)
RE_RECIPIENT_FROM_INPUT = re.compile(
    r"to\s*[:=]\s*(?:req\.body|request\.(?:form|json|POST)|\$_(?:POST|GET|REQUEST))", re.IGNORECASE,
)


def clean_phone(p):
    digits = re.sub(r"\D", "", p)
    return digits if 8 <= len(digits) <= 15 else None


def is_real_email(e):
    low = e.lower()
    domain = low.split("@", 1)[1]
    tld = domain.rsplit(".", 1)[-1]
    if tld in EMAIL_IGNORE_TLDS:
        return False
    if any(domain == d or domain.endswith("." + d) for d in EMAIL_IGNORE_DOMAINS):
        return False
    if re.match(r"^\d+(\.\d+)*$", domain.split(".")[0]):
        return False  # package@1.2.3 style
    return True


def run(root):
    root = Path(root).resolve()
    exposures = []      # {type, value, file, line, how}
    forms = []          # {file, line, protected}
    senders = []        # {file, rate_limited, recipient_from_input}
    for rel, path, _b in iter_files(root):
        ext = Path(rel).suffix.lower()
        if ext not in VISIBLE_EXT:
            continue
        text = read_text(path, max_bytes=2_000_000)
        if not text:
            continue
        label, _signals, _flags = guess_label(rel, text)
        visible = label in ("FE", "CONFIRM?") or in_public_dir(rel) or ext in TEMPLATE_EXT
        if label in ("TEST", "DOCS", "GENERATED", "CONFIG", "PRIVATE"):
            visible = in_public_dir(rel)
        lines = text.splitlines()

        if visible:
            for no, line in enumerate(lines, 1):
                if len(line) > 4000:
                    line = line[:4000]
                for m in RE_MAILTO.finditer(line):
                    if is_real_email(m.group(1) if "@" in m.group(1) else "x@example.com"):
                        exposures.append({"type": "email", "value": m.group(1), "file": rel, "line": no, "how": "mailto link"})
                for m in RE_EMAIL.finditer(line):
                    if "mailto:" in line[max(0, m.start() - 8):m.start()]:
                        continue
                    if is_real_email(m.group(1)):
                        exposures.append({"type": "email", "value": m.group(1), "file": rel, "line": no, "how": "plain text"})
                for m in RE_TEL.finditer(line):
                    d = clean_phone(m.group(1))
                    if d:
                        exposures.append({"type": "phone", "value": m.group(1).strip(), "file": rel, "line": no, "how": "tel/sms link"})
                for m in RE_CHAT.finditer(line):
                    exposures.append({"type": "phone", "value": m.group(1), "file": rel, "line": no, "how": "chat link (WhatsApp/Zalo/Telegram/Viber)"})
                for m in RE_PHONE_CTX.finditer(line):
                    d = clean_phone(m.group(2))
                    if d and not re.search(r"tel:|sms:", line[max(0, m.start(2) - 6):m.start(2)]):
                        exposures.append({"type": "phone", "value": m.group(2).strip(), "file": rel, "line": no, "how": "plain text"})
                for m in RE_JSONLD_CONTACT.finditer(line):
                    exposures.append({"type": "email" if m.group(1).lower() == "email" else "phone", "value": m.group(2),
                                      "file": rel, "line": no, "how": "structured data (JSON-LD/schema)"})
            for m in RE_FORM.finditer(text):
                no = text.count("\n", 0, m.start()) + 1
                forms.append({"file": rel, "line": no, "protected": bool(RE_FORM_PROTECT.search(text))})
                break

        if label in ("BE", "BE:DB", "BE:STORAGE", "CONFIRM?") or ext == ".php":
            if RE_SENDER.search(text):
                senders.append({
                    "file": rel,
                    "rate_limited": bool(RE_RATE_LIMIT.search(text)),
                    "recipient_from_input": bool(RE_RECIPIENT_FROM_INPUT.search(text)),
                })

    # de-duplicate exposures
    seen, uniq = set(), []
    for e in exposures:
        key = (e["type"], e["value"].lower(), e["file"], e["line"])
        if key not in seen:
            seen.add(key)
            uniq.append(e)
    exposures = uniq

    findings = []
    n = 0
    emails = sorted({e["value"].lower() for e in exposures if e["type"] == "email"})
    phones = sorted({re.sub(r"\D", "", e["value"]) for e in exposures if e["type"] == "phone"})
    if emails:
        n += 1
        files = sorted({e["file"] for e in exposures if e["type"] == "email"})
        findings.append(make_finding("SCAN-SPAM-%03d" % n, "low", "abuse",
                                     "%d email address(es) visible in page source (%d file(s)) - harvestable by spam bots" % (len(emails), len(files)),
                                     file=files[0], source="scan_contacts", confidence="high",
                                     note="Addresses: " + ", ".join(emails[:10])))
    if phones:
        n += 1
        files = sorted({e["file"] for e in exposures if e["type"] == "phone"})
        findings.append(make_finding("SCAN-SPAM-%03d" % n, "low", "abuse",
                                     "%d phone number(s) visible in page source (%d file(s)) - harvestable by spam/robocall bots" % (len(phones), len(files)),
                                     file=files[0], source="scan_contacts", confidence="medium"))
    for f in forms:
        if not f["protected"]:
            n += 1
            findings.append(make_finding("SCAN-SPAM-%03d" % n, "medium", "abuse",
                                         "Form without visible spam protection (no honeypot/CAPTCHA found in file)",
                                         file=f["file"], line=f["line"], source="scan_contacts", confidence="low",
                                         note="Check the server handler: honeypot, time-trap, rate limit, CAPTCHA verification."))
    for s in senders:
        if s["recipient_from_input"]:
            n += 1
            findings.append(make_finding("SCAN-SPAM-%03d" % n, "high", "abuse",
                                         "Email/SMS recipient appears to come from user input (open relay risk)",
                                         file=s["file"], source="scan_contacts", confidence="low"))
        if not s["rate_limited"]:
            n += 1
            findings.append(make_finding("SCAN-SPAM-%03d" % n, "medium", "abuse",
                                         "Email/SMS/OTP sending code without a visible rate limit in this file",
                                         file=s["file"], source="scan_contacts", confidence="low",
                                         note="Rate limit may be configured elsewhere (middleware/gateway) - verify."))
    return {
        "scanner": "scan_contacts",
        "root": str(root),
        "exposures": exposures,
        "forms": forms,
        "message_senders": senders,
        "findings": findings,
    }


def print_report(result, limit=40):
    ex = result["exposures"]
    print("== SECURE_CHECK scan_contacts ==")
    print("  visible contact data: %d occurrence(s)" % len(ex))
    for e in ex[:limit]:
        print("   - %-5s %-32s %s:%s (%s)" % (e["type"], e["value"][:32], e["file"], e["line"], e["how"]))
    if len(ex) > limit:
        print("   ... %d more in JSON output" % (len(ex) - limit))
    print("  forms found: %d (unprotected: %d)" % (len(result["forms"]), sum(1 for f in result["forms"] if not f["protected"])))
    print("  message-sending files: %d" % len(result["message_senders"]))
    for f in result["findings"]:
        print("  [%-8s] %s  (%s)" % (f["severity"].upper(), f["title"], f["file"]))


def main(argv=None):
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    ap.add_argument("--out")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    result = run(args.root)
    if args.out:
        write_json(Path(args.out) / "contacts.json", result)
    if not args.quiet:
        print_report(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
