# Tasks — Edupro SMS

Forward-looking backlog. For the detailed historical record of how each
item was built (including the granular sprint-by-sprint log this file
used to hold), see `.claude/DECISIONS.md` and `.claude/CHANGELOG.md`.

## Completed

**MVP (all core modules):**

- [x] Roles, School Settings, Grading Scale (`docs/03_DocTypes.md`)
- [x] Academic structure via Frappe Education (Academic Year/Term,
      Program, Course, Student Group)
- [x] People (Student, Instructor, Guardian) with Custom Fields
      (`boarding_type`, `class_teacher`)
- [x] Marks entry (Assessment Plan/Result) with Term Mark/Exam Mark
      criteria
- [x] Report Card doctype + approval workflow (Pending → Reviewed →
      Approved/Rejected → Published)
- [x] IGCSE Report Card print format, with authenticity QR code and
      watermark
- [x] Parent email delivery on Publish
- [x] Student/Guardian portal (`/my-reports`)
- [x] Row-level permission scoping (Report Card, Assessment
      Plan/Result, Student, Student Fee/Ledger)
- [x] Finance module: Student Fee, Student Ledger Entry, Fee Statement/
      Payment Receipt print formats, Bursar role
- [x] Headmaster dashboard (academic + finance summary)
- [x] Automated test suite for Report Card lifecycle (`docs/07_Testing.md`)

**Production deployment (Frappe Cloud):**

- [x] Restructured the app to standard Frappe layout (nested module
      folder, `modules.txt`, package-qualified imports) — required for
      Frappe Cloud's GitHub-based app install
- [x] Deployed `edupro_sms` to a Frappe v16 bench on Frappe Cloud
- [x] Migrated production data from the local v15 instance (492
      students + all related academic/finance records) via backup
      restore
- [x] Configured custom domain (`firstclasshighschool.edupro.co.zw`)
- [x] Configured production email (two accounts, custom Edupro SMS
      branding) — `docs/06_Email_System.md`
- [x] Restored super-admin access

## In Progress / Open

- [ ] Clear the Frappe Cloud "site creation failed" flag — pending
      Frappe Cloud support running `bench migrate --skip-search-index`
      (see `docs/08_Deployment.md` §8.2). Blocks self-service domain/SSL
      verification and in-place migrate until resolved.
- [ ] Full browser-based UAT pass against production (`docs/07_Testing.md`
      §7.4) — most of the workflow has been exercised programmatically,
      not yet by a human clicking through the actual UI.
- [ ] Desk UI trigger for `generate_report_cards` (currently
      console/API only).
- [ ] Confirm scheduled backups are enabled on the production site.

## Backlog (not blocking, pick up as time allows)

- [ ] Headmaster-facing email delivery report (vs. digging through
      Error Log for failures).
- [ ] Guardian-facing fee history view on `/my-reports` (Fees tab).
- [ ] Rewrite or remove `analytics_api.py` / `fee_dashboard_api.py` —
      dead code referencing fields that don't exist in this schema
      (see `docs/12_Finance_Billing.md` §12.7 history).
- [ ] Load-test performance at 200+ students / concurrent users (only
      spot-checked at 20-student scale so far).

## Post-MVP / Future Apps

- `edupro_finance` — full GL/accounting, cost centers, payment gateway
  integration.
- `edupro_attendance` — attendance tracking.
- `edupro_transport` — transport/route management.
- Moodle/LMS integration — unfinished local-dev code
  (`setup_moodle_integration.py`) not currently part of the production
  app; revisit if/when needed.
