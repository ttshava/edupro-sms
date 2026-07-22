# Edupro SMS

**Official repository for First Class High School's academic reporting
and finance system.**

Edupro SMS is a custom [Frappe Framework](https://frappeframework.com/)
application that manages the full academic reporting cycle — marks entry,
Class Teacher review, Headmaster approval, IGCSE-graded report cards,
parent email delivery, and school fee billing — plus student/parent
self-service portals.

Long-term goal: a multi-tenant School ERP platform (one Frappe app per
concern — `edupro_sms` first, `edupro_finance`/`edupro_attendance`/
`edupro_transport` later), not just a report-card generator.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Framework | [Frappe Framework](https://frappeframework.com/) v16 (production) / v15 (local dev — see [`docs/08_Deployment.md`](docs/08_Deployment.md)) |
| Base ERP | [ERPNext](https://erpnext.com/) — Sales/Accounting scaffolding only; this app does not use ERPNext's GL/invoicing |
| Curriculum data model | [Frappe Education](https://github.com/frappe/education) — Student, Instructor, Course, Program, Assessment Plan/Result, Grading Scale, etc. (see [`docs/03_DocTypes.md`](docs/03_DocTypes.md)) |
| Database | MariaDB |
| Cache / Queue | Redis + RQ (background jobs) |
| Language | Python 3.10+ (backend), JavaScript (Frappe Desk client scripts) |
| PDF rendering | wkhtmltopdf via Frappe's native Print Format pipeline |
| QR codes | `qrcode` + `Pillow` (report-card authenticity verification) |
| Frontend | Frappe Desk (admin/staff) + Frappe website pages (`www/`, student/parent portals) — no separate SPA |
| Hosting (production) | [Frappe Cloud](https://frappecloud.com/) |
| Hosting (local dev) | Docker Desktop + [`frappe_docker`](https://github.com/frappe/frappe_docker) |

## Repository Structure

```
Edupro SMS/
├── edupro_sms/                    # the Frappe app (this is what gets installed on a site)
│   ├── hooks.py                   # app config: boot, portal routes, permissions, doc events, fixtures
│   ├── modules.txt                # "Edupro SMS" — the single module this app owns
│   ├── patches.txt                # schema migration patches (empty — none yet)
│   │
│   ├── edupro_sms/                # the app's Frappe *module* folder (doctype/report/print_format live here)
│   │   ├── doctype/                   # Class Subject Assignment, Curriculum, Report Card,
│   │   │                              #   Report Card Assessment Result, School Settings,
│   │   │                              #   Student Fee, Student Ledger Entry
│   │   ├── print_format/              # igcse_report_card, fee_statement, payment_receipt
│   │   └── report/                    # my_classes, report_card_status_by_class
│   │
│   ├── *.py                       # business-logic modules at the package root, e.g.:
│   │   ├── academic_calendar.py       # term/year helpers
│   │   ├── approvals.py               # report-card review/approval helpers
│   │   ├── boot.py                    # boot_session hook
│   │   ├── branding.py                # School Settings → Website Settings sync
│   │   ├── class_review.py            # Class Teacher review page data
│   │   ├── dashboard.py                # Headmaster dashboard stats
│   │   ├── fee_permissions.py          # row-level scoping for Student Fee / Ledger
│   │   ├── fees.py                     # billing rules, fee/ledger creation
│   │   ├── grading.py                  # grade-boundary lookup
│   │   ├── marks_entry.py              # teacher marks-entry page data
│   │   ├── qr.py                       # report-card verification QR code
│   │   ├── student_hooks.py            # Student.after_insert → ensure Student role
│   │   ├── student_permissions.py      # row-level scoping for Student
│   │   ├── teacher_assignment.py       # Class Subject Assignment helpers, class-teacher grants
│   │   ├── teacher_permissions.py      # row-level scoping for Assessment Plan/Result
│   │   └── watermark.py                # report-card watermark / school logo data URI
│   │
│   ├── fixtures/                  # version-controlled Roles, Grading Scale, Custom Fields,
│   │                              #   Workflow + Workflow State/Action, Custom DocPerm
│   ├── public/                    # js/ + css/ assets
│   ├── templates/                 # shared Jinja includes/pages
│   └── www/                       # portal pages: dashboard, my-reports, bursar*, marks-entry,
│                                  #   class-review, admin, verify-report-card, import-data
│
├── docs/                          # technical source of truth — see index below
├── .claude/                       # AI/process guidance (how Claude should work on this repo)
├── frappe_docker/                 # vendored clone for local dev (gitignored)
├── pyproject.toml                 # app metadata + Python dependencies
└── apps.txt                       # "edupro_sms" (bench app list)
```

**Note on the nested `edupro_sms/edupro_sms/` folder:** this isn't a
mistake — it's standard Frappe app layout. The outer `edupro_sms/` is the
Python package (what gets pip-installed); the inner `edupro_sms/edupro_sms/`
is the Frappe *module* folder where DocTypes, Print Formats, and Reports
must live so Frappe's migration tooling can find them. Business-logic
`.py` files that aren't tied to a specific DocType live at the outer
package root.

## Documentation Index

Technical source of truth — if a doc and this README ever disagree on a
detail, the doc wins.

| Doc | Covers |
|---|---|
| [`docs/01_Project_Overview.md`](docs/01_Project_Overview.md) | Project identity, scope, success metrics |
| [`docs/02_Database.md`](docs/02_Database.md) | Multi-tenancy model, entity relationships |
| [`docs/03_DocTypes.md`](docs/03_DocTypes.md) | Every DocType, fields, IGCSE grading rules |
| [`docs/04_Workflows.md`](docs/04_Workflows.md) | Marks entry, approval workflow, special cases |
| [`docs/05_Print_Formats.md`](docs/05_Print_Formats.md) | Report card & fee statement layout |
| [`docs/06_Email_System.md`](docs/06_Email_System.md) | Parent email delivery, SMTP setup |
| [`docs/07_Testing.md`](docs/07_Testing.md) | Test strategy, scenarios, UAT checklist |
| [`docs/08_Deployment.md`](docs/08_Deployment.md) | Local dev (Docker) + production (Frappe Cloud) |
| [`docs/09_API.md`](docs/09_API.md) | API/auth conventions |
| [`docs/10_User_Guide.md`](docs/10_User_Guide.md) | End-user walkthroughs per role |
| [`docs/11_Roles_And_Permissions.md`](docs/11_Roles_And_Permissions.md) | Role capability matrix |
| [`docs/12_Finance_Billing.md`](docs/12_Finance_Billing.md) | School fees, billing, ledger |
| [`docs/13_Backup_Restore.md`](docs/13_Backup_Restore.md) | Backup/restore procedure |

## Quickstart (local development)

Full setup detail is in [`docs/08_Deployment.md`](docs/08_Deployment.md) —
summary:

```bash
cd frappe_docker
docker compose -p edupro -f compose.edupro.yaml up -d
docker compose -p edupro -f compose.edupro.yaml exec backend bash
# inside the container:
bench --site edupro.localhost migrate
```

Site: `http://localhost:8080` (or the configured `host_name`).

## Production

Hosted on **Frappe Cloud**, custom domain
`firstclasshighschool.edupro.co.zw`. See
[`docs/08_Deployment.md`](docs/08_Deployment.md) for bench/site details.

## Development Rules

- **Never modify core Frappe/ERPNext/Education files.** Everything
  school-specific lives in `edupro_sms`.
- Model data with DocTypes, not bespoke tables.
- Fixtures (Roles, Workflow, Custom Fields, Custom DocPerm) are
  version-controlled — don't hand-configure them only in the Desk UI on
  one site.
- See [`.claude/CODING_STANDARDS.md`](.claude/CODING_STANDARDS.md) for
  detailed conventions.
