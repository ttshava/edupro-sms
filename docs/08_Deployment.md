# 08 — Deployment

## 8.1 Local Development

**Status: running** (set up 2026-07-03). Docker Desktop on Windows, using
the official `frappe_docker` repo cloned into `frappe_docker/` at the
project root (not a `docker/` subfolder — that was the original plan but
the actual working setup lives at the top level; `frappe_docker/` is
gitignored since it's a vendored clone, not our source).

### What's built

A custom image `edupro-sms:v15` (via `images/custom/Containerfile`, the
only frappe_docker image variant that both pins an exact Python version
*and* supports baking in extra apps via `apps.json`):

- Frappe **15.113.4**, ERPNext **15.115.0**, Education **15.5.3**
- Python **3.11.15**, Node 18.20.2
- One site: `edupro.localhost`, all three apps + our own `edupro_sms`
  (0.0.1) installed, developer mode on

`frappe_docker/apps.json`:

```json
[
  { "url": "https://github.com/frappe/erpnext", "branch": "version-15" },
  { "url": "https://github.com/frappe/payments", "branch": "version-15" },
  { "url": "https://github.com/frappe/education", "branch": "version-15.2" }
]
```

**Gotcha:** the Education app doesn't use a plain `version-15` branch — it's
`version-15.1`/`version-15.2` (point-release branches). Check
`git ls-remote --heads https://github.com/frappe/education` before bumping.

**Gotcha:** frappe_docker's shell scripts (`resources/core/*.sh`) got
checked out with CRLF line endings on Windows (Git's `core.autocrlf=true`
default), which breaks their shebang inside the Linux container
(`exec: no such file or directory`, containers crash-loop). Fixed once with
`sed -i 's/\r$//'` on the affected `.sh` files before building — if
`frappe_docker/` is ever re-cloned, redo this before building.

### Build command (for rebuilding, e.g. after bumping versions)

```bash
cd frappe_docker
docker build \
  --build-arg=FRAPPE_PATH=https://github.com/frappe/frappe \
  --build-arg=FRAPPE_BRANCH=version-15 \
  --build-arg=PYTHON_VERSION=3.11 \
  --build-arg=NODE_VERSION=18.20.2 \
  --secret=id=apps_json,src=apps.json \
  --tag=edupro-sms:v15 \
  --file=images/custom/Containerfile .
```

### Day-to-day: start/stop

```bash
cd frappe_docker
docker compose -p edupro -f compose.edupro.yaml up -d      # start
docker compose -p edupro -f compose.edupro.yaml down        # stop (keeps data)
docker compose -p edupro -f compose.edupro.yaml ps           # status
docker compose -p edupro -f compose.edupro.yaml logs -f backend
docker compose -p edupro -f compose.edupro.yaml exec backend bash   # shell in, run bench commands
```

**After editing any `edupro_sms` Python file (controllers, hooks, API
modules), restart the containers — don't just `bench clear-cache`.**
Gunicorn workers cache already-imported Python modules in memory;
`clear-cache` only clears Frappe's application-level caches (docfield
metadata etc.), not the running processes. A code change can be
completely invisible over HTTP while `bench console` (a fresh process)
shows it working — this bit us once in Sprint 7 (see
`.claude/DECISIONS.md` 0009). JSON-only changes (DocType fields via
`developer_mode` export, fixtures) don't need this — only actual `.py`
logic changes do.

```bash
docker compose -p edupro -f compose.edupro.yaml restart backend queue-short queue-long scheduler websocket
```

**`compose.edupro.yaml` is a generated file** — merged from `compose.yaml`
+ `overrides/compose.mariadb.yaml` + `overrides/compose.redis.yaml` +
`overrides/compose.noproxy.yaml` + `overrides.local/compose.edupro-sms-app.yaml`.
Regenerate it after changing `.env` or any override:

```bash
docker compose --env-file .env \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.noproxy.yaml \
  -f overrides.local/compose.edupro-sms-app.yaml \
  -p edupro config > compose.edupro.yaml
```

### The `edupro_sms` app lives on the host, not just in the container

`edupro_sms` source is at `apps/edupro_sms/` (project root), bind-mounted
into every bench-role container (backend/queue-short/queue-long/scheduler/
websocket/configurator) via `overrides.local/compose.edupro-sms-app.yaml`.
Edit it directly with VS Code — changes are visible in the container
immediately (Python changes need a `bench restart` equivalent via
container restart or `bench migrate` for schema changes; JS/CSS need
`bench build --app edupro_sms`). It has its own git repo
(`apps/edupro_sms/.git`, separate from this project's repo — see
`CODING_STANDARDS.md`).

**The Python venv (`env/`) is also not shared between containers by
default** — each bench-role container gets its own independent copy from
the image, so `pip install -e apps/edupro_sms` in one container doesn't
make edupro_sms importable in another. Fixed with a shared named volume
`bench-env` (mounted at `/home/frappe/frappe-bench/env` on every
bench-role service) plus a `configurator` command override that
re-installs `edupro_sms` into it on every startup, before backend starts
(everything else `depends_on: configurator`). This is why `configurator`
also needs the `apps/edupro_sms` bind mount even though it doesn't run
the app. Without this, edupro_sms silently breaks on the next
`docker compose down && up -d` — see `.claude/DECISIONS.md` 0006 for the
full story and how it was diagnosed.

The other three apps (`frappe`, `erpnext`, `education`) are **not**
bind-mounted — they're baked into the `edupro-sms:v15` image only. That's
intentional: we never edit core Frappe/ERPNext/Education, so there's
nothing to gain from host-mounting them, and it keeps the image
self-contained for those.

Site: **http://localhost:8080** — `Administrator` / password in
`frappe_docker/.env` (`ADMIN_PASSWORD`, dev-only, gitignored).
`compose.edupro.yaml` is the merged config (`compose.yaml` +
`overrides/compose.mariadb.yaml` + `overrides/compose.redis.yaml` +
`overrides/compose.noproxy.yaml`), pre-generated so day-to-day commands
don't need to restate all the `-f` flags.

Site data lives in Docker-managed volumes (`edupro_sites`, `edupro_db-data`,
`edupro_redis-queue-data`), not host bind-mounts — matches frappe_docker's
own default and avoids Windows bind-mount permission issues. Use
`bench backup` + `docker cp` to pull a backup out to the host `backups/`
folder when needed, rather than relying on a live bind mount.

### Sample portal accounts (all fictional, `@example.edupro.test`)

Password for all of these: `edupro_test_2026`. Portal URL:
http://localhost:8080/my-reports. These are portal-only (`user_type =
Website User`) — logging in lands on `/edu-portal`, not Desk.

| Role | Name | Username | Notes |
|---|---|---|---|
| Student | Kwabena Owusu | `kwabena.owusu@example.edupro.test` | Form 4A — report Published |
| Student | Adjoa Asante | `adjoa.asante@example.edupro.test` | Form 4A — report Published |
| Student | Yaw Darko | `yaw.darko@example.edupro.test` | Form 4B — report not yet generated |
| Student | Abena Mensah | `abena.mensah@example.edupro.test` | Form 4B — report not yet generated |
| Guardian | Ama Owusu | `ama.owusu@example.edupro.test` | guardian of Kwabena **and** Abena — multi-child test case |
| Guardian | Kofi Asante | `kofi.asante@example.edupro.test` | guardian of Adjoa |
| Guardian | Efua Darko | `efua.darko@example.edupro.test` | guardian of Yaw |

**Gotcha:** the Student doctype auto-provisions a `User` on insert, and
it defaults to `user_type = System User`, not `Website User` — harmless
for permissions (role-based, not user_type-based) but wrong for the
login UX (System User defaults to a Desk redirect that then fails
permission checks, rather than landing on the portal). Fixed on all 7
accounts above; set `user_type = Website User` explicitly on any new
Student/Guardian portal accounts going forward.

**Gotcha:** a one-off performance-check script (`docs/08` §8.3) left 20
throwaway `User` accounts behind (`perfcheck*@example.edupro.test`) even
after its Student/Report Card cleanup — Student creation's auto-provisioned
User isn't deleted by `frappe.delete_doc("Student", ...)`. Clean up Users
explicitly in any future one-off script that creates Students.

### Do not use the ERPNext Setup Wizard

Logging in as Administrator on a fresh site prompts ERPNext's Company/
fiscal-year setup wizard (`/setup-wizard/0`). **Skip it** — Edupro SMS
uses its own `School Settings` Single DocType (per `docs/02_Database.md`
§2.2 / `.claude/DECISIONS.md` 0004) specifically so schools don't need
ERPNext's company/finance setup at all. The wizard is also actively
broken in this environment: submitting it throws `AttributeError:
'NoneType' object has no attribute 'replace'` in
`erpnext/setup/setup_wizard/operations/install_fixtures.py` (the
"Country" field isn't reaching the backend).

**This took three attempts to actually fix — see
`.claude/DECISIONS.md` 0011 for the full story** (kept deliberately
undiluted as a lesson in premature "fixed" claims). Summary of what's
actually in place on the running site:

1. `Installed Application` rows for `frappe` and `erpnext` both have
   `is_setup_complete = 1` (this is what `frappe.is_setup_complete()`
   actually reads — **not** `System Settings.setup_complete`, which
   does nothing here despite the field existing).
2. A minimal `Company` record exists ("First Class High" / "FCH"), so
   that flag doesn't get silently recomputed back to `0` (ERPNext
   recomputes it against whether any `Company` exists).
3. **The actual root cause of the save-triggered redirect loop:** the
   `desktop:home_page` default value had been left set to the literal
   string `"setup-wizard"` (a stray `DefaultValue` record, unrelated to
   any of the above). Client-side navigation after actions like Save
   sends the browser to `frappe.boot.home_page`, so this made the wizard
   the destination after every save, which then redirected itself away
   again since setup actually was complete — the visible "flashing and
   looping." Fixed with
   `frappe.db.set_default("desktop:home_page", "Workspaces")`.
4. `edupro_sms/edupro_sms/boot.py` (`boot_session` hook) additionally
   forces `sysdefaults.setup_complete = 1` on every session as
   defense-in-depth — not the fix for the bug above, but cheap
   insurance against the wizard resurfacing via some other stale
   default not yet discovered.

**How this was actually found:** curl/HTTP-status checks and even a
first round of in-browser confirmation both missed it, because the
redirect is client-side JS reacting to boot data — a page loading with
200 doesn't prove the client won't navigate away moments later, and
navigating-in-browser isn't the same test as the actual reported
action (Save). What worked: exporting a HAR file from DevTools and
grepping the *raw boot JSON* (not the bundled JS source, which contains
misleadingly similar-looking field-name references) for `sysdefaults`.

To "set up the school," fill in **School Settings**
(http://localhost:8080/app/school-settings) instead — confirmed working,
including Save, by the owner in-browser.

## 8.2 Environments

| Environment | Status | Notes |
|---|---|---|
| Local (dev) | **Running** | Docker on the owner's Windows machine — see §8.1 |
| Pilot school (staging/prod) | Not started | One Frappe site for the pilot school; hosting TBD (likely a small VPS) once MVP is ready |
| Additional schools | Future | Each new school = a new site on shared infra (per `docs/02` §2.2) |

## 8.3 Performance & Scalability Targets

| Metric | Target (single school) | Target (10 schools, shared infra) | **Measured, Sprint 8** |
|---|---|---|---|
| Students | 2,000 | 20,000 | — (untested at scale) |
| Concurrent users | 100 | 1,000 | — (untested) |
| API response time | < 200ms | < 500ms | — (not formally measured; interactive Desk/portal use felt instant on this single-container dev setup) |
| PDF generation time | < 5 sec/student | < 10 sec/student | **0.37 sec/student**, 20-student synthetic batch (`frappe.get_print` + `get_pdf`); extrapolates to ~1.2 min for 200 students |
| Report card generation | *(not in original target list)* | | **12 ms/student** (`generate_report_cards`, 20-student batch) |
| Marks entry (insert+submit) | *(not in original target list)* | | **127 ms/student** (Assessment Result insert + submit, 20-student batch) |
| Email processing | 1,000/hr | 10,000/hr | — (pipeline verified correct, not load-tested — see `docs/06` §6.6) |
| Database query time | < 50ms | < 100ms | — (not formally measured) |
| Storage (PDFs/year) | ~2GB | ~20GB | — (not measured; single sample PDF ≈ 24KB) |

**Measurement method:** a throwaway script created 20 synthetic students +
one Assessment Plan, timed marks entry / report generation / PDF
generation, then explicitly deleted everything it created (see gotcha
below). All comfortably inside target — PDF generation has roughly 13×
headroom against the 5 sec/student ceiling. Full 200-student load testing
and concurrent-user testing were not performed — this container is a
single-instance dev setup, not representative of production
concurrency. Re-run before pilot-school go-live on production-like infra.

**Gotcha:** `frappe.db.rollback()` does **not** reliably undo a script's
changes once any document has been `.submit()`ted — submission appears to
force an internal commit partway through. The first performance-check run
left real leftover data in the site despite an explicit rollback call at
the end; had to write an explicit cleanup script instead. Don't trust
`frappe.db.rollback()` alone to make a submit-heavy script side-effect-free
— verify with a count query afterward, or clean up explicitly.

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

## 8.5 MVP Release Readiness (as of 2026-07-03, end of Sprint 8)

| Area | Status |
|---|---|
| Core data model (Academic Year/Term, Class, Subject, People, Assessments) | ✅ Done — extends Frappe Education (`docs/03`) |
| Approval workflow (Draft → Pending → Reviewed → Approved/Rejected → Published) | ✅ Done, verified with real locking |
| Report card generation, class position | ✅ Done, verified |
| Report card PDF (IGCSE-branded) | ✅ Done, verified |
| Student/Guardian portal (`/my-reports`) | ✅ Done, verified over real HTTP incl. negative cases |
| Parent email delivery | ✅ Pipeline verified; **real SMTP not configured** (`docs/06` §6.6) |
| Permission scoping (Class Teacher/Student/Guardian) | ✅ Done for Report Card; other DocTypes use Role Permissions Manager defaults only (`docs/11` §11.2) |
| Automated tests (TC-01–TC-12) | ✅ 12/12 pass |
| Headmaster dashboard | ✅ Basic Script Report; no Desk button for `generate_report_cards` yet |
| Performance | ✅ Spot-checked at 20-student scale, well within targets; **not load-tested at 200+ students or with concurrent users** |
| UAT (real browser click-through) | ❌ Not done — checklist ready (`docs/07` §7.4), needs a human |
| Real pilot-school data | ❌ All data is sample/placeholder — School Settings, classes, subjects, people all need real data before go-live |
| Special-case handling (Absent/Exempt/Medical Withdrawal effects on totals) | ❌ Field exists, calculation logic doesn't use it yet (`docs/04` §4.3) |
| Desk UI trigger for report generation | ❌ Console/API only |
| Background-job wrapping for bulk PDF/email at scale | ❌ Works synchronously for the tested scale; needs `frappe.enqueue` wrapping before a real 200-student class |

**Bottom line:** the system is functionally complete and verified for the
documented MVP scope, running entirely on sample data. What's between
here and a real pilot-school launch is: real data entry (not a code
task), real SMTP configuration, a human UAT pass in an actual browser,
and the small list of "not yet built" polish items above — none of which
are architectural gaps, all straightforward follow-up work.

## 8.6 Deployment Checklist

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

## 8.7 Ongoing Support & Maintenance

See `docs/01_Project_Overview.md` §1.6 for the support/maintenance table
(bug fix SLA, backup cadence, security scanning, monitoring, training,
feature request intake).
