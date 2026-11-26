# SECURE_CHECK - Refactor plan

- **Project:** {{name}} · **Date:** {{yyyy-mm-dd}}
- **Chosen structure:** {{layered | feature modules | framework conventions}} - because {{reason}}
- **Rule:** restructuring and splitting do not change behaviour.

## 1. Current vs proposed structure

```
CURRENT                                  PROPOSED
{{tree}}                                 {{tree}}
```

Architecture target: `Client → Backend → (Database | File Storage)`

| Layer | Current location(s) | Proposed location |
|-------|---------------------|-------------------|
| Frontend | | |
| Backend logic (services) | | |
| Authorization (policies) | | |
| Database branch | | |
| File storage branch | | |
| Config / env | | |

## 2. Moves

| ID | From | To | Reason | Imports to update |
|----|------|----|--------|-------------------|
| MOVE-01 | | | | |

## 3. Splits

```
SPLIT-01  {{file}}  ({{size}}, mixes: {{responsibilities}})
  -> {{new file}}   {{its single job}}
  -> {{new file}}   {{its single job}}
  Imports to update: {{files}}
  Public surface: {{re-export kept / all imports updated}}
  Risk: {{Low/Med/High}} · Effort: {{S/M/L}} · Verify: {{command / manual check}}
```

### Reviewed and kept as is

| File | Why it is fine |
|------|----------------|

## 4. Quarantine / remove from public

| ID | Path | Evidence | Destination |
|----|------|----------|-------------|
| DEL-01 | | | `_quarantine/...` |
| CFG-02 | | | outside web root / `.gitignore` |

## 5. Config changes

| ID | File | Change |
|----|------|--------|
| CFG-01 | `.gitignore` | add `.env*`, keys (+ optional `secure-check-report/`, `_quarantine/` - already local-only) |

## 6. Execution order

1. Branch `secure-check/{{date}}` / backup
2. FIX (Critical, High) → CFG → MOVE → SPLIT → DEL → SPAM → FIX (Medium, Low)
3. After each group: {{build/test commands}}

## 7. Verification

- Build: `{{command}}`
- Tests: `{{command}}`
- Manual: {{key flows to click through}}
- Re-scan: `python <skill>/scripts/run_all.py . --out secure-check-report/raw`
