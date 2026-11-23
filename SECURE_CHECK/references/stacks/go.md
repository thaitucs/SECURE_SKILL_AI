# Go (net/http, Gin, Echo, Fiber, Chi)

**Detect:** `go.mod`; imports `github.com/gin-gonic/gin`, `labstack/echo`, `gofiber/fiber`,
`go-chi/chi`, `net/http`.

**Boundary:** `BE`. Embedded static files (`embed.FS`) are public - check what is embedded.

**Secrets/env:** `os.Getenv` / config libs; no literals; `.env` ignored.

**Database branch:** `database/sql`, `sqlx`, `pgx`, GORM, ent. Use placeholders (`$1`/`?`);
watch `fmt.Sprintf` in queries, GORM `Raw`/`Exec`/`Where` with string building, `Order`
from input.

**File storage branch:** `r.ParseMultipartForm(maxMemory)` + `http.MaxBytesReader`,
`http.DetectContentType`, server names, storage package with S3/GCS SDK.

**Top risks:** missing auth middleware on route groups; ownership checks; `http.ServeFile`
/ `filepath.Join` with user paths (traversal - use `filepath.Clean` + root check or
`os.Root`); `exec.Command("sh", "-c", input)`; `InsecureSkipVerify: true`; no timeouts on
`http.Server` (Slowloris); `html/template` vs `text/template` (use `html/template` for HTML);
JWT libs without algorithm checks; old Go versions (`govulncheck`).

**Target mapping**
```
cmd/server/main.go
internal/http/       handlers + middleware + routes
internal/service/    business logic
internal/policy/     authorization
internal/repository/ DATABASE branch
internal/storage/    FILE STORAGE branch
internal/config/
```

**Verify:** `go build ./...`, `go vet ./...`, `go test ./...`, `govulncheck ./...`.
