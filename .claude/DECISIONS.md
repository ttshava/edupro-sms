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

**Status quo until the spike concludes:** `TASKS.md` and
`docs/03_DocTypes.md` still assume option (a) — fresh DocTypes in
`edupro_sms` — as the fallback. Record the spike's outcome here as a new
entry (0006) once it's run.
