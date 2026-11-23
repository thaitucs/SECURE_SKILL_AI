# .NET - ASP.NET Core (MVC, Web API, Minimal APIs, Blazor)

**Detect:** `*.csproj` with `Microsoft.NET.Sdk.Web`, `Program.cs`, `Controllers/`.

**Boundary:** server code = `BE`; `wwwroot/` = public static; **Blazor WebAssembly** code runs
in the browser = `FE` (no secrets, no authoritative logic). Blazor Server runs on server.

**Secrets/env:** `appsettings.json` / `appsettings.Production.json` must not contain real
connection strings or keys - use User Secrets (dev), env vars, Azure Key Vault.

**Database branch:** EF Core `DbContext` (`Data/`), repositories. Watch `FromSqlRaw` /
`ExecuteSqlRaw` with concatenation (use `FromSqlInterpolated` or parameters), Dapper string
building.

**File storage branch:** `IFormFile` with `RequestSizeLimit`, extension + signature checks,
store outside `wwwroot` or in Azure Blob/S3; serve via controller with authorization.

**Top risks:** missing `[Authorize]` (prefer a fallback policy requiring auth); resource-
based authorization for ownership (`IAuthorizationService`); `app.UseDeveloperExceptionPage()`
in production; CORS `AllowAnyOrigin` + credentials; `[IgnoreAntiforgeryToken]` on forms;
`Html.Raw` with user data; `BinaryFormatter`; overposting (bind DTOs, not entities);
missing `UseHsts()`/`UseHttpsRedirection()`; rate limiting middleware (`AddRateLimiter`).

**Target mapping:** `Controllers/` or `Endpoints/` · `Services/` (logic) · `Authorization/`
(policies/handlers) · `Validators/` (FluentValidation) · `Data/` + `Repositories/`
(DATABASE) · `Storage/` (STORAGE).

**Verify:** `dotnet build`, `dotnet test`, `dotnet list package --vulnerable`.
