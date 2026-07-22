# 01 — Project Overview

> Technical source of truth for the system as a whole. Module-level detail
> lives in the other numbered `docs/` files — see the index in the root
> [`README.md`](../README.md).

## 1.1 Project Identity

- **Project Name:** Edupro School Management System — Academic Reporting
- **Deployed For:** First Class High School (live tenant —
  `School Settings.school_name`), production URL
  `firstclasshighschool.edupro.co.zw`
- **Curriculum:** IGCSE (International General Certificate of Secondary
  Education) — configurable per school/site; IGCSE is the default.
- **Primary Purpose:** Automate the complete academic reporting cycle
  from marks entry to parent delivery, plus termly fee billing.

## 1.2 Core Philosophy

> "Build a School ERP Platform, not just a report card generator."

The system must be:

- **Scalable** — one Frappe site per school (`docs/02_Database.md`), so
  onboarding a new school is "provision a site," not "add rows to a
  shared table."
- **Secure** — role-based access with granular, row-level permissions
  where it matters (`docs/11_Roles_And_Permissions.md`).
- **User-friendly** — teachers should learn marks entry in under 15
  minutes.
- **Reliable** — zero data loss, audit trails for every approval action.

## 1.3 Scope — What's In

| Feature Area | Specific Features |
|---|---|
| User Management | Admin, Teacher, Class Teacher, Headmaster, Bursar, Student, Guardian roles |
| School Setup | Classes, Subjects, Terms, Grading Scales, Academic Years, Curricula (grading bands) |
| Marks Entry | Term Mark + Exam Mark per subject, subject comments, special-case handling (Absent/Exempt/Medical Withdrawal) |
| Approval Workflow | Teacher submits → Class Teacher reviews → Headmaster approves/rejects → Publish |
| Report Generation | IGCSE grade calculation, class-position ranking, PDF generation with authenticity QR code |
| Portal Access | Student views own results; Guardian views all linked children; both view fee statements |
| Email Delivery | Automated PDF report cards to parents on Publish |
| Billing & Fees | Termly flat-rate fees by boarding type, payment tracking, running ledger statement |

## 1.4 Scope — What's Out (Future Phases)

- Native mobile apps (iOS/Android)
- SMS integration
- Parent–teacher chat
- Advanced GL/accounting (a future `edupro_finance` app — basic termly
  billing is already live, see `docs/12_Finance_Billing.md`)
- Attendance system (future `edupro_attendance` app)
- Timetable generation
- Online exams (live quiz-taking UX)
- Moodle/LMS integration — code exists in the local dev tree
  (`setup_moodle_integration.py`, `automate_moodle_sync_test.py`) but is
  **not part of the production app**; see `docs/08_Deployment.md`.

## 1.5 Success Metrics

| Metric | Target |
|---|---|
| Adoption rate | > 80% of teachers using the system |
| Time to enter marks | < 1 hour for 30 students |
| Report accuracy | 100% grade/position calculations correct |
| System uptime | > 99.5% |
| PDF generation speed | < 5 seconds per student |
| Support tickets | < 10 per month |

## 1.6 Ongoing Support & Maintenance

| Aspect | Approach |
|---|---|
| Bug fixes | Priority-based, resolved within 48 hours |
| Data integrity | Automated Frappe Cloud backups; periodic manual verification |
| Security updates | Keep Frappe/ERPNext/Education on a supported version line |
| Performance monitoring | Frappe Cloud's built-in site monitoring |
| User training | Documentation + role-based walkthroughs (`docs/10_User_Guide.md`) |
| Feature requests | Collected in `.claude/TASKS.md` |

## 1.7 Status

**Live in production** on Frappe Cloud, serving real data for First
Class High School: 492 students (Form 1 through Upper 6), 40 teaching
staff, 13 classes, 28 subjects, and live termly fee billing.

The production site was migrated from a locally-hosted Frappe v15
instance to Frappe Cloud (Frappe v16) — see `docs/08_Deployment.md` for
the full deployment story, including the app restructuring this required.
