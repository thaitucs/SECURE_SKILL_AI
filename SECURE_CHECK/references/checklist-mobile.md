# Checklist - Mobile apps (Android, iOS, React Native, Flutter, Ionic/Capacitor, .NET MAUI)

Based on OWASP Mobile Top 10 (2024). **Rule zero:** everything inside the app package can be
extracted by the user. The app is frontend. Secrets and authoritative logic go to the backend.

| # | Risk | Check |
|---|------|-------|
| M1 | Improper Credential Usage | No secret keys in code, `strings.xml`, `Info.plist`, `.env` assets, `--dart-define`, `react-native-config`, `BuildConfig` fields. Third-party secret calls go through your backend. |
| M2 | Inadequate Supply Chain Security | Dependencies from official registries, versions pinned, SDKs reviewed (ads/analytics collecting data), no unverified binaries. |
| M3 | Insecure Authentication/Authorization | Auth enforced by the backend; no "offline admin mode"; biometric checks backed by keystore crypto, not just a boolean; tokens refreshed/expired. |
| M4 | Insufficient Input/Output Validation | Deep links/intents/URL schemes validated; WebView inputs escaped; no SQL injection in local SQLite queries. |
| M5 | Insecure Communication | HTTPS only; Android `usesCleartextTraffic=false` / Network Security Config; iOS ATS not disabled globally (`NSAllowsArbitraryLoads`); no custom TrustManager/`onReceivedSslError → proceed()`; certificate pinning for high-risk apps. |
| M6 | Inadequate Privacy Controls | Only needed permissions; PII minimised; logs/analytics without PII; privacy manifest (iOS) and data safety form (Android) accurate. |
| M7 | Insufficient Binary Protections | Release builds minified/obfuscated (R8/ProGuard, `--obfuscate --split-debug-info`, Hermes); debug flags off; integrity checks for high-risk apps (Play Integrity, App Attest). |
| M8 | Security Misconfiguration | `android:debuggable` false, `allowBackup` false or rules, exported components (`android:exported`) minimal and protected, no world-readable files, FileProvider paths narrow. |
| M9 | Insecure Data Storage | Tokens in Keychain / Keystore / EncryptedSharedPreferences / `flutter_secure_storage` / `expo-secure-store` - **not** AsyncStorage, SharedPreferences, UserDefaults, plain files, SQLite without encryption. No sensitive data in caches, screenshots of sensitive screens hidden (`FLAG_SECURE`). |
| M10 | Insufficient Cryptography | No custom crypto, no hard-coded encryption keys/IVs, no ECB, no MD5/SHA1 for security, platform keystore for keys. |

## Platform specifics

**Android**
- `AndroidManifest.xml`: `debuggable`, `allowBackup`, `usesCleartextTraffic`, exported
  activities/services/receivers/providers, custom permissions with `signature` level.
- `google-services.json` is public-ish; the protection is Firebase rules + App Check.
- Signing: `*.jks`/`key.properties` never committed.
- WebView: `setJavaScriptEnabled` only if needed, `addJavascriptInterface` only for trusted
  content, `setAllowFileAccess(false)`.

**iOS**
- `Info.plist`: ATS exceptions, URL schemes, usage descriptions.
- Keychain accessibility (`kSecAttrAccessibleWhenUnlockedThisDeviceOnly`).
- Universal Links preferred over custom URL schemes for auth callbacks.

**React Native / Expo**
- `EXPO_PUBLIC_*` and `app.json` `extra` are public.
- Hermes bytecode is not encryption.
- `expo-secure-store` for tokens.

**Flutter**
- `assets/.env`, `lib/constants.dart` are readable after unpacking.
- `flutter build --obfuscate --split-debug-info=...` for release.

**Hybrid (Ionic/Capacitor/Cordova)**
- CSP in `index.html`, `allowNavigation` narrow, no `*` in `<access origin>`.

## Backend-related (most mobile bugs are really API bugs)
- Run `checklist-api.md` on the backend the app calls.
- The API must not trust app-side checks ("the app only sends valid prices").
- OTP/SMS endpoints protected (`contact-anti-spam.md` section 5).
