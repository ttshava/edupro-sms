# 08 — Deployment

## 8.1 Local Development

- Docker Desktop on Windows, using the official `frappe_docker` setup
  (config lives in `docker/`).
- Start Docker Desktop → start containers → run `bench` commands inside
  the container (or via `docker compose exec`).

## 8.2 Environments

| Environment | Status | Notes |
|---|---|---|
| Local (dev) | Planned | Docker on the owner's Windows machine |
| Pilot school (staging/prod) | Not started | One Frappe site for the pilot school; hosting TBD (likely a small VPS) once MVP is ready |
| Additional schools | Future | Each new school = a new site on shared infra (per `docs/02` §2.2) |

## 8.3 Performance & Scalability Targets

| Metric | Target (single school) | Target (10 schools, shared infra) |
|---|---|---|
| Students | 2,000 | 20,000 |
| Concurrent users | 100 | 1,000 |
| API response time | < 200ms | < 500ms |
| PDF generation time | < 5 sec/student | < 10 sec/student |
| Email processing | 1,000/hr | 10,000/hr |
| Database query time | < 50ms | < 100ms |
| Storage (PDFs/year) | ~2GB | ~20GB |

### Optimization strategies

1. Indexes on `student`, `class`, `term` Link fields (`docs/02` §2.4).
2. Redis caching for frequently accessed data.
3. All PDF generation and email sending as background jobs (RQ), never
   inline in a request.
4. CDN for static assets once beyond local dev.
5. Read replicas for reporting, if/when needed at multi-school scale.
6. Horizontal scaling (load balancer + multiple app instances) — a
   later-phase concern, not MVP.

## 8.4 Security & Compliance

| Area | Requirement |
|---|---|
| Authentication | Frappe's built-in password hashing (bcrypt); 2FA optional |
| Authorization | Role-based access control matching `docs/11_Roles_And_Permissions.md` |
| Data encryption | TLS 1.3 for all traffic; encryption at rest for backups |
| Session management | Frappe's session handling — confirm timeout policy (default vs. custom) before pilot launch |
| Audit trail | Frappe's built-in document versioning + Comments; see `.claude/CODING_STANDARDS.md` |
| Privacy | Data anonymization capability for a student's departure/deletion request |
| File security | Signed/permission-checked URLs for PDF access, not public file links |
| Rate limiting | Not built into Frappe by default — add at the reverse-proxy layer (Nginx) if exposed publicly |

Note: the source spec mentioned JWT authentication for a custom API layer.
For MVP, the frontend is Frappe Desk/portal, which uses Frappe's native
session-cookie auth — JWT only becomes relevant if/when a separate
mobile/SPA client is built (post-MVP). See `docs/09_API.md`.

## 8.5 Deployment Checklist

**Pre-deployment:** code review completed; tests passed
(`docs/07_Testing.md`); site migrations tested; SSL certificate installed;
site config/environment variables set; backups automated.

**Deployment steps:**
1. Pull `edupro_sms` app onto the target site/bench.
2. Install/update the app on the relevant site(s).
3. Run `bench migrate`.
4. Build frontend assets (`bench build`).
5. Restart bench/supervisor.
6. Verify health-check endpoint.
7. Update DNS if needed (new school site).
8. Enable monitoring.

**Post-deployment:** verify all user roles work; test email delivery; test
PDF generation; check logging; run performance spot-check against §8.3;
update `docs/` and `.claude/CHANGELOG.md`.

## 8.6 Ongoing Support & Maintenance

See `docs/01_Project_Overview.md` §1.6 for the support/maintenance table
(bug fix SLA, backup cadence, security scanning, monitoring, training,
feature request intake).
