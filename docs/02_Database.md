# 02 — Database

## 2.1 Engine

MariaDB (Frappe default), managed via the Docker Frappe setup in `docker/`.
Redis for cache and the RQ background job queue.

## 2.2 Multi-Tenancy Model

**Decision (accepted — see `.claude/DECISIONS.md` 0004):** one Frappe
**site** per school. Each site has its own database; the `edupro_sms`
app is installed on every site.

This means:

- **No `school_id` foreign key anywhere.** Tenant isolation is structural
  (separate DB per site), not a filter every query has to remember.
- The `School` entity from the original spec's ERD is **not** a DocType
  with rows — it becomes a per-site **Single DocType**, e.g. `School
  Settings` (name, code, address, phone, email, logo, motto, curriculum,
  timezone, status). One record per site, no list view.
- Cross-school reporting/analytics (if ever needed) would query across
  sites, not across rows in a shared table — out of scope for MVP.

If the owner decides against this (e.g. wants single-database
multi-tenancy for cross-school analytics), every entity below needs a
`school` Link field added back in, and permission rules need to filter by
it everywhere. That's a materially bigger and more error-prone build — flag
before Sprint 2.

## 2.3 Entity Relationships (translated from the source ERD)

```
Academic Year 1───* Term
Academic Year 1───* Class
Class 1───* Class Subject Assignment *───1 Subject
Class 1───* Student (via Enrollment)
Student *───1 Parent/Guardian (many students can share a guardian; a
    student can have multiple guardians — see docs/03)
Class 1───1 Class Teacher (a Teacher)
Class Subject Assignment *───1 Teacher (teacher assigned per class+subject)
Student *───* Marks *───1 Subject, *───1 Term
Student 1───* Report Card *───1 Term
Report Card *───* Marks (aggregated)

Finance (Sprint 8+):
Student 1───* Student Fee *───1 Academic Term
Student 1───* Student Ledger Entry *───1 Academic Term
Student Fee 1───* Student Ledger Entry (optional back-reference)
```

`School` does not appear in this diagram — it's implicit (the site). Full
field-level DocType definitions are in `docs/03_DocTypes.md` (including
the new Finance DocTypes in the Finance Module section).

## 2.4 Indexes

Frappe auto-indexes Link fields, but confirm/add explicit indexes on
high-traffic lookups once built:

- `Marks`: (`student`, `term`), (`class`, `subject`, `term`)
- `Report Card`: (`student`, `term`)
- `Enrollment`: (`student`, `academic_year`)

## 2.5 File Storage

```
storage/ (per site, under Frappe's private/public files)
├── reports/
│   ├── {academic_year}/
│   │   ├── {term}/
│   │   │   ├── student_{id}.pdf
│   │   │   ├── student_{id}_thumb.png
│   │   │   └── class_report_{class_id}.pdf
├── assets/
│   ├── logo.png
│   ├── signature_headmaster.png
│   └── signature_teacher.png
└── backups/
    ├── database_{date}.sql
    └── files_{date}.tar.gz
```

- **Priority:** cloud storage (S3 / Google Cloud) for production; local
  storage with regular backups as MVP fallback.
- **File types:** PDF, PNG, JPEG, CSV.
- **Naming:** `{type}_{id}_{timestamp}.{extension}`.
- **Retention:** report PDFs = permanent; temp uploads/exports = 7 days;
  backups = 30 days.

## 2.6 Backups

Use `bench backup` (per-site, since each school is its own site). Schedule
daily automated backups; store copies in the project's `backups/` folder
during local dev, and off-host storage once a real school's data exists.
Monthly manual verification per `docs/01` §1.6.
