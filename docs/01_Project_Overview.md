# 01 — Project Overview

> Technical source of truth for the system as a whole. Module-level detail
> lives in the other numbered `docs/` files — see the index in
> `.claude/CLAUDE.md`.

## 1.1 Project Identity

- **Project Name:** EduPro School Management System – Academic Reporting
- **Version:** 1.0 (MVP)
- **Curriculum:** IGCSE (International General Certificate of Secondary
  Education) — configurable per school/site, IGCSE is the default and only
  curriculum required for MVP.
- **Primary Purpose:** Automate the complete academic reporting cycle from
  marks entry to parent delivery.

## 1.2 Core Philosophy

> "Build a School ERP Platform, not just a report card generator."

The system must be:

- **Scalable** — handle 1 to 1,000+ schools (via one Frappe site per
  school — see `docs/02_Database.md`).
- **Secure** — role-based access with granular permissions
  (`docs/11_Roles_And_Permissions.md`).
- **User-friendly** — teachers should learn it in under 15 minutes.
- **Reliable** — zero data loss, audit trails for all actions.

## 1.3 MVP Scope — What's In

| Feature Area | Specific Features |
|---|---|
| User Management | Admin, Teacher, Class Teacher, Headmaster, Bursar, Student, Parent roles |
| School Setup | Classes, Subjects, Terms, Grading Scales, Academic Years, Curricula (grading bands) |
| Marks Entry | Term Mark + Exam Mark per subject, subject comments, special case handling (Absent/Exempt/Medical Withdrawal) |
| Approval Workflow | Teacher submits → Class Teacher reviews → Headmaster approves/rejects |
| Report Generation | IGCSE-compliant multi-curriculum grade calculation (Cambridge/ZIMSEC), PDF generation |
| Portal Access | Student views own results; Parent views all linked children; Student/Parent view fees |
| Email Delivery | Automated PDF reports to parents |
| Print Function | Direct printing of report cards and fee statements |
| Billing & Fees | Termly flat-rate student fees by boarding type, payment tracking, ledger statements |

## 1.4 MVP Scope — What's Out (Future Phases)

- Native mobile apps (iOS/Android)
- SMS integration
- Parent–teacher chat
- Advanced finance/GL accounting (future `edupro_finance` app — basic termly billing is in MVP, see `docs/12_Finance_Billing.md`)
- AI-powered recommendations
- Attendance system (future `edupro_attendance` app)
- Timetable generation
- Online exams (live quiz-taking UX)

## 1.5 Success Metrics for MVP

| Metric | Target | How to Measure |
|---|---|---|
| Adoption rate | > 80% of teachers using system | Daily active users |
| Time to enter marks | < 1 hour for 30 students | User tracking |
| Report accuracy | 100% calculations correct | Automated testing (`docs/07`) |
| Parent satisfaction | > 90% positive feedback | Surveys |
| System uptime | > 99.5% | Monitoring tools |
| PDF generation speed | < 5 seconds per PDF | Performance logs |
| Support tickets | < 10 per month | Ticketing system |

## 1.6 Ongoing Support & Maintenance

| Aspect | Approach |
|---|---|
| Bug fixes | Priority-based, resolved within 48 hours |
| Data integrity | Daily automated backups, monthly manual verification |
| Security updates | Weekly vulnerability scanning |
| Performance monitoring | Real-time monitoring with alerts |
| User training | Video tutorials, documentation, quarterly workshops |
| Feature requests | Collected, prioritized, added to `.claude/TASKS.md` backlog |

## 1.7 Status

Pre-development. Sprint 0 (documentation/environment scaffolding) in
progress — see `.claude/TASKS.md`. Two architecture decisions
(`.claude/DECISIONS.md` 0004, 0005) must be resolved before Sprint 2.
