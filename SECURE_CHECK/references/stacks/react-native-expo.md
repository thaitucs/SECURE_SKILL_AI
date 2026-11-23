# React Native / Expo

**Detect:** `react-native`, `expo` in `package.json`; `app.json`/`app.config.js`, `android/`,
`ios/`.

**Boundary:** the whole app = `FE` (ships to devices). Backend is separate (API, BaaS,
serverless).

**Secrets/env:** `EXPO_PUBLIC_*`, `app.json` → `extra`, `react-native-config` `.env` values,
`Constants.expoConfig` - all **readable in the bundle**. Only public values.

**Database branch:** none in the app except local cache (SQLite/MMKV) - no secrets there
unencrypted. Remote data via API or BaaS with rules.

**File storage branch:** upload via backend or presigned URL; no storage secrets in app.

**Top risks**
- Tokens in `AsyncStorage` → use `expo-secure-store` / `react-native-keychain`.
- `WebView` with `originWhitelist={['*']}`, `javaScriptEnabled` on untrusted content,
  `onMessage` trusting any origin.
- Deep links (`Linking`) handling auth callbacks without validation.
- Cleartext HTTP allowed (Android `usesCleartextTraffic`, iOS ATS exceptions).
- OTA updates (EAS Update / CodePush) - signed and from your account only.
- Logic that grants rewards/purchases on the client → verify receipts server-side.
- `console.log` of tokens in release builds.

**Target mapping**
```
src/screens/ src/components/ src/navigation/ src/hooks/
src/services/api/   src/store/   src/utils/   src/config/ (public values only)
```

**Verify:** `npx expo export` / `npx react-native bundle`, grep the bundle for secrets, run
tests (`jest`), `npm audit`.
