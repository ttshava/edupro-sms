# Decisions — Edupro SMS

Architecture Decision Log. One entry per significant decision — record what
was decided, why, and what alternatives were rejected. Append new entries at
the bottom; don't rewrite history, add a superseding entry instead.

---

## 0001 — Build on Frappe Framework, not a custom SMS from scratch

**Date:** 2026-07-03
**Status:** Accepted

**Decision:** Use the Frappe Framework (DocTypes, Workflows, Print Formats,
Role Permissions Manager, RQ background jobs) as the platform, rather than
building a bespoke school management system from scratch.

**Why:** The target is a multi-tenant SaaS product for multiple schools.
Frappe already provides a production-grade data layer, permission system,
workflow engine, PDF/print formatting, and admin UI (Desk), which would
otherwise be reimplemented and re-hardened from zero. The owner has prior
Moodle experience, making an ERP-style framework a comfortable fit.

**Rejected alternative:** Fully custom stack (e.g. Django/Node from
scratch) — more flexibility but far more time spent rebuilding
infrastructure Frappe already solves.

---

## 0002 — All customization lives in a dedicated custom app (`edupro_sms`)

**Date:** 2026-07-03
**Status:** Accepted

**Decision:** All Edupro-specific DocTypes, workflows, print formats,
reports, and automation live in a custom app named `edupro_sms`. Core Frappe
(and any future ERPNext) files are never modified directly.

**Why:** Keeps customizations upgradable, version-controlled, and portable
across sites/tenants. Future domains (finance, attendance, transport) become
their own apps rather than being folded into `edupro_sms`, so a school can
adopt modules independently — this directly supports the multi-tenant SaaS
goal.

---

## 0003 — Local development via Docker on Windows, not native Bench install

**Date:** 2026-07-03
**Status:** Accepted

**Decision:** Run Frappe locally using the official Docker setup rather than
installing Bench directly on Windows.

**Why:** Bench's native install story on Windows is unreliable (it targets
Linux/WSL). Docker gives a reproducible environment closer to production and
avoids fighting Windows-specific setup issues.

---

## 0004 — Multi-tenancy via one Frappe site per school, not a shared `School` table

**Date:** 2026-07-03 (confirmed by owner 2026-07-03)
**Status:** Accepted

**Decision:** Model multi-tenancy using Frappe's native pattern — one site
per school, all running the `edupro_sms` app — rather than a single shared
database with a `School` DocType and a `school_id` foreign key on every
other DocType (Student, Class, Marks, etc.).

**Why:** The source functional spec's ERD models multi-tenancy the way a
hand-rolled Django/Node app would (a `School` table, `school_id` on every
row). That's not how Frappe multi-tenancy works: Frappe already isolates
tenants at the site level (separate DB per site, shared codebase/app). Using
the native pattern means data isolation between schools is structural, not
something every query/permission rule has to remember to filter by
`school_id`. School-level settings (name, logo, motto, curriculum,
timezone) become a per-site **Single DocType** ("School Settings") instead
of rows in a shared table.

**Rejected alternative:** Literal ERD translation (shared `School` table +
`school_id` FK everywhere) — matches the supplied spec exactly, but fights
Frappe's grain and pushes tenant-isolation bugs into application code
instead of the platform.

Confirmed by owner 2026-07-03 — no further follow-up needed.

---

## 0005 — Evaluate reusing Frappe's Education app before building DocTypes from scratch

**Date:** 2026-07-03 (spike-first approach confirmed by owner 2026-07-03)
**Status:** Accepted — run the spike in Sprint 1, decide the actual
build path from its findings

**Decision:** Before writing any `edupro_sms` DocTypes, install and
inspect Frappe's official "Education" domain app (Academic Year, Academic
Term, Program, Course, Student, Guardian, Instructor, Program Enrollment,
Assessment, etc. — overlaps significantly with `docs/03_DocTypes.md`).
Spend a bounded spike (Sprint 1, before Sprint 2 DocType work starts)
evaluating three options: (a) build fresh in `edupro_sms` regardless, (b)
install the Education app and extend it, or (c) cherry-pick specific
Education DocTypes (e.g. `Guardian`, `Academic Year`) and build the
IGCSE-specific pieces (approval workflow, weighted grading, Class Teacher
review) fresh.

**Why:** Avoids duplicating work Frappe already did, without committing
blind — the Education app's data model may not map cleanly onto the
IGCSE-specific approval workflow without heavy customization of its own,
so the spike's job is to find out before Sprint 2 locks in the DocType
list.

**Resolved 2026-07-03 — see 0007.** Spike run, outcome: extend the
Education app rather than build fresh.

---

## 0007 — Extend Frappe's Education app rather than build DocTypes from scratch

**Date:** 2026-07-03
**Status:** Accepted (resolves 0005)

**Decision:** `edupro_sms` builds on top of the Education app's existing
DocTypes rather than modeling Class/Subject/Marks/etc. from scratch.
Mapping from `docs/03_DocTypes.md`'s original plan to what Education
already provides:

| Planned DocType | Education app equivalent | Reuse as-is? |
|---|---|---|
| Academic Year | `Academic Year` | Yes |
| Term | `Academic Term` | Yes |
| Grade Boundary | `Grading Scale` + `Grading Scale Interval` | Yes (interval uses a single `threshold` per row instead of explicit min/max — functionally equivalent) |
| Parent/Guardian | `Guardian` + `Student Guardian` | Yes (already supports multiple guardians per student) |
| Teacher | `Instructor` | Yes |
| Student | `Student` | Yes |
| Class | `Student Group` | Yes (a batch of students; `group_based_on` supports Batch/Course/Activity) |
| Subject | `Course` | Yes |
| Enrollment / Subject Allocation | `Program Enrollment` + `Program Enrollment Course` | Yes |
| Assessment | `Assessment Plan` + `Assessment Criteria` (child table, weighted) | Yes — Test 40% / Exam 60% modeled as two weighted criteria |
| Marks | `Assessment Result` + `Assessment Result Detail` | Yes |
| Report Card PDF | `Student Report Generation Tool` | Reuse its data-fetching helper (`get_formatted_result`); build our own print template on top |
| School Settings | *(nothing in Education)* | Build fresh — small Single DocType, still needed |

**Why:** The Education app already implements roughly 70% of the planned
MVP data model, tested and maintained upstream. Building it fresh would
duplicate solid functionality for no benefit — our actual differentiator
is the IGCSE-specific *process* (approval workflow, class/headmaster
comments, class position, our report card layout), not the underlying
data model.

**What still needs custom build in `edupro_sms`** (this replaces most of
the original Sprint 2+ plan in `TASKS.md` — see updated sprints there):

1. A Frappe Workflow on `Assessment Result`: Draft → Pending Approval →
   Reviewed (Class Teacher) → Approved/Rejected (Headmaster) → Published.
2. Custom Fields: Class Teacher comment, Headmaster comment, special-case
   marker (Absent/Exempt/Medical Withdrawal) — likely on `Assessment
   Result` or a thin wrapper doctype if aggregation across courses needs
   its own record (TBD during Sprint 2 design).
3. Class position/ranking calculation (custom report or scheduled job).
4. IGCSE-branded Report Card Print Format (`docs/05_Print_Formats.md`),
   reusing Education's result-fetching logic where possible.
5. Parent email delivery wired to the workflow's "Published" transition
   (background job, `docs/06_Email_System.md`).
6. Class Teacher role permission scoping (own class only).
7. `School Settings` Single DocType (per-site branding/config, per
   `DECISIONS.md` 0004).

**Rejected alternatives:** (a) build fresh — rejected, duplicates
maintained upstream functionality; (b) cherry-pick only the simplest
matches (Academic Year/Term, Grading Scale, Guardian) and build
Class/Assessment/Marks fresh — rejected, `Assessment Plan`/`Result`
already support weighted criteria which covers the Test/Exam split
without a bespoke doctype.

**Follow-up:** `docs/03_DocTypes.md` needs a rewrite to reflect this
mapping instead of the original from-scratch field tables. Do that before
starting Sprint 2 DocType/workflow work.

---

## 0006 — Local dev environment stood up: frappe_docker at project root, custom image, Frappe/ERPNext v15 + Education v15.2

**Date:** 2026-07-03
**Status:** Done

**Decision:** `frappe_docker` lives at the project root (`frappe_docker/`,
gitignored), not in a `docker/` subfolder as originally sketched in
`PROJECT_CONTEXT.md` — matches what was actually built and is simpler
(no path indirection). Built a custom image (`edupro-sms:v15`) via
`images/custom/Containerfile` rather than the more commonly documented
`images/layered/Containerfile`, because `custom` is the only variant that
both pins an exact `PYTHON_VERSION` build arg *and* supports the
`apps.json` secret for baking in extra apps — `layered` builds from a
pre-published `frappe/build:${FRAPPE_BRANCH}` image with a Python version
we can't control directly.

**Why:** Python 3.11 was an explicit requirement. Result: Frappe 15.113.4,
ERPNext 15.115.0, Education 15.5.3, Python 3.11.15, one site
(`edupro.localhost`) with developer mode on. Full command reference in
`docs/08_Deployment.md` §8.1.

**Gotchas hit and fixed (see `docs/08_Deployment.md` §8.1 for detail):**
Education app has no plain `version-15` branch (used `version-15.2`
instead); frappe_docker's shell scripts checked out with CRLF line
endings on Windows (`core.autocrlf=true`) broke their shebang and
crash-looped every service using the custom image until fixed with
`sed -i 's/\r$//'`.

**Follow-up still open:** this environment makes the 0005 spike
*possible* to run, but the actual evaluation (compare Education app's
data model against `docs/03_DocTypes.md`, decide build-fresh vs. extend
vs. cherry-pick) hasn't been done yet — 0005 stays open until that
happens.

**Important correction made after initial setup (two-part):** `bench
new-app edupro_sms` was first run directly inside the running `backend`
container. That writes into the container's writable layer, not any
persisted volume — compose.yaml only declares `sites` as a named volume,
`apps/` is baked into the image at build time. A `docker compose down`
would have silently deleted the newly created app.

*Part 1 — app source.* Fixed by: `docker cp`-ing `apps/edupro_sms` out to
the host (`apps/edupro_sms/`, which already has its own `.git` from
`bench new-app`'s default git init), then bind-mounting
`../apps/edupro_sms:/home/frappe/frappe-bench/apps/edupro_sms` on every
bench-role service. `edupro_sms` source now lives on the host and is
live-edited from there. The other three apps (frappe/erpnext/education)
are intentionally left baked into the image only — we never edit core
Frappe, so there's nothing to gain from host-mounting those.

*Part 2 — Python package registration (found and fixed after Part 1
alone still broke on a normal `docker compose down && up -d`).* The app's
`env/` (bench's Python virtualenv, where `uv pip install -e apps/edupro_sms`
registers the package) is *also* baked into the image, and — this is the
subtle part — **not shared between containers**: backend, queue-short,
queue-long, scheduler, and configurator each get their own independent
writable-layer copy of `env/` from the same image, even though they're
all the same image. Installing edupro_sms into one container's `env/`
(e.g. via `configurator`) does not make it visible to `backend`. Fixed by
adding a shared named volume `bench-env` mounted at
`/home/frappe/frappe-bench/env` on every bench-role service, plus having
`configurator` (which every other service `depends_on`) run
`uv pip install -e apps/edupro_sms` into that shared volume on every
startup, before anything else starts. Verified across two full
`down`/`up` cycles. See `frappe_docker/overrides.local/compose.edupro-sms-app.yaml`
and `docs/08_Deployment.md` §8.1 for the working config.

---

## 0008 — Report Card is a new DocType; approval workflow lives there, not on Assessment Result

**Date:** 2026-07-03
**Status:** Accepted (confirmed by owner)

**Decision:** Built a new `Report Card` DocType (one per Student +
Academic Term) rather than putting the approval workflow directly on
`Assessment Result` as `TASKS.md` originally sketched. `Report Card`
aggregates a student's already-submitted `Assessment Result`s (one row
per subject in a child table), and carries: `class_teacher_comment`,
`headmaster_comment`, `total_score`/`average_percentage`/`overall_grade`,
`position`/`number_of_students`, `pdf`, `sent_to_parent_at`.

**Why:** `class_teacher_comment`/`headmaster_comment` are per-student
(one comment about the whole report), not per-subject. Putting the
workflow on `Assessment Result` would mean either duplicating the same
comment across every subject record for a student, or approving a
student's report as N separate per-subject actions instead of one. A
Report Card also gives a natural home for the PDF attachment and
delivery tracking, which don't belong on any single subject's result.

**Design:**
- `Assessment Result` entry stays simple — teacher submits per subject
  (`docstatus` 0→1), no custom workflow there.
- `generate_report_cards(student_group, academic_term)` (whitelisted,
  in `report_card.py`) aggregates each active student's submitted
  results into a Report Card, skipping (and reporting) students missing
  any required course — never silently generating a partial report.
- Class position uses standard competition ranking (ties share a rank,
  next distinct rank skips accordingly), computed once per batch across
  the whole Student Group.
- Workflow "Report Card Approval": Pending Approval → Reviewed (Class
  Teacher) → Approved/Rejected (Headmaster) → Published, with `doc_status`
  mapped so **Approved and Published are actually submitted/locked**
  (docstatus=1) — not just a label change. Verified: editing a field on
  a Published record throws `UpdateAfterSubmitError`.

**Real Frappe gotchas hit while building this (useful if repeated):**

1. **Workflow State / Workflow Action Master are separate master lists.**
   You can't just write a state name like "Pending Approval" into a
   Workflow's states table — it must exist as its own `Workflow State`
   record first (same for `Workflow Action Master` and action names).
   `Approved`/`Rejected`/`Review` already existed as stock records;
   `Pending Approval`/`Reviewed`/`Published`/`Resubmit`/`Publish` had to
   be created. All exported as fixtures.
2. **`allow_on_submit` is required for the workflow_state field** to
   transition between two docstatus=1 states (Approved → Published) —
   without it, Frappe blocks the change with `UpdateAfterSubmitError`
   even though it's the workflow engine making the change, not a user
   editing a random field.
3. **`Assessment Plan.academic_term` is `fetch_from: student_group.academic_term`**
   — it was never set on the Sprint 3 Student Group records, so every
   Assessment Plan silently had `academic_term = null` despite the
   value being passed at creation time (fetch_from overwrites on every
   save, silently). Fixed by setting `academic_term` on the Student
   Groups and re-saving everything downstream. Academic Term's actual
   autoname is `"{academic_year} ({term_name})"` e.g. `"2026 (Term 1)"`
   — not the more obvious `"2026 Term 1"` guessed initially.
4. **PDF generation needs a container-reachable `host_name`.** Default
   `frappe.utils.get_url()` returned `http://edupro.localhost` (no
   port) — unreachable from inside the backend container, since that
   hostname/port only resolves via the host machine's port mapping.
   wkhtmltopdf failed with a network `ConnectionRefusedError` fetching
   the print CSS. Fixed with
   `bench set-config host_name "http://frontend:8080"` (the frontend
   container's internal Docker-network address).
5. **`frappe.get_single` is not available inside the Print Format Jinja
   sandbox** (security restriction) — use
   `frappe.db.get_single_value(doctype, fieldname)` instead.

All of the above are now baked into the actual working code/config —
this entry exists so they don't get silently rediscovered if the
environment is ever rebuilt from scratch.

---

## 0009 — Portals via custom `www/` pages; permission scoping via query conditions + has_permission; gunicorn worker restart gotcha

**Date:** 2026-07-03
**Status:** Accepted

**Decision:** Student/Parent portal access is a custom Frappe website
page (`edupro_sms/www/my-reports/`), not Frappe's generic
DocType-list-view portal machinery — gives full control over the
per-child grouping a Guardian needs, which the generic portal doesn't
support out of the box. Row-level access control is enforced via
`get_permission_query_conditions` + `has_permission` on `Report Card`
(`report_card.py`), covering all three non-admin roles:

- **Class Teacher** — only Student Groups where they're `class_teacher`.
- **Student** — only their own report, and only once `Published`.
- **Guardian** — only their linked children's reports (via `Student
  Guardian`), and only once `Published`.
- Any role without a matching Instructor/Student/Guardian record **fails
  closed** (`1=0`), not open.

**Why fail closed:** a portal user with a role but no linked
identity record is a data/setup bug, not a "grant broad access" signal —
better to show nothing than leak everything.

**Verified over real HTTP** (cookie-based login, not just unit-style
checks): correct data isolation on both the `/my-reports` list page and
the print view (`/printview?...` → 403 for cross-student access), with
explicit negative-case tests (a Student's page must not contain another
student's name), not just happy-path checks.

**Gotcha — gunicorn workers cache imported Python modules across
requests.** `bench clear-cache` clears Frappe's *application-level*
caches (docfield metadata, etc.) — it does **not** restart the actual
gunicorn worker processes, which keep already-imported Python modules in
memory. A change to `report_card.py` (adding the permission functions)
was invisible over HTTP — one worker was still running the pre-change
code — even though `bench console` (a fresh process) showed the fix
working correctly. First symptom: a Student's portal page briefly showed
another student's data despite `has_permission` checks being correct in
isolation. **Fix: restart the actual containers
(`docker compose restart backend queue-short queue-long scheduler
websocket`) after any Python controller/hook code change**, not just
`bench clear-cache` — this is now the standard step, not a one-off.

**Email delivery verified functionally, SMTP itself still TBD.** Created
a placeholder `Email Account` (fake SMTP host) purely to get past
Frappe's "no outgoing account configured" guard, confirmed the full
pipeline builds correct `Email Queue` records (right recipient, subject,
body content matching the actual student's data, PDF attached), then
**removed the placeholder** so the site doesn't carry fake config. Real
SMTP setup is still a deployment-time task (`docs/06_Email_System.md`).

---

## 0010 — Sprint 8: automated tests, dashboard, performance check, MVP readiness

**Date:** 2026-07-03
**Status:** Done

**Decision/summary:** Closed out the MVP build. Added
`test_report_card.py` (`FrappeTestCase`, all 12 required scenarios from
`docs/07_Testing.md`, 12/12 pass), a "Report Card Status by Class"
Script Report for the Headmaster (`docs/03`/`TASKS.md` Sprint 8), a
performance spot-check at 20-student scale (well within targets —
`docs/08_Deployment.md` §8.3), and a real UAT checklist
(`docs/07_Testing.md` §7.4) for a human to click through before
go-live. Full MVP readiness status recorded in `docs/08_Deployment.md`
§8.5 — functionally complete on sample data; real pilot-school
deployment needs real data entry, real SMTP, and a browser-based UAT
pass, none of which are architectural gaps.

**Two more real gotchas found (same "looks fine, isn't" pattern as
0006/0009):**

1. **`FrappeTestCase`'s rollback isn't fully isolated between test
   *methods* within one run** — only the outer `bench run-tests`
   transaction fully cleans up. A test asserting on data scoped to an
   entire `student_group` + `academic_term` (e.g. class position
   ranking, which is computed across *every* Report Card sharing that
   pair) will see other tests' students unless given its own isolated
   Student Group. Symptom: TC-11 expected rank 3, got rank 7 — caused by
   4 other tests' students still being visible in the shared group.
2. **`frappe.db.rollback()` does not reliably undo a script's changes
   once any document has been `.submit()`ted.** A standalone performance
   check script called `frappe.db.rollback()` at the end expecting a
   clean slate; 20 synthetic students, an Academic Year, and related
   records were still in the database afterward — submission appears to
   force an internal commit partway through the run. Had to write an
   explicit cleanup script instead, and verified with count queries
   rather than trusting the rollback. **Lesson: never trust
   `frappe.db.rollback()` alone in a submit-heavy one-off script — verify
   afterward, or clean up explicitly.**

Also required `bench set-config allow_tests true` once on the site before
`bench run-tests` would run at all (disabled by default even with
developer_mode on).

---

## 0011 — ERPNext Setup Wizard: skip it (three attempts to actually kill it)

**Date:** 2026-07-03
**Status:** Fixed (defense-in-depth: real root cause fixed + a
belt-and-suspenders `boot_session` override)

**Decision:** Confirmed (again) that Edupro SMS doesn't use ERPNext's
Company/fiscal-year setup wizard — `docs/02_Database.md` §2.2 already
established this (0004). This entry records the incident and — honestly
— three attempts before it was actually fixed. Kept as a cautionary
example of premature "fixed" claims, not cleaned up to look tidier in
hindsight.

**What happened:** Logging in as Administrator triggered ERPNext's setup
wizard (`/setup-wizard/0`). Submitting it crashed with `AttributeError:
'NoneType' object has no attribute 'replace'` in
`erpnext/setup/setup_wizard/operations/install_fixtures.py` — the
wizard's "Country" field wasn't reaching the backend. Since Edupro SMS
doesn't need this wizard at all, the right fix is to mark setup as
complete some other way, not debug ERPNext's form.

**Attempt 1 (wrong): `System Settings.setup_complete = 1`.** Value
persisted, `/app` returned HTTP 200 with no redirect header — reported
fixed. Wrong: `frappe.is_setup_complete()` (what the client actually
checks) doesn't read `System Settings` at all.

**Attempt 2 (necessary but not sufficient): fix the real per-app flag.**
`frappe.is_setup_complete()` reads the `Installed Application` table and
requires both `frappe` and `erpnext` rows to have `is_setup_complete = 1`.
`erpnext`'s was `0`. Fixed it directly, then discovered that value gets
**recomputed** by `InstalledApplications.update_versions()` based on
`has_company()` (does any `Company` record exist) — with zero Company
records, any recomputation would flip it back to `0`. Created a minimal
Company record so the recomputation would permanently agree. Verified
`/app/school-settings` loaded correctly (confirmed by the owner
in-browser this time, learning from attempt 1) — **navigation** worked.
Reported fixed. Still wrong: **saving** School Settings triggered a
rapid redirect loop that attempts 1 and 2 didn't touch at all.

**Attempt 3 (the actual root cause): a stray `desktop:home_page` default
value.** Found by having the owner export a HAR file from DevTools and
grepping the *raw boot JSON payload* (not the JS source bundle, which
happened to contain misleading matches on the same field names) for
`sysdefaults`. It contained `"desktop:home_page": "setup-wizard"` — a
Frappe `DefaultValue` record, completely independent of
`is_setup_complete`/`Installed Application`/`System Settings`, that had
been left pointing at the wizard (very likely set automatically by
Frappe while setup was genuinely incomplete, and never updated since the
real wizard was never completed). `boot.py`'s `add_home_page()` reads
this value into `bootinfo.home_page` on every session; client-side
post-action navigation (confirmed: specifically after Save) sent the
browser to `frappe.boot.home_page`, landing on the wizard page, which
then redirected itself away since setup was in fact complete — producing
the observed flash/loop. Fixed with
`frappe.db.set_default("desktop:home_page", "Workspaces")`. Verified in
the raw boot JSON (`"home_page": "Workspaces"`) and confirmed by the
owner saving School Settings successfully in-browser.

**Also added:** `edupro_sms/edupro_sms/boot.py` with a `boot_session`
hook that unconditionally forces `sysdefaults.setup_complete = 1` and
populates `setup_wizard_completed_apps` with all installed apps, on
every session. Not the fix for this specific bug, but cheap
defense-in-depth against the wizard resurfacing via some other stale
default we haven't found yet.

**Lessons (worth internalizing, not just noting):**
1. Curl-based "200 and no redirect header" verification missed both
   wrong attempts because the redirect logic is **client-side JS**
   reacting to boot data — a passing HTTP status proves the page
   *loaded*, not that the client won't *navigate away* a moment later.
2. Even an in-browser confirmation (attempt 2) can be incomplete if it
   only tests navigation, not the actual reported action (Save). Match
   the verification to the *exact* reported repro steps, not an adjacent
   one that seems equivalent.
3. When grepping rendered HTML for a JSON value, **watch out for the
   same field name appearing in embedded JS source** (e.g. this page
   bundles `setup_wizard.js`, which references
   `frappe.boot.setup_wizard_completed_apps` in code) — that will match
   your grep and look like data. Find the actual data blob (here:
   `"sysdefaults": { ... }`) before trusting a match.
4. A HAR export / real browser diagnostic was more useful than continued
   server-side guessing after two wrong theories — worth asking for
   sooner, not as a last resort.

## 0012 — Login page branding via Website Settings, not a core template override

**Decision:** Brand `/login` (school name, logo, motto) by driving
Frappe's existing `Website Settings.app_name`/`app_logo`/`copyright`
fields — which `frappe/www/login.py` already reads directly — rather
than shadowing `frappe/www/login.html` with an app-level override.

**Why:** `login.py`'s `get_context()` builds `app_name` from
`frappe.get_website_settings("app_name")` and the logo via
`get_app_logo()` (`Website Settings.app_logo`, falling back to Navbar
Settings), and the footer (shown on login when
`show_footer_on_login=1`) renders `Website Settings.copyright`. All
three pieces of "simple branding" the owner asked for (logo + name +
motto) are already wired into stock fields — no need to reimplement
OAuth/social-login/LDAP/email-link flows by shadowing the whole
template, which the `/my-reports` vs `edu-portal` precedent
(`DECISIONS.md` 0009) would otherwise have suggested as the pattern.

**Implementation:** `edupro_sms/edupro_sms/branding.py`, wired as an
`on_update` doc event on `School Settings` (`hooks.py`), so branding
stays in sync automatically on every save rather than being a one-off
console fix — matters because of 0004 (one site per school): each
school's site should brand itself from its own `School Settings`
without any manual step. Also flips the school logo `File` to public on
sync, since a private file 404s for the `Guest` user viewing `/login`
(caught by testing the actual unauthenticated request, not just the DB
field value).

## 0013 — Headmaster/Instructor land on a website dashboard, not Desk, without losing Desk access

**Decision:** Headmaster and Instructor now default to a new
`/dashboard` website page (`www/dashboard/`) after login. They stay
`user_type = System User` (unlike Student/Guardian, which are Website
Users) and keep full, unrestricted Desk access — the owner explicitly
chose this scope (dashboard-only) over a fully website-only experience,
because marks entry and report-card approval are still Desk-form-based
and reimplementing both on the website was out of scope for this ask.

**Why this couldn't just reuse the `role_home_page` hook** (the
mechanism already used for Student/Guardian → `/my-reports`, 0009):
`frappe/www/login.py`'s `set_user_info()` only calls
`get_home_page()` (which consults `role_home_page`) for
`user_type == "Website User"`. For every other user type it sets
`home_page` from the user's `default_app` route (via
`frappe.apps.get_default_path()`), falling back to `/app`. Since
Headmaster/Instructor deliberately stay System Users, `role_home_page`
is simply never consulted for them — confirmed by reading
`frappe/auth.py`'s `set_user_info()` and `frappe/apps.py`'s
`get_default_path()`/`get_route()` before building anything, not by
trial and error.

**Implementation:**
1. `hooks.py` `add_to_apps_screen` registers `edupro_sms` with
   `route: "/dashboard"` and a `has_permission` gate
   (`edupro_sms/edupro_sms/dashboard.py::has_dashboard_access`,
   true for Headmaster/Instructor).
2. A `User.validate` doc event
   (`dashboard.py::sync_dashboard_default_app`) sets
   `default_app = "edupro_sms"` whenever a user has either role, so
   `get_default_path()` resolves to `/dashboard` for them without a
   manual per-account step — future Headmaster/Instructor accounts get
   this automatically, same spirit as 0012's branding sync.
3. `/dashboard`'s `get_context()` branches by role: Headmaster gets a
   school-wide summary; Instructor gets their assigned classes by
   **importing and reusing** the My Classes Script Report's `_rows()`
   function (`edupro_sms/edupro_sms/report/my_classes/my_classes.py`)
   instead of duplicating the query — it already scopes correctly to
   the logged-in Instructor via `teacher_permissions.py`, regardless of
   whether it's called from a Desk report or a website page.

**Side effect caught before shipping:** adding a non-`/app/*` route to
`add_to_apps_screen` breaks `frappe.apps.get_route()`'s
`is_desk_apps()` shortcut for every *other* System User without a
personal `default_app` (Administrator, future System Managers) —
Frappe can no longer assume "all registered apps are Desk apps," so it
sends them to the `/apps` picker screen instead of straight into Desk.
Caught by testing Administrator's login response before considering
this done, not just Headmaster/Instructor's. Fixed by setting
`System Settings.default_app = "erpnext"` (matching erpnext's own
`add_to_apps_screen` route of `/app/home`, the same page Administrator
landed on before this change) — restores the old fallback for anyone
without a personal override, while Headmaster/Instructor's personal
`default_app` still takes priority for them.

## 0014 — Removed Desk access for Teacher/Headmaster, after building website replacements, not before

**Decision:** Reverses part of 0013. An independent QA pass
(`exports/Edupro_SMS_QA_Report_2026-07-03.pdf`) tested against a
stricter brief than 0013 assumed — Teacher must enter marks and
Headmaster must approve report cards *entirely on the website*, and
neither should be able to reach Desk at all. 0013's "keep Desk access"
call directly failed that brief. Resolved by building the two website
equivalents Desk was standing in for, then removing Desk access once
both were verified working, not as a single step.

**Why sequenced this way (build first, remove access last):** Desk
access was these two roles' only way to do real work up to this point.
Removing it before the replacement existed would have left them with
no working tool — a strictly worse outcome than the thing being fixed.
Each piece was verified independently before the next: marks entry
end-to-end (create, edit an already-submitted mark via the cancel/
amend Frappe requires, cross-class permission denial) before touching
approvals; approve/reject/publish end-to-end (including confirming a
Published report actually reaches the parent's `/my-reports`) before
touching Desk access; and only then was `user_type` flipped.

**Implementation:**
1. `edupro_sms/edupro_sms/marks_entry.py` + `www/marks-entry/` — a
   teacher-facing form per Assessment Plan. Deliberately does *not*
   reimplement Assessment Result's validation (max score, grade calc,
   duplicate check) — it builds a normal document and lets
   `Document.validate()` do that, same as the Desk form always did.
   Editing an already-submitted result needed a real cancel+amend+
   resubmit, since `Assessment Result` is `is_submittable=1` with no
   `allow_on_submit` fields (checked the doctype JSON before assuming
   a plain field update would work — it wouldn't have). Skips
   re-amending rows whose scores are unchanged from what's already
   stored, to avoid pointless cancel/amend churn on every save.
2. `edupro_sms/edupro_sms/approvals.py` + a Pending Approvals section
   on `/dashboard` — calls `frappe.model.workflow.apply_workflow(doc,
   action)`, the same function Desk's own workflow buttons call,
   against the existing `Report Card Approval` workflow
   (`fixtures/workflow.json`). No new state machine.
3. `edupro_sms/edupro_sms/dashboard.py`'s `sync_dashboard_default_app`
   User validate hook (from 0013) now also sets
   `user_type = "Website User"` for Headmaster/Instructor, so future
   accounts get the no-Desk-access treatment automatically, same as
   the `default_app` sync already did.

**Side effect checked for and not found this time:** re-verified
`is_system_user()` and `frappe.apps.get_default_path()` behave
identically for a `Website User` with `default_app` already set as
they did for a `System User` (both resolve to `/dashboard` via the
same `elif user_default_app:` branch) — the flip didn't require
touching the `add_to_apps_screen`/`default_app` mechanism from 0013 at
all, it "just worked" once `user_type` changed. Confirmed Administrator
and both flipped accounts (Headmaster, Teacher) all still land in the
right place after a full restart, not just before it.

## 0015 — Report card QR code links to a public minimal-info verify page, not the full printview

**Decision:** The anti-forgery QR code added to the IGCSE Report Card
print format encodes a link to a new public (no-login) `/verify-
report-card?code=...` page that shows only student name, class, term,
overall grade, and average percentage — not the full subject-by-
subject mark breakdown, and not a link straight into the existing
`/printview` (which requires login and, if that login wall were ever
loosened, would expose everything). The `code` is a random
`secrets.token_hex(8)` stored in a new `Report Card.verification_code`
field, set once at first Publish — deliberately not the document's own
`RC-{student}-{term}` name, which is guessable/enumerable.

**Why:** The point of a scan-to-verify feature is letting a third party
(an employer, another school, a skeptical relative) confirm a printed
report card is genuine without needing a portal account, while not
turning the QR code into a way to pull a student's full academic record
off a piece of paper that could be lost, photocopied, or photographed
by anyone. A minimal public confirmation page is the standard pattern
for this class of feature (diploma/certificate verification services
work the same way) and was chosen over the two alternatives considered:
linking straight to the printview (fails the point above) or a bare
code with no page at all (asks too much of whoever is checking).

**How to apply:** If any other document ever needs a similar QR/
verification feature, follow the same shape — random unguessable
token on the document, a public page keyed by that token, and a
deliberately narrow set of fields on that page. Don't reuse the
document's own name as the token.

## 0016 — Teacher dashboard mockup: kept the current submit-on-save model, CSV-only for bulk marks entry

**Decision:** The owner supplied a detailed mockup for a richer teacher
dashboard/marks-entry experience that implied two things beyond what
exists today: (1) marks going through their own Draft → "Submit for
Approval" → "Request Revisions" cycle, separate from the Report Card
approval Headmaster already does, and (2) a set of "Bulk Operations"
including attendance-style Mark All Present/Absent and grade-curve/±N
adjustment tools. A clarifying question was asked about both; the
owner didn't respond. Given the size of the ask and the genuine
architectural fork on point (1), the lower-risk, recommended option
from that question was taken for both rather than guessing at the
more invasive one: marks still submit directly when a teacher clicks
Save (no new approver, no new workflow states) — "Submit for Approval"
in the mockup maps onto the existing Save action, which already feeds
the real approval gate at the Report Card level (Class Teacher review
→ Headmaster approve → publish). Bulk operations were limited to CSV
export/import; attendance-style present/absent marking was dropped
entirely (wrong concept for a marks-only system, no attendance data
model exists), and grade-curve/±N tools were left out since "curve"
has no agreed-on computation.

**Why:** Introducing a second approval gate before the Report Card
level would be a materially bigger, riskier change than the rest of
the mockup — it needs new workflow states, a new reviewer screen, and
rules for who can request revisions, none of which were specified.
Building it on a guess risks locking in the wrong shape for a real
school process. The visual/UX parts of the mockup (summary bar, class
cards, live grade calculation, grade boundaries table, CSV round-trip,
grade distribution chart) were all buildable from data that already
exists and carried no such risk, so those went ahead without waiting
for a response.

**How to apply:** If the owner later confirms they do want a genuine
subject-level approval gate, treat it as new scope, not a bug fix —
it changes who can edit a mark after entry and needs its own workflow
states (mirroring `Report Card`'s Pending Approval/Reviewed/Approved/
Published pattern is the natural starting point, but distinct roles
need deciding: does the Class Teacher approve each subject teacher's
marks, or does this stay Headmaster-only?).

## 0017 — Parent/student dashboard mockup: built the redesign, skipped the subsystems it implied

**Decision:** Same pattern as 0016, one week apart. The owner's parent/
student dashboard mockup was mostly a genuine "make it slick and
space-saving" visual redesign — that part was built in full (compact
stat chips, child cards, per-child academic summary, subject
performance table, progress panel, resend-email action). But the
mockup also implied several subsystems that don't exist and weren't
separately requested: self-service "Add Child" (security-sensitive —
letting a parent link themselves to any student needs an approval
step, not a free-form add), a parent-teacher messaging inbox, meeting/
slot booking, a generic notifications & alerts feed (the mockup's
sample items — "Parent-Teacher Meeting Saturday", "Academic Calendar
Update" — have no backing data model at all), and granular email
preference toggles. None of these were built.

**Why:** Same reasoning as 0016 — a "redesign the dashboard" request
doesn't license inventing new subsystems with security implications
(self-service child linking) or no real data to drive them
(notifications feed, messaging). Where a small real feature already
had a ready-made hook, it was built: `Report Card.viewed_by_parent_at`
existed as a field but nothing ever set it, so the "New Reports" badge
was wired up properly instead of faking a notification count.

**How to apply:** If the owner asks for any of the skipped pieces
specifically, treat each as its own scoped feature, not a dashboard
tweak:
- Add Child needs an approval workflow (Guardian requests a link,
  Headmaster/admin confirms it's correct) — never silent/instant.
- Messaging needs a new DocType (thread + message rows) and its own
  permission model, not a stretch of Report Card comments.
- Notifications needs a real event source per item shown, not
  placeholder text — don't build the feed until there's something
  real to put in it beyond "New Reports" (which already exists now).

## 0018 — Headmaster dashboard mockup: bulk-approve reuses the existing workflow, no new subsystems

**Decision:** Third round of the same mockup pattern (0016 teacher
dashboard, 0017 parent dashboard). The owner's headmaster mockup
implied: a per-class "Approve All" (real, and cheap — see below), a
separate freeform "Headmaster Comments" running log, an elaborate
Report Generation builder with Attendance/Behavior toggles, a mass
"Send Broadcast" email composer, and a "Notify Teachers" action. Built
the genuinely real parts (Class Performance Overview, a `/class-review`
drill-down, per-class Pending Approvals rollup, real Subject
Performance Analysis, real Recent Activity), skipped the rest.

**Why "Approve All" was safe to build, unlike the subject-level
approval gate skipped in 0016:** this one isn't a new workflow at
all — `apply_class_report_card_action` (`approvals.py`) just loops the
*same* `apply_workflow` call the individual Approve/Reject/Publish
buttons already make, filtered to whichever Report Cards in a class
are currently in the right state. No new states, no new roles, no new
data model. That's the dividing line worth remembering: bulk-applying
an *existing* action to many documents is safe to build on request;
inventing a *new* approval gate is not.

**Why the rest was skipped:** a "Headmaster Comments" log would
duplicate the per-Report-Card `class_teacher_comment`/
`headmaster_comment` fields that already exist with no clear separate
purpose. Attendance/Behavior toggles have literally no data model —
attendance is `edupro_attendance`, a whole future app per
`CLAUDE.md`'s own roadmap, not in scope for a dashboard redesign. Mass
broadcast email and "Notify Teachers" are new communication
subsystems with real misuse/rate-limit risk, same reasoning as
skipping parent-teacher messaging in 0017.

**Real gap found while building Recent Activity:** `Report Card` has
no change tracking enabled — `tabVersion` has zero rows for it despite
61 real workflow transitions this session. There is no way to
reconstruct exact "who approved what when" history from current data.
Recent Activity instead shows each card's real `modified` timestamp +
current `workflow_state` ("X's report is now Published"), which is
honest about what actually happened (last touched, now in this state)
without claiming a precise event log that doesn't exist.

**How to apply:** If precise approval-history auditing is ever
actually requested (not implied by a mockup), the real fix is enabling
`track_changes` on `Report Card` (or a dedicated audit log doctype),
not trying to reverse-engineer it from `modified` timestamps.
