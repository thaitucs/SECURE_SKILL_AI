# Electron / Tauri desktop apps

**Detect:** `electron` in `package.json` (`main` field → main process file);
`src-tauri/`, `tauri.conf.json`, `Cargo.toml`.

**Boundary**
- Electron main process = privileged local code (treat like `BE` for review, but it ships to
  users → no secrets). Renderer = `FE`. Preload = bridge (minimal API).
- Tauri Rust commands = privileged local code; web UI = `FE`.
- A real backend (API) is still needed for secrets and authoritative logic.

**Secrets/env:** nothing secret inside `app.asar` or the Tauri binary.

**Database branch:** local SQLite for user data only; central data via API (no direct
connection to a shared remote DB).

**File storage branch:** local files with user-only permissions; uploads via API.

**Top risks:** see `references/checklist-desktop.md` (contextIsolation, nodeIntegration,
sandbox, IPC validation, `shell.openExternal`, navigation, CSP, updater signing, Tauri
capability scopes).

**Target mapping**
```
Electron: src/main/ (main process, ipc handlers)  src/preload/  src/renderer/ (UI)
Tauri:    src-tauri/src/commands/  src-tauri/capabilities/  src/ (UI)
```

**Verify:** `npm run build` / `npm run make`, `cargo build`, `cargo audit` (if installed),
check `webPreferences` of every `BrowserWindow`.
