# Native Android (Kotlin/Java) and iOS (Swift/Objective-C)

**Detect:** Android: `app/src/main/AndroidManifest.xml`, `build.gradle`, `.kt`/`.java`.
iOS: `*.xcodeproj`/`*.xcworkspace`, `Info.plist`, `.swift`, `Podfile`, `Package.swift`.

**Boundary:** all app code = `FE`. Backend separate.

**Secrets/env:** Android `BuildConfig` fields, `strings.xml`, `gradle.properties`,
`local.properties` (should be gitignored); iOS `Info.plist`, `.xcconfig`, constants - all
extractable. Signing files (`*.jks`, `key.properties`, `*.p12`, `*.mobileprovision`)
must not be committed.

**Database branch:** Room/SQLite/Realm/Core Data/SwiftData = local cache. Use SQLCipher or
platform encryption for sensitive data. Parameterize raw SQLite queries.

**File storage branch:** app sandbox files - no world-readable modes; remote uploads via API.

**Top risks**
- Android: `android:debuggable="true"`, `allowBackup="true"`, exported components without
  permissions, `usesCleartextTraffic="true"`, custom `TrustManager`/`HostnameVerifier`
  accepting all, `WebView.addJavascriptInterface` with untrusted content, `MODE_WORLD_READABLE`,
  secrets in `SharedPreferences` (use `EncryptedSharedPreferences`/Keystore), R8 disabled
  for release.
- iOS: `NSAllowsArbitraryLoads = YES`, tokens in `UserDefaults` (use Keychain), URL scheme
  hijacking (prefer Universal Links), sensitive data in screenshots/app switcher, logging
  PII with `print`/`NSLog`.
- Both: purchase/entitlement checks only on device; certificate pinning for banking-grade apps.

**Target mapping:** Android - `ui/`, `viewmodel/`, `data/{remote, local, repository}`,
`domain/`, `di/`. iOS - `Features/<Feature>/{Views, ViewModels}`, `Services/API`,
`Persistence/`, `Models/`.

**Verify:** `./gradlew lint test assembleRelease`; `xcodebuild test`; inspect the release
package for secrets (`apktool d`, `unzip *.ipa`) only on the user's own build.
