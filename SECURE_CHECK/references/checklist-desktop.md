# Checklist - Desktop apps (Electron, Tauri, .NET WPF/WinForms/MAUI, Qt, Java)

The installed app is **frontend**: users can unpack it (`asar extract`, decompilers).

## Electron
- [ ] `contextIsolation: true`, `nodeIntegration: false`, `sandbox: true` for all windows.
- [ ] Preload exposes a minimal API via `contextBridge`; no raw `ipcRenderer` or `require`.
- [ ] IPC handlers in main validate sender (`event.senderFrame.url`) and arguments.
- [ ] No `shell.openExternal` with untrusted URLs (allow-list `https:`).
- [ ] No remote content loaded with Node privileges; `webSecurity` not disabled;
      `allowRunningInsecureContent` false.
- [ ] Navigation restricted (`will-navigate`, `setWindowOpenHandler`).
- [ ] CSP set for local pages.
- [ ] Auto-updates signed and over HTTPS (electron-updater with code signing).
- [ ] Electron version supported (old Chromium = many CVEs).
- [ ] No secrets in `app.asar`; API calls needing secrets go through a backend.

## Tauri
- [ ] `allowlist`/capabilities minimal (fs scope, shell scope, http scope).
- [ ] Commands (`#[tauri::command]`) validate inputs, no arbitrary path/command execution.
- [ ] CSP configured in `tauri.conf.json`.
- [ ] Updater signature key private and not in repo.

## Native (.NET, Qt, Java, C++)
- [ ] Connection strings / API keys not embedded (decompilers reveal them).
- [ ] App does not connect directly to a central DB with a shared account - use an API.
- [ ] Local secrets via OS store (DPAPI / Windows Credential Manager, macOS Keychain,
      libsecret).
- [ ] Installer/updater signed; update channel HTTPS + signature check.
- [ ] DLL search-order hijacking: load libraries from absolute paths.
- [ ] Local files/registry written with user-only permissions.

## Common
- [ ] Licence/feature checks that matter are verified server-side.
- [ ] Logs do not contain tokens.
- [ ] Crash reports scrub PII.
