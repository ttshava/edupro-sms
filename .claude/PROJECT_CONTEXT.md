# Project Context — Edupro SMS

> Detailed module specs live in `docs/`. This file summarizes vision,
> scope, and current status only — see `docs/` for the authoritative
> detail behind every line here.

## Vision

Edupro is an IGCSE-curriculum academic-reporting platform for junior and
high school students. Core philosophy: **"Build a School ERP Platform,
not just a report card generator."** It started as a single-school tool
and is designed to become a **multi-tenant SaaS product** serving 1 to
1,000+ schools, without a rewrite.

The system must be scalable, secure (role-based, granular permissions),
usable (teachers productive in under 15 minutes), and reliable (zero
data loss, full audit trail).

## Deployed School

**First Class High School** — live production tenant, real data: 492
students, 40 teaching staff, 28 subjects, 13 classes. See
`docs/01_Project_Overview.md` §1.7.

## Scope — What's In

| Feature Area | Specific Features |
|---|---|
| User Management | Admin, Teacher, Class Teacher, Headmaster, Bursar, Student, Guardian roles |
| School Setup | Classes, Subjects, Terms, Grading Scales, Academic Years |
| Marks Entry | Term Mark + Exam Mark per subject, subject comments, special-case handling |
| Approval Workflow | Teacher submits → Class Teacher reviews → Headmaster approves/rejects → Publish |
| Report Generation | IGCSE grade calculation, class-position ranking, PDF with authenticity QR |
| Portal Access | Student views own results; Guardian views all linked children; both view fees |
| Email Delivery | Automated PDF report delivery to parents on Publish |
| Billing & Fees | Termly flat-rate fees, payment tracking, running ledger statement |

Full detail: `docs/01_Project_Overview.md`, `docs/03_DocTypes.md`,
`docs/04_Workflows.md`, `docs/12_Finance_Billing.md`.

## Scope — What's Out (Future Phases)

Native mobile apps, SMS integration, parent-teacher chat, attendance
system, timetable generation, online exams, advanced GL/accounting
(future `edupro_finance` app). Moodle/LMS integration exists as
unfinished local-dev code but is not part of the production app —
see `docs/08_Deployment.md` §8.2.

## Roles

Admin, Teacher, Class Teacher, Headmaster, Bursar, Student, Guardian —
full capability matrix in `docs/11_Roles_And_Permissions.md`.

## Architecture

- **Custom app:** `edupro_sms` — holds all Edupro DocTypes, workflows,
  print formats, reports, and automation. See the root
  [`README.md`](../README.md) for the file structure.
- **No core modifications.** All customization lives in `edupro_sms`
  (plus fixtures for Roles/Custom Fields/Workflows/Print Formats).
- **Multi-tenancy:** one Frappe **site per school**. School-level
  settings (name, logo, motto, curriculum, timezone) live in a per-site
  `School Settings` Single DocType, not a shared table with a
  `school_id` foreign key.
- **Data model:** extends Frappe's Education app (Academic Year,
  Academic Term, Instructor, Guardian, Student, Assessment Plan/Result,
  Grading Scale, etc.) rather than modeling from scratch —
  `docs/03_DocTypes.md`.
- **Modularity for the future:** additional domains (finance,
  attendance, transport) become their own apps installed alongside
  `edupro_sms`.
- **Infrastructure:** two environments — local Docker dev (Frappe v15)
  and Frappe Cloud production (Frappe v16). See
  `docs/08_Deployment.md`.

## Current Status

**MVP feature-complete and live in production.** All core workflows
(marks entry, approval, report generation, email, portals, billing) are
built, tested, and running against real school data on Frappe Cloud.

See [`TASKS.md`](TASKS.md) for the current backlog and
[`DECISIONS.md`](DECISIONS.md) for the historical architecture decision
log.
