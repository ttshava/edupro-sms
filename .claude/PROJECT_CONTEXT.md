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
- **Infra:** Dockerized Frappe on Windows for local dev — `frappe_docker/`
  at the project root (gitignored vendor clone), MariaDB + Redis via
  frappe_docker's standard overrides. Running since 2026-07-03, see
  `docs/08_Deployment.md` §8.1.

Full detail: `docs/02_Database.md`, `docs/03_DocTypes.md`.

## Current Sprint

**Sprint 8 — Dashboards, Testing & MVP Release: done. All 9 planned
sprints (0–8) are complete — MVP feature-complete on sample data.**

Sprint 8 added: automated tests covering all 12 required scenarios from
`docs/07_Testing.md` (12/12 pass), a Headmaster dashboard ("Report Card
Status by Class"), a performance spot-check (well within targets at
20-student scale), and a real UAT checklist for a human browser pass.
Full readiness breakdown in `docs/08_Deployment.md` §8.5 — what's left
before a real pilot-school launch is deployment/data/config work (real
School Settings, real classes/people, real SMTP, a browser UAT pass), not
further feature development. See `.claude/TASKS.md` Backlog for the small
list of non-blocking polish items and genuinely post-MVP features
(`edupro_finance`, `edupro_attendance`, `edupro_transport`, etc.).

Environment: `frappe_docker/` at project root, custom image
`edupro-sms:v15`, Frappe 15.113.4 + ERPNext 15.115.0 + Education 15.5.3,
Python 3.11.15, site `edupro.localhost` at http://localhost:8080
(`DECISIONS.md` 0006, `docs/08` §8.1). Data model direction: extend the
Education app rather than build fresh (`DECISIONS.md` 0007,
`docs/03_DocTypes.md`).

See [`TASKS.md`](TASKS.md) for the full sprint breakdown.
