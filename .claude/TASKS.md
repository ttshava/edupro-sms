# Tasks — Edupro SMS

Sprints follow the module build order, updated to reflect the full IGCSE
functional spec (see `docs/`). Check items off as they're completed;
update `CHANGELOG.md` when a sprint's work ships.

## Sprint 0 — Documentation & Environment Scaffolding

- [x] Create `.claude/` documentation set
- [x] Ingest full functional spec into `docs/01`–`11`
- [x] Decide `.claude/DECISIONS.md` 0004 (site-per-school, accepted) and
      0005 (spike first in Sprint 1, accepted)
- [ ] Install Docker Desktop, VS Code, Git, Claude Desktop

## Sprint 1 — Project Setup

- [ ] Install Frappe via Docker (`docker/`)
- [ ] Create custom app `edupro_sms`
- [ ] Configure site (one site = one school, per 0004 — accepted)
- [ ] Configure Git (repo init, `.gitignore`, first commit)
- [ ] Spike: install/inspect Frappe's Education app, evaluate options
      (a) build fresh (b) extend Education app (c) cherry-pick — record
      outcome as DECISIONS.md 0006 before Sprint 2 starts

## Sprint 2 — Foundation: Roles, Academic Year, Terms, Grading Scale

- [ ] Roles: Admin, Teacher, Class Teacher, Headmaster, Student, Parent
      (see `docs/11_Roles_And_Permissions.md`)
- [ ] School Settings (Single DocType — per-site)
- [ ] Academic Year DocType
- [ ] Term DocType (with `marks_entry_deadline`)
- [ ] Grade Boundary DocType (IGCSE A*–F scale, configurable — `docs/03`)

## Sprint 3 — Academic Structure

- [ ] Class DocType (includes stream as a field, per `docs/03`)
- [ ] Subject DocType (configurable test/exam weights, default 40/60)
- [ ] Class–Subject allocation

## Sprint 4 — People

- [ ] Teacher DocType
- [ ] Class Teacher designation (Teacher + assigned Class)
- [ ] Parent/Guardian DocType (supports multiple parents per student)
- [ ] Student DocType
- [ ] Student–Class Enrollment (tracks history across academic years)

## Sprint 5 — Assessments & Marks

- [ ] Marks DocType (test_score, exam_score, calculated total/percentage/grade)
- [ ] Subject comment field
- [ ] Special-case handling: Absent (ABS), Exempt, Medical Withdrawal (MW)
      — see `docs/04_Workflows.md` §special cases
- [ ] Save-as-draft + submit-for-approval actions

## Sprint 6 — Approval Workflow & Reporting

- [ ] Workflow: Draft → Pending Approval → Reviewed (Class Teacher) →
      Approved/Rejected (Headmaster) → Published (`docs/04`)
- [ ] Class Teacher comment
- [ ] Headmaster comment + bulk class approval
- [ ] Class position calculation (with tie handling)
- [ ] Report Card DocType (aggregation)
- [ ] Report Card Print Format matching `docs/05_Print_Formats.md`
- [ ] PDF generation

## Sprint 7 — Portals & Communication

- [ ] Student portal: view own report card (current + historical terms)
- [ ] Parent portal: view all linked children, switch between them
- [ ] Print function (Desk + portal)
- [ ] Email Queue & Parent Emailing (background job, HTML template —
      `docs/06_Email_System.md`)
- [ ] Delivery status logging

## Sprint 8 — Dashboards, Testing & MVP Release

- [ ] Headmaster dashboard (class status overview)
- [ ] Run test scenarios TC-01–TC-12 (`docs/07_Testing.md`)
- [ ] Performance check against targets (`docs/08_Deployment.md`)
- [ ] User Acceptance Testing
- [ ] Prepare MVP release (deployment checklist, `docs/08`)

## Backlog (post-MVP)

- `edupro_finance` app
- `edupro_attendance` app
- `edupro_transport` app
- Native mobile apps, SMS integration, parent-teacher chat
- AI-powered recommendations
- Timetable generation, online exams
- Multi-school analytics/reporting across sites (only relevant if 0004 is
  revisited)
