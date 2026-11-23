# Flask / FastAPI / Starlette

**Detect:** `flask` / `fastapi` in requirements; `app = Flask(__name__)`,
`app = FastAPI()`.

**Boundary:** Python code = `BE`; Jinja templates render server-side; `static/` = `FE`.

**Secrets/env:** `app.secret_key`/`SECRET_KEY` from env (not literal); `pydantic-settings`
for FastAPI config.

**Database branch:** SQLAlchemy / SQLModel / Tortoise / Motor / PyMongo. Watch
`text(f"...")`, `execute("..." % x)`, `.format()` in SQL. Put queries in `repositories/`.

**File storage branch:** Flask `request.files` + `secure_filename` is **not enough** - use
server-generated names, `MAX_CONTENT_LENGTH`, content checks; FastAPI `UploadFile` - read in
chunks and enforce size. Store via `storage/` adapter (boto3, google-cloud-storage).

**Top risks**
- `app.run(debug=True)` / Werkzeug debugger exposed (remote code execution).
- No CSRF in Flask forms (use Flask-WTF) when cookie sessions are used.
- `render_template_string` with user input (SSTI).
- `Markup()`/`|safe` with user data.
- FastAPI: endpoints missing `Depends(get_current_user)`; response models not set →
  leaking fields (`response_model=UserPublic`); CORS `allow_origins=["*"]` with
  `allow_credentials=True`.
- JWT via `python-jose`/`PyJWT` without `algorithms=[...]`.
- `subprocess` with `shell=True`, `yaml.load` without `SafeLoader`, `pickle`.
- No rate limit (`slowapi`, `flask-limiter`).

**Target mapping**
```
app/
  main.py                  create app, middleware, routers
  api/routes/              routers / blueprints (thin)
  services/                business logic
  policies/                authorization
  schemas/                 pydantic / marshmallow (validation + output)
  db/ { session.py, models/, repositories/, migrations/ (alembic) }   DATABASE branch
  storage/ { service.py, adapters/ }                                  FILE STORAGE branch
  core/config.py           settings from env
```

**Verify:** `pytest`, `python -m compileall`, `pip-audit`, start with `uvicorn`/`flask run`.
