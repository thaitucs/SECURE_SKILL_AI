# Checklist - APIs (REST, GraphQL, gRPC, webhooks)

Based on OWASP API Security Top 10 (2023).

| # | Risk | Check |
|---|------|-------|
| API1 | Broken Object Level Authorization (BOLA/IDOR) | Every endpoint with an object id checks the caller may access that object. Try mentally: "what if I change `:id` to someone else's?" Prefer non-guessable ids **and** checks (UUIDs alone are not authorization). |
| API2 | Broken Authentication | Tokens validated on every request (signature, `exp`, issuer, audience). API keys hashed in DB, revocable, scoped. No auth in query strings. Rate-limited login/token endpoints. |
| API3 | Broken Object Property Level Authorization | Responses use explicit serializers/DTOs (no `password_hash`, `email` of others, internal flags). Requests use allow-listed writable fields (no mass assignment of `role`, `price`, `verified`). |
| API4 | Unrestricted Resource Consumption | Pagination with max page size, body size limits, upload limits, timeouts, rate limits per user/IP, GraphQL depth/complexity limits, limits on expensive operations (PDF/AI/SMS/email). |
| API5 | Broken Function Level Authorization | Admin/internal endpoints require admin role on the server. No "hidden" endpoints relying on obscurity (`/api/admin/*`, `/internal/*`, `/debug/*`). HTTP method checks (GET vs DELETE). |
| API6 | Unrestricted Access to Sensitive Business Flows | Purchase, signup, voting, coupon, referral, booking flows protected from automation (rate limits, CAPTCHA, device/account limits). |
| API7 | Server-Side Request Forgery | URL inputs fetched server-side are validated against allow-lists; internal IP ranges and metadata endpoints blocked; redirects not followed blindly. |
| API8 | Security Misconfiguration | CORS allow-list, security headers, TLS, verbose errors off, unused methods disabled, GraphQL introspection off in prod (unless public), Swagger/OpenAPI UI not public for private APIs. |
| API9 | Improper Inventory Management | Old versions (`/v1`) retired or equally secured, staging/test APIs not public or protected, documented list of endpoints. |
| API10 | Unsafe Consumption of APIs | Data from third-party APIs validated like user input; TLS verified; timeouts; webhook payloads signature-verified. |

## Extra checks

- [ ] Input validation schema on every endpoint (zod/joi/class-validator/pydantic/
      FormRequest/Bean Validation).
- [ ] Consistent error format without stack traces.
- [ ] Idempotency keys for payment/order creation.
- [ ] Webhook endpoints: signature check, replay protection (timestamp), no auth bypass.
- [ ] GraphQL: per-field authorization, query depth/cost limits, batching limits,
      persisted queries for public clients if possible.
- [ ] gRPC: TLS, auth interceptors, message size limits.
- [ ] API keys for third parties used by **your** server stay on the server.
- [ ] Logs include request ids, exclude secrets/PII.
