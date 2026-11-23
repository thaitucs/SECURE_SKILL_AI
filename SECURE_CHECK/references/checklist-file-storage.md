# Checklist - File Storage branch (images, video, audio, PDF, uploads)

See `architecture-model.md` section 4.

## Placement
- [ ] Only backend `storage/` module uses privileged storage credentials.
- [ ] Uploads are **not** stored in the source tree, in `public/`, or anywhere the web server
      executes scripts. Local disk storage lives outside the web root (or a dedicated folder
      with script execution disabled).
- [ ] Files are not stored in the database (see `checklist-database.md`).
- [ ] Metadata row in DB for each file (owner, key, mime, size, visibility).

## Upload validation (server side)
- [ ] Authentication + authorization before accepting the upload.
- [ ] Max size enforced by the server/proxy (`client_max_body_size`, multer `limits`,
      `upload_max_filesize`, `MAX_CONTENT_LENGTH`).
- [ ] Allow-list of types; check **magic bytes**, not only extension or client `Content-Type`.
- [ ] Reject executable/script types (`.php`, `.phtml`, `.phar`, `.jsp`, `.asp(x)`, `.exe`,
      `.sh`, `.js` served as HTML, `.html`/`.svg` uploaded by users unless sanitised -
      SVG can contain scripts).
- [ ] Server-generated file names/keys (UUID); original name stored only as metadata.
- [ ] Path traversal impossible (`../` in names ignored because names are not used as paths).
- [ ] Images re-encoded / resized (removes polyglots), EXIF (GPS) stripped from user photos.
- [ ] Archives (zip) not extracted without zip-slip and zip-bomb protection.
- [ ] Optional: antivirus scan for documents shared with other users.
- [ ] Count/quota limits per user (abuse, cost).

## Access
- [ ] Buckets private by default; **no public listing**.
- [ ] Private files served via permission-checked endpoint or **short-lived signed URLs**
      (minutes). No permanent public links to invoices/IDs/contracts.
- [ ] Public assets in a separate bucket/prefix from user uploads.
- [ ] `Content-Disposition: attachment` for user-uploaded documents; `X-Content-Type-Options:
      nosniff`; serve user content from a separate domain/CDN if it may contain HTML/SVG.
- [ ] Presigned upload URLs restrict key, content type, size (POST policy) and expiry.
- [ ] Download endpoint checks ownership (IDOR on `/files/:id`).

## Provider config (`[YOU]` items where they live in the cloud console)
- **S3/R2/B2**: Block Public Access on; bucket policy least privilege; IAM user only for this
  bucket; versioning/lifecycle; CORS limited to your origins and methods.
- **GCS**: uniform bucket-level access; no `allUsers` on private buckets.
- **Azure Blob**: container access level `Private`; SAS tokens short-lived and scoped.
- **Firebase Storage rules**: no `allow read, write: if true`; check `request.auth.uid` in
  path; validate `request.resource.size` and `contentType`.
- **Supabase Storage**: bucket not public unless intended; policies on `storage.objects`.
- **Cloudinary**: signed uploads (no unsigned preset for user uploads), API secret server-side.

## Lifecycle
- [ ] Deleting a record deletes or schedules deletion of its files (no orphans).
- [ ] Temporary files cleaned.
- [ ] Backups of storage in a separate private location.
