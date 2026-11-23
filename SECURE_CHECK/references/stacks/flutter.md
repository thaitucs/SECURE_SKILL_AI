# Flutter / Dart

**Detect:** `pubspec.yaml`, `lib/main.dart`, `android/`, `ios/`, `web/`.

**Boundary:** app code = `FE`. Dart server code (Shelf, Dart Frog, Serverpod) in a separate
package = `BE`.

**Secrets/env:** `--dart-define`, `flutter_dotenv` `assets/.env`, `lib/constants.dart`,
`firebase_options.dart` - all extractable. Only public values (Firebase options are public by
design; rules protect data).

**Database branch:** local `sqflite`/`drift`/`hive`/`isar` = cache only; encrypt sensitive
data (`sqlcipher`, `hive` encryption with key in secure storage). Remote via API/BaaS.

**File storage branch:** uploads through backend or Firebase Storage with strict rules.

**Top risks**
- Tokens in `shared_preferences` → `flutter_secure_storage`.
- `badCertificateCallback` returning `true` (disables TLS checks).
- Release built without `--obfuscate --split-debug-info`.
- `webview_flutter` with JS channels exposed to untrusted pages.
- Firebase rules open (see `baas-firebase-supabase.md`).
- In-app purchase validation only on device → verify server-side.

**Target mapping**
```
lib/
  main.dart  app.dart
  features/<feature>/{presentation (screens, widgets), state (bloc/riverpod/provider),
                      data (repositories, api), domain (models)}
  core/{network, config (public), utils, theme}
```

**Verify:** `flutter analyze`, `flutter test`, `flutter build apk --release --obfuscate
--split-debug-info=build/symbols`, `dart pub outdated`.
