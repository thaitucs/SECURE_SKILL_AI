# Java / Kotlin - Spring Boot (and Jakarta EE, Ktor, Micronaut, Quarkus)

**Detect:** `pom.xml`/`build.gradle(.kts)` with `spring-boot-starter-*`; `@SpringBootApplication`.

**Boundary:** all server code = `BE`; `src/main/resources/static` and `templates` = served
content.

**Secrets/env:** `application.properties|yml` must not hold real passwords - use env
placeholders `${DB_PASSWORD}`, Vault, or cloud secret managers. Check profiles
`application-prod.yml` committed with secrets.

**Database branch:** Spring Data repositories / JPA entities / jOOQ / MyBatis. Watch
`createNativeQuery` / `@Query(nativeQuery=true)` with concatenation, `JdbcTemplate` string
building, MyBatis `${}` (use `#{}`).

**File storage branch:** `MultipartFile` with `spring.servlet.multipart.max-file-size`,
content checks (Apache Tika), storage service with S3/GCS/Azure SDK.

**Top risks**
- Spring Security misconfig: `permitAll()` too broad, `csrf().disable()` with cookie sessions,
  missing method security (`@PreAuthorize`) for ownership.
- Actuator endpoints exposed (`management.endpoints.web.exposure.include=*`) → env/heapdump
  leak.
- Jackson default typing / Java deserialization of untrusted data.
- Entities returned directly as JSON (leaks fields, mass assignment) - use DTOs.
- Log4j/Spring versions with known CVEs.
- XXE in XML parsers (disable DTDs).

**Target mapping:** `controller/` · `service/` (logic) · `security/` + `policy/` ·
`dto/` + validation (`@Valid`) · `repository/` + `entity/` (DATABASE) · `storage/` (STORAGE)
- or package-by-feature.

**Verify:** `mvn verify` / `gradle build`, OWASP Dependency-Check if available.
