# 08 — Deployment

Two environments exist: **local development** (Docker, Frappe v15) and
**production** (Frappe Cloud, Frappe v16). This doc covers both.

## 8.1 Local Development (Docker)

Docker Desktop on Windows, using the official `frappe_docker` repo
cloned into `frappe_docker/` at the project root (gitignored — it's a
vendored clone, not our source).

**Stack:** Frappe 15.113.4, ERPNext 15.115.0, Education 15.5.3, Python
3.11.15, Node 18.20.2. Site: `edupro.localhost`.

`frappe_docker/apps.json`:

```json
[
  { "url": "https://github.com/frappe/erpnext", "branch": "version-15" },
  { "url": "https://github.com/frappe/payments", "branch": "version-15" },
  { "url": "https://github.com/frappe/education", "branch": "version-15.2" }
]
```

**Gotcha:** the Education app uses point-release branches
(`version-15.1`/`version-15.2`), not a plain `version-15` branch — check
`git ls-remote --heads https://github.com/frappe/education` before
bumping.

### Day-to-day: start/stop

```bash
cd frappe_docker
docker compose -p edupro -f compose.edupro.yaml up -d      # start
docker compose -p edupro -f compose.edupro.yaml down        # stop (keeps data)
docker compose -p edupro -f compose.edupro.yaml exec backend bash   # shell in
```

**After editing any `edupro_sms` Python file, restart the containers —
don't just `bench clear-cache`.** Gunicorn workers cache already-imported
Python modules in memory; `clear-cache` only clears Frappe's
application-level metadata caches, not the running processes.

```bash
docker compose -p edupro -f compose.edupro.yaml restart backend queue-short queue-long scheduler websocket
```

### The `edupro_sms` app lives on the host

Source is at `apps/edupro_sms/` (project root locally), bind-mounted
into every bench-role container. Edit directly with your editor —
changes are visible in the container immediately (Python changes need a
container restart; JS/CSS need `bench build --app edupro_sms`; schema
changes need `bench migrate`).

The other apps (`frappe`, `erpnext`, `education`) are **not**
bind-mounted — they're baked into the custom image only. They should
never be edited directly.

### Do not use the ERPNext Setup Wizard

Logging in as Administrator on a fresh site prompts ERPNext's Company/
fiscal-year setup wizard. **Skip it** — `edupro_sms` uses its own
`School Settings` Single DocType specifically so schools don't need
ERPNext's company/finance setup at all.

## 8.2 Production (Frappe Cloud)

**Bench:** `firstclass` · **Site:** `firstclass.frappe.cloud` · **Custom
domain:** `firstclasshighschool.edupro.co.zw` (CNAME, DNS hosted at
`edupro.co.zw`'s registrar) · **Stack:** Frappe 16.27.1, ERPNext 16.28.0,
Education, `edupro_sms`.

### How production data got there

The production site was populated by restoring a full backup from the
local Frappe v15 instance (492 students, 40 instructors, 28 courses, and
all related academic/finance data), letting Frappe Cloud run the
standard v15→v16 migration during restore. A second local app,
`edupro_primary` (an in-progress Moodle/LMS integration), was
deliberately excluded from the restore — it's local-dev-only for now.

### Frappe app structure requirements

Getting a custom app onto Frappe Cloud via GitHub requires the standard
Frappe app layout, which this repo didn't originally have:

- **Package naming must match exactly.** Frappe's asset build keys
  public asset paths by the app's *module* name (`edupro_sms`,
  underscore), not the pip package name. `pyproject.toml`'s
  `[project].name` must be `edupro_sms`, not a hyphenated variant —
  otherwise the build fails with a cryptic `paths[0] must be of type
  string` error deep in esbuild.
- **`modules.txt` is required** (`edupro_sms/modules.txt` — one line,
  `Edupro SMS`) so Frappe knows which module(s) the app owns.
- **DocTypes, Print Formats, and Reports must live under the nested
  module folder** — `edupro_sms/edupro_sms/doctype/`, not
  `edupro_sms/doctype/` — or `bench migrate` won't find them.
- **All internal imports must be package-qualified**
  (`from edupro_sms.grading import ...`, not a bare `from grading
  import ...`) — a bare import only works when the app's own directory
  happens to be on `sys.path`, which isn't guaranteed once the app is
  installed as a normal Python package.
- **`hooks.py` must declare every integration point explicitly** — boot
  session, portal routing (`role_home_page`), Jinja methods, row-level
  permissions (`permission_query_conditions`/`has_permission`),
  `doc_events`, and fixtures. A hooks.py missing any of these lets the
  app install but silently drops that functionality.

### DNS / custom domain

The custom domain is a CNAME record (`firstclasshighschool` →
`firstclass.frappe.cloud`) added at the DNS registrar. A pre-existing A
record for the same subdomain name will conflict — DNS doesn't allow a
CNAME to coexist with any other record type at the same name — so an old
A record must be deleted first if the subdomain was previously
provisioned another way (e.g. by a hosting panel's own subdomain
feature).

### Known platform issue: search-index migration step

Frappe v16.27.1 has a bug where the final "rebuild search index" step of
`bench migrate` can fail with a `PicklingError` trying to serialize the
session user for a background job. This doesn't affect the actual data
migration (which completes fully beforehand) — only this cosmetic
finalization step. If a Frappe Cloud site shows "Broken / site creation
failed" after an otherwise-successful restore, this is the likely cause;
the fix is `bench migrate --skip-search-index` run by Frappe Cloud
support (a site flagged this way blocks self-service migrate/domain
actions until support intervenes).

### Super-admin access

Frappe Cloud's "Login As Administrator" button provides passwordless
super-admin access — the standard way to get into Desk. If a site is in
the "Broken" state, this is blocked too (support has to clear the flag
first).

## 8.3 Performance & Scalability Targets

| Metric | Target (single school) | Target (10 schools, shared infra) |
|---|---|---|
| Students | 2,000 | 20,000 |
| Concurrent users | 100 | 1,000 |
| API response time | < 200ms | < 500ms |
| PDF generation time | < 5 sec/student | < 10 sec/student |
| Email processing | 1,000/hr | 10,000/hr |
| Database query time | < 50ms | < 100ms |

### Optimization strategies

1. Indexes on `student`, `student_group`, `academic_term` Link fields
   (`docs/02_Database.md` §2.4).
2. Redis caching for frequently accessed data.
3. PDF generation and email sending as background jobs (RQ), never
   inline in a request.
4. Read replicas for reporting, if/when needed at multi-school scale.
5. Horizontal scaling (load balancer + multiple app instances) — a
   later-phase concern.

## 8.4 Security & Compliance

| Area | Approach |
|---|---|
| Authentication | Frappe's built-in password hashing |
| Authorization | Role-based access control (`docs/11_Roles_And_Permissions.md`) |
| Data encryption | TLS for all traffic (Frappe Cloud manages certificates) |
| Session management | Frappe's native session handling |
| Audit trail | Frappe's built-in document versioning + Comments |
| File security | Attach fields are permission-checked, not public links |
| Rate limiting | Not built into Frappe by default — add at the reverse-proxy layer if ever needed |

The frontend is Frappe Desk/portal pages, which use Frappe's native
session-cookie auth. See `docs/09_API.md` for API-key auth if a
separate client is ever built.

## 8.5 Deployment Checklist (pushing an app update to production)

1. Push the change to the app's GitHub repo (`main` branch).
2. On Frappe Cloud: bench → Apps → Edupro SMS → **Fetch Latest Updates**.
3. Bench → **Update Available** → select Edupro SMS → select the site →
   **Deploy and update site** (builds the new image and migrates the
   site in one step).
4. Verify: site loads, core workflows still work (marks entry → review
   → approve → publish → email), no new errors in the site's Error Log.
5. Update `docs/` and `.claude/CHANGELOG.md` if the change is
   user-facing or structural.

## 8.6 Ongoing Support & Maintenance

See `docs/01_Project_Overview.md` §1.6.
