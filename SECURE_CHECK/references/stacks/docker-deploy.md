# Docker, docker-compose, Kubernetes, CI/CD

**Detect:** `Dockerfile`, `docker-compose*.yml`, `k8s/`, `helm/`, `.github/workflows/`,
`.gitlab-ci.yml`, `Jenkinsfile`, `bitbucket-pipelines.yml`.

**Label:** `CONFIG` (but secrets inside → `SECRET` finding).

**Docker**
- [ ] No secrets in `ENV`/`ARG` or copied files (image layers keep them forever). Use runtime
      env, Docker secrets, BuildKit `--mount=type=secret`.
- [ ] `.dockerignore` excludes `.git`, `.env*`, `node_modules`, keys, tests, `secure-check-report`.
- [ ] Non-root user (`USER app`), minimal base image, pinned versions/digests.
- [ ] Multi-stage build: dev tools and source maps not in the final image.
- [ ] Healthcheck; no `--privileged`; no Docker socket mounted.

**docker-compose**
- [ ] Database ports not published to `0.0.0.0` in production (`"5432:5432"` → remove or bind
      `127.0.0.1`).
- [ ] Passwords via `env_file` (gitignored) or secrets - not literals like
      `POSTGRES_PASSWORD: postgres`.
- [ ] Admin tools (adminer, phpMyAdmin, Mongo Express) not exposed publicly.

**Kubernetes**
- [ ] Secrets in `Secret` objects / external secret manager, not ConfigMaps or plain YAML in
      repo (base64 is not encryption).
- [ ] `securityContext`: `runAsNonRoot`, `readOnlyRootFilesystem`, drop capabilities.
- [ ] NetworkPolicies so only the backend can reach the DB.
- [ ] Resource limits.

**CI/CD**
- [ ] Secrets in CI secret store, masked; not echoed.
- [ ] `pull_request_target` workflows do not run untrusted code with secrets.
- [ ] Third-party actions pinned to a commit SHA.
- [ ] Least-privilege `permissions:` in GitHub Actions.
- [ ] Deploy keys / cloud credentials scoped per environment; OIDC preferred over long-lived
      keys.
- [ ] Optional: run SECURE_CHECK `QUICK` mode in CI (`templates/ci/`).

**Verify:** `docker build .`, `docker compose config`, `hadolint` (if installed),
`docker history <image>` to check no secrets in layers.
