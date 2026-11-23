# SECURE_CHECK - Security report

- **Project:** {{name}}
- **Date:** {{yyyy-mm-dd}}
- **Reviewed by:** {{AI name/model}} using SECURE_CHECK
- **Scope:** {{folders reviewed}} · **Not reviewed:** {{folders/areas, or "none"}}
- **Stack:** {{stack}}
- **Score:** {{score}}/100 (**{{grade}}**) {{cap note}} → projected {{projected}}/100 after fixes

> This file lists vulnerabilities. Do not publish or deploy it.

## Summary

| Severity | Open | Proposed fix in plan |
|----------|------|----------------------|
| Critical | {{n}} | {{n}} |
| High | {{n}} | {{n}} |
| Medium | {{n}} | {{n}} |
| Low | {{n}} | {{n}} |
| Info | {{n}} | - |

| Category | Score | Notes |
|----------|-------|-------|
| Secrets & credentials | {{s}}/20 | |
| Authentication & authorization | {{s}}/20 | |
| Input handling & injection | {{s}}/15 | |
| Public exposure | {{s}}/10 | |
| Database & file storage | {{s}}/10 | |
| Configuration & transport | {{s}}/10 | |
| Abuse & spam protection | {{s}}/10 | |
| Dependencies | {{s}}/5 | |

## What is already good

- {{e.g. passwords hashed with argon2id}}
- {{e.g. all queries use Prisma, no raw SQL}}

## Findings

<!-- Repeat per finding, ordered Critical → Info. -->

### FIX-01 · Critical · secrets - {{title}}

- **Location:** `{{path}}:{{line}}` {{(+ other locations)}}
- **Evidence:** `{{masked snippet}}`
- **Impact:** {{what an attacker can do, plain words}}
- **Fix:** {{steps}}

  ```{{lang}}
  // before
  {{masked bad code}}
  // after
  {{fixed code}}
  ```
- **Effort:** {{S/M/L}} · **Change risk:** {{Low/Med/High}}
- **You must also do:** {{YOU-xx, e.g. rotate key}}
- **Reference:** {{OWASP id / checklist item}}

## Checks performed

| Checklist | Result |
|-----------|--------|
| Secrets scan (source) | {{done / partial / not possible}} |
| Secrets scan (build output, history) | {{...}} |
| Public exposure | {{...}} |
| Web app / API / mobile checklist | {{...}} |
| Database | {{...}} |
| File storage | {{...}} |
| Contact anti-spam | {{...}} |
| Dependency audit | {{tool + result, or "not available"}} |

## Accepted risks

| ID | Finding | Accepted by | Reason |
|----|---------|-------------|--------|

## Git history cleanup (if secrets were committed)

1. **Rotate first** - history cleanup does not un-leak a key.
2. Install `git-filter-repo` (or BFG).
3. `git filter-repo --path <file> --invert-paths` (remove a file) or
   `--replace-text replacements.txt` (replace strings).
4. Force-push all branches and tags; ask every collaborator to re-clone.
5. Ask the hosting provider to purge cached views if the repo was public.
