# 02 — Database

## 2.1 Engine

MariaDB (Frappe's default database). Redis provides caching and backs the
RQ background job queue. In production, all of this is managed by
Frappe Cloud; locally it runs in Docker (`docs/08_Deployment.md`).

## 2.2 Multi-Tenancy Model

**One Frappe site per school.** Each site has its own database; the
`edupro_sms` app is installed on every site that needs it.

This means:

- **No `school_id` foreign key anywhere.** Tenant isolation is
  structural (a separate database per site), not a filter every query
  has to remember to apply.
- There is no `School` DocType with rows. Instead, each site has a single
  **`School Settings`** Single DocType (name, code, address, phone,
  email, logo, motto, curriculum board, timezone, status) — one record
  per site, no list view.
- Cross-school reporting (if ever needed) would query across sites, not
  across rows in a shared table — out of scope today.

Onboarding a second school means provisioning a new Frappe site with
`edupro_sms` installed, not adding a row anywhere.

## 2.3 Entity Relationships

```
Academic Year 1───* Academic Term
Academic Year 1───* Student Group (class)
Student Group 1───* Class Subject Assignment *───1 Course (subject)
Student Group 1───* Student (via Program Enrollment)
Student *───1..* Guardian (many-to-many via Student Guardian child table)
Student Group 1───1 Class Teacher (an Instructor, via a Custom Field)
Class Subject Assignment *───1 Instructor (teacher assigned per class+subject)
Student *───* Assessment Result *───1 Course, *───1 Assessment Plan (term)
Student 1───* Report Card *───1 Academic Term
Report Card *───* Assessment Result (aggregated, snapshotted)

Finance:
Student 1───* Student Fee *───1 Academic Term
Student 1───* Student Ledger Entry *───0..1 Student Fee (back-reference)
```

`School` doesn't appear here — it's implicit (the site itself). Full
field-level DocType definitions are in `docs/03_DocTypes.md`.

## 2.4 Indexes

Frappe auto-indexes Link fields. The high-traffic lookups worth
confirming explicit indexes on:

- `Assessment Result`: (`student`, `assessment_plan`)
- `Report Card`: (`student`, `academic_term`)
- `Student Ledger Entry`: `posting_datetime` (ledger is always read in
  date order)

## 2.5 File Storage

Production (Frappe Cloud) stores public/private files as managed object
storage — no manual path management needed. Locally, Frappe's standard
per-site `public/files/` and `private/files/` folders under
`sites/<site>/`.

- **File types in use:** PDF (report cards, fee statements), PNG/JPEG
  (school logo, signatures), CSV (bulk import).
- **Retention:** report card PDFs are permanent (attached to the
  `Report Card` record); backups follow Frappe Cloud's retention policy.

## 2.6 Backups

See `docs/13_Backup_Restore.md` for the full backup/restore procedure —
production backups are Frappe Cloud's managed `Restore with files`
mechanism; local dev uses `bench backup --with-files`.
