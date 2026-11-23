# Django (and Django REST Framework)

**Detect:** `django` in requirements; `manage.py`, `settings.py`, `urls.py`, `apps.py`.

**Boundary:** Python code = `BE`; `templates/` render on the server (`FE` output, but escaping
is server-side); `static/` = `FE`. A separate SPA folder = `FE`.

**Secrets/env:** `SECRET_KEY`, DB password, email password from env (`django-environ`,
`os.environ`). `SECRET_KEY = 'django-insecure-...'` committed → High (Critical if deployed).

**Database branch:** `models.py`, `migrations/`. Watch `raw()`, `extra()`, `RawSQL`,
`cursor.execute(f"...")`. Use `selectors.py`/`repositories.py` for complex reads.

**File storage branch:** `FileField`/`ImageField` + `django-storages` (S3/GCS/Azure).
`MEDIA_ROOT` must not be served by Django in production with `DEBUG`; private media served
through a view with permission checks or signed URLs (`AWS_QUERYSTRING_AUTH=True`).
Validate size/type (`FileExtensionValidator` + content check).

**Top risks**
- `DEBUG = True` in production; `ALLOWED_HOSTS = ['*']`.
- Missing `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`,
  `SECURE_HSTS_SECONDS`, `SECURE_CONTENT_TYPE_NOSNIFF` (run `manage.py check --deploy`).
- `@csrf_exempt` on state-changing views.
- `|safe`, `mark_safe`, `{% autoescape off %}` with user data.
- DRF: `permission_classes = [AllowAny]` defaults, missing object-level permissions
  (`has_object_permission`), `fields = '__all__'` in serializers (leaks + mass assignment),
  no throttling (`DEFAULT_THROTTLE_CLASSES`).
- Admin at `/admin/` with weak passwords (add 2FA, rename path optional).
- `pickle` loads of user data.

**Target mapping**
```
<app>/views.py        thin (HTTP)          <app>/services.py   business logic
<app>/permissions.py  authorization        <app>/selectors.py  DB reads
<app>/models.py       DATABASE branch      <app>/storage.py    FILE STORAGE branch
<app>/serializers.py  validation + output shape
```

**Verify:** `python manage.py check --deploy`, `python manage.py test`, `pip-audit`.
