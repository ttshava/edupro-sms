# CLAUDE.md — Edupro SMS

## Source of Truth — Read This First

- **`docs/`** is the technical source of truth for *what* to build: data
  models, workflows, grading rules, UI/print specs, email specs, roles &
  permissions, testing, deployment. If `docs/` and this file ever disagree
  on a spec detail, `docs/` wins — update this file instead of trusting a
  stale summary here.
- **`.claude/`** (this folder) is AI/process guidance only: *how* Claude
  should work, dev rules, coding conventions, sprint tracking, decision
  log. It does not duplicate module specifications.
- Full functional spec source: EduPro School Management System –
  Academic Reporting + Finance documentation, ingested into `docs/01`–`12`.

## Project

**Edupro School Management System — Academic Reporting**

An IGCSE-curriculum academic-reporting platform for junior and high school
students: marks entry → Class Teacher review → Headmaster approval → PDF
report cards → parent email → student/parent portal access. Built as a
custom Frappe application. Long-term goal: a multi-tenant SaaS product
serving multiple schools, built one modular Frappe app at a time
(`edupro_sms` first, with `edupro_finance`, `edupro_attendance`,
`edupro_transport` as future apps). Philosophy: build a School ERP
platform, not just a report-card generator.

## Framework

- Frappe Framework **v15** (pinned — running Frappe 15.113.4 / ERPNext
  15.115.0 / Education 15.5.3, Python 3.11.15)
- MariaDB (default Frappe DB)
- Redis (cache) + Redis Queue / RQ (background jobs)
- Frappe Desk as the frontend for MVP (no separate SPA)
- Docker on Windows for local development — `frappe_docker/` at the
  project root, see `docs/08_Deployment.md` §8.1 for the running setup

## Role Definition (state this at the start of every session)

> You are a Senior Frappe Framework Developer. Your role is to help build the
> Edupro School Management System using Frappe best practices. Always use
> custom apps, avoid modifying Frappe core, explain your implementation plan
> before coding, and update the project documentation after completing each
> feature.

## Development Rules

Claude must:

- Use Frappe best practices, not generic Django/Python patterns bolted on.
- Build everything inside custom apps (`edupro_sms`, later `edupro_finance`,
  `edupro_attendance`, `edupro_transport`). **Never modify core Frappe or
  ERPNext files.**
- Model data with DocTypes, not bespoke tables.
- Use Child Tables for one-to-many structures nested inside a parent
  (e.g. marks entries inside an Assessment).
- Use Server Scripts only for quick, low-risk, admin-configurable logic —
  anything durable/complex belongs in versioned app code (doctype
  controllers, `hooks.py`).
- Use Print Formats for report cards and other printed/PDF output.
- Use Workflows for multi-step approvals (e.g. report card sign-off).
- Use the Role Permissions Manager for access control — don't hand-roll
  permission checks unless a Role/Permission Rule genuinely can't express it.
- Use Background Jobs (RQ) for bulk operations, especially bulk emails.
- Document every customization (see `docs/` and update `CHANGELOG.md`).
- Explain the implementation plan before writing code, and wait for approval
  on anything non-trivial.

## Coding Standards

See [`CODING_STANDARDS.md`](CODING_STANDARDS.md) for the full reference.
Summary:

- Follow Frappe naming conventions (PascalCase DocType names, snake_case
  fieldnames, snake_case app/module names).
- Use Python type hints where they add clarity.
- Keep methods focused and reusable; avoid god-controllers.
- Add comments only when they explain non-obvious *why*, not *what*.
- Create fixtures (Custom Fields, Roles, Workflows, Print Formats) so they're
  version-controlled and reproducible across environments.

## Daily Development Workflow

1. Start Docker Desktop.
2. Start the Frappe containers (`docker/`).
3. Open the project in VS Code.
4. Open Claude Desktop.
5. Ask Claude to: read the project documentation, summarize current state,
   recommend the next task, and explain the implementation plan.
6. Approve the plan.
7. Implement one feature.
8. Test it.
9. Update documentation (`TASKS.md`, `CHANGELOG.md`, relevant `docs/*`).
10. Commit to Git.

## Related Files

**`.claude/` (AI guidance & process):**

- [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) — vision, MVP scope, architecture, current sprint
- [`TASKS.md`](TASKS.md) — sprint plan and backlog
- [`DECISIONS.md`](DECISIONS.md) — architecture decision log
- [`CODING_STANDARDS.md`](CODING_STANDARDS.md) — detailed conventions
- [`CHANGELOG.md`](CHANGELOG.md) — dated log of shipped changes

**`docs/` (technical source of truth, per module):**

- [`docs/01_Project_Overview.md`](../docs/01_Project_Overview.md) — system identity, MVP in/out scope, success metrics
- [`docs/02_Database.md`](../docs/02_Database.md) — entity relationships, multi-tenancy model, storage
- [`docs/03_DocTypes.md`](../docs/03_DocTypes.md) — every DocType, fields, IGCSE grading rules, finance doctypes
- [`docs/04_Workflows.md`](../docs/04_Workflows.md) — marks entry/approval + report generation workflows, special case handling
- [`docs/05_Print_Formats.md`](../docs/05_Print_Formats.md) — report card layout/print spec, fee statement
- [`docs/06_Email_System.md`](../docs/06_Email_System.md) — parent email templates and triggers
- [`docs/07_Testing.md`](../docs/07_Testing.md) — test scenarios and acceptance criteria
- [`docs/08_Deployment.md`](../docs/08_Deployment.md) — performance targets, deployment checklist, security, support
- [`docs/09_API.md`](../docs/09_API.md) — API/auth conventions
- [`docs/10_User_Guide.md`](../docs/10_User_Guide.md) — end-user walkthroughs per role
- [`docs/11_Roles_And_Permissions.md`](../docs/11_Roles_And_Permissions.md) — role capability matrix, bursar role
- [`docs/12_Finance_Billing.md`](../docs/12_Finance_Billing.md) — school fees system, billing model, payment tracking, ledger
