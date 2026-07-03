# Project Context — Edupro SMS

> Detailed module specs live in `docs/`. This file summarizes vision, scope,
> and sprint status only — see `docs/` for the authoritative detail behind
> every line here.

## Vision

Edupro is an IGCSE-curriculum academic-reporting platform for junior and
high school students. Core philosophy: **"Build a School ERP Platform, not
just a report card generator."** It starts as a single-school tool run by
the owner (who has Moodle experience) and is designed from day one to
become a **multi-tenant SaaS product** serving 1 to 1,000+ schools, without
a rewrite.

The system must be scalable, secure (role-based, granular permissions),
usable (teachers productive in under 15 minutes), and reliable (zero data
loss, full audit trail).

## Target Schools

- IGCSE-curriculum junior and high schools.
- Initial rollout: a single pilot school, self-hosted, to validate the
  workflow end-to-end before onboarding additional schools.

## MVP Scope — What's In

| Feature Area | Specific Features |
|---|---|
| User Management | Admin, Teacher, Class Teacher, Headmaster, Student, Parent roles |
| School Setup | Classes, Subjects, Terms, Grading Scales, Academic Years |
| Marks Entry | Test + Exam scores per subject, subject comments |
| Approval Workflow | Teacher submits → Class Teacher reviews → Headmaster approves/rejects |
| Report Generation | IGCSE-compliant grade calculation, PDF generation |
| Portal Access | Student views own results; Parent views all linked children |
| Email Delivery | Automated PDF report delivery to parents |
| Print Function | Direct printing of report cards |

Full detail: `docs/01_Project_Overview.md`, `docs/03_DocTypes.md`,
`docs/04_Workflows.md`.

## MVP Scope — What's Out (Future Phases)

Native mobile apps, SMS integration, parent-teacher chat, finance/fees
module, AI-powered recommendations, attendance system, timetable
generation, online exams. Also out of `edupro_sms` specifically (future
separate apps): `edupro_finance`, `edupro_attendance`, `edupro_transport`.

## Roles

Admin, Teacher, Class Teacher, Headmaster, Student, Parent — full
capability matrix in `docs/11_Roles_And_Permissions.md`.

## Architecture

- **Custom app:** `edupro_sms` — holds all Edupro DocTypes, workflows, print
  formats, reports, and automation.
- **No core modifications.** All customization lives in `edupro_sms` (plus
  fixtures for Roles/Custom Fields/Workflows/Print Formats).
- **Multi-tenancy:** one Frappe **site per school** (recommended default —
  see `.claude/DECISIONS.md` 0004). School-level settings (name, logo,
  motto, curriculum, timezone) live in a per-site Single DocType, not a
  shared `School` table with a `school_id` foreign key on every record.
  This is a deviation from the literal ERD supplied in the source spec —
  flagged for confirmation, not yet locked in.
- **Open question (Sprint 1):** evaluate whether to extend Frappe's
  official Education app (which already ships Academic Year, Academic
  Term, Instructor, Guardian, Student, Assessment, etc.) instead of
  building every DocType from scratch in `edupro_sms`. See
  `.claude/DECISIONS.md` 0005.
- **Modularity for the future:** additional domains (finance, attendance,
  transport) become their own apps installed alongside `edupro_sms`.
- **Infra:** Dockerized Frappe bench on Windows for local dev, MariaDB +
  Redis via the standard Frappe Docker setup.

Full detail: `docs/02_Database.md`, `docs/03_DocTypes.md`.

## Current Sprint

**Sprint 0 — Documentation & environment scaffolding** (in progress)

- [x] Create `.claude/` project docs
- [x] Ingest full functional spec into `docs/01`–`11`
- [x] Decide multi-tenancy model (0004: site-per-school, accepted) and
      Education-app approach (0005: spike first in Sprint 1, accepted)
- [ ] Install Docker Desktop, VS Code, Git, Claude Desktop
- [ ] Stand up `docker/` Frappe environment
- [ ] Create `edupro_sms` custom app, configure site, configure Git
- [ ] Run the Education-app spike (0005) before starting Sprint 2

See [`TASKS.md`](TASKS.md) for the full sprint breakdown.
