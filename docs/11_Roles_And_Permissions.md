# 11 — Roles & Permissions

New file (not in the original 10-doc skeleton) — added because the role
model is central enough to the whole system to need its own source of
truth, referenced from every other doc.

## 11.1 Role Definitions & Capabilities

### System Administrator (Frappe Role: `System Manager`)

**Primary responsibility:** configure and maintain the system.

- Full CRUD on all system data.
- Manage sites/schools (per `docs/02` §2.2, this means provisioning new
  Frappe sites, not rows in a shared table).
- Configure system-wide settings.
- Manage user accounts and role assignments.
- View audit logs.
- System backup and restore.
- **Cannot** enter marks or approve reports unless also explicitly
  assigned a Teacher/Headmaster role.

### Teacher (Frappe Role: `Teacher`)

**Primary responsibility:** enter marks and subject-specific feedback.

- View assigned class(es)/subject(s) only (via Class Subject Allocation).
- Enter test and exam scores.
- Add subject-specific comments.
- Save marks as Draft; submit for approval.
- **Cannot** view marks for other classes/subjects, approve reports, or
  add Class Teacher/Headmaster comments.

**Implementation (corrected 2026-07-09, `.claude/DECISIONS.md` 0021):**
`Assessment Plan`/`Assessment Result` access is scoped in
`teacher_permissions.py` to an exact `(student_group, course)` match
against `Class Subject Assignment` — the same table that assigns them
the subject in the first place. Earlier this scoped by `student_group`
alone, which meant teaching (or being Class Teacher of) *any* subject in
a class granted read/write access to *every* subject in that class. Now
a teacher assigned only French in a class cannot see or enter marks for
Mathematics in that same class, even if they're that class's Class
Teacher. This does not affect the Class Teacher's own whole-class
capabilities below — those are gated by a separate, independent check.

### Class Teacher (Frappe Role: `Class Teacher`, layered on top of `Teacher`)

**Primary responsibility:** manage a specific class.

- All Teacher capabilities, scoped to their own class(es).
- Add Class Teacher comment (general feedback).
- View all subjects for their class.
- Review marks before Headmaster approval.
- Recommend promotion/retention.
- **Cannot** approve reports, manage other classes.

Determined by `Student Group.class_teacher` (Custom Field, added Sprint 4
— see `docs/03_DocTypes.md`). **Permission scoping built and verified,
Sprint 7:** `get_permission_query_conditions` on `Report Card` restricts a
Class Teacher to only Student Groups where they're the `class_teacher`
(`edupro_sms/edupro_sms/doctype/report_card/report_card.py`) — contextual,
not a flat role grant, since "which class" varies per teacher.

**Two separate grants are required, not one:** the `Student Group.class_teacher`
Link field *and* the Frappe `Class Teacher` role on the Instructor's
User — `approvals._is_class_teacher_of()` (which gates the class-review
page, report-card comments, and the Review workflow step) checks both.
`teacher_assignment.assign_class_teacher()` sets the Link field and now
(2026-07-09, `.claude/DECISIONS.md` 0021) auto-grants the role too, so a
newly-designated Class Teacher isn't locked out of their own class. The
teacher dashboard surfaces this distinctly: a **"My Class"** section
(only shown to Class Teachers) always lists the classes they manage,
separate from **"Subjects You Teach"** (their `Class Subject Assignment`
rows) — previously the only Class Teacher-specific UI was a "Review"
link that only appeared when a report card happened to be pending.

### Headmaster (Frappe Role: `Headmaster`)

**Primary responsibility:** final quality assurance and approval.

- View all classes and their status.
- Review individual student reports.
- Add Headmaster comment.
- Approve entire class reports (bulk).
- Reject reports with a feedback reason.
- Generate final PDFs for printing.
- Trigger email to parents.
- View school fees and payment status (read-only).
- Manage individual fees and ledger entries (create, edit, share) — see `docs/12_Finance_Billing.md`.
- **Cannot** enter marks or edit existing marks.

### Bursar (Frappe Role: `Bursar`, built Sprint 8+)

**Primary responsibility:** day-to-day financial management.

- View and manage student fees (`Student Fee` CRUD).
- Record payments and create ledger entries (`Student Ledger Entry` create/read/write).
- Print fee statements for students/parents.
- Generate fee reports (TBD, Sprint 9+).
- **Cannot** enter marks, approve reports, or access academic data.

(Created as a fixture in `edupro_sms/fixtures/role.json`.)

### Student (Frappe Role: `Student`, portal user)

**Primary responsibility:** access personal academic information.

- Login to student portal — **built, Sprint 7**: `/my-reports`
  (`edupro_sms/www/my-reports/`).
- View own report card (HTML + PDF) — built, only `Published` reports
  are visible (enforced server-side, not just hidden in the UI).
- View current and historical terms — built (page lists all accessible
  terms; only one term of data exists so far to test with).
- Print report — built (print/download link per report, using the
  `IGCSE Report Card` format; permission-checked, verified a
  cross-student attempt gets HTTP 403).
- **Cannot** view other students' reports or access admin functions —
  verified with a real negative-case HTTP test, not just assumed.

### Parent (Frappe Role: `Guardian`, portal user)

**Primary responsibility:** monitor children's academic progress. (Role
is named `Guardian` in Frappe/Education, not `Parent` — same concept.)

- View all linked children (via `Student.guardians` / reverse-synced
  `Guardian.students`) — **built, Sprint 7**, same `/my-reports` page,
  grouped per child.
- Toggle between children's reports — built (each child gets its own
  block on the page; verified with a guardian linked to two students).
- View summary dashboard across all children — the per-child grouping on
  `/my-reports` covers this for MVP; a dedicated dashboard view is not
  built.
- Receive email notifications — built, Sprint 7
  (`docs/06_Email_System.md`), triggered automatically on Publish.
- Download/print PDF per child — built, same print link as Student.
- **Cannot** view other parents' children or access admin functions —
  verified server-side (row-level query conditions + single-doc
  `has_permission`, fails closed for unmatched users).

## 11.2 DocType Permission Matrix

| DocType | Admin | Headmaster | Class Teacher | Bursar | Teacher | Student | Parent |
|---|---|---|---|---|---|---|---|
| School Settings | CRUD | Read | – | – | – | – | – |
| Academic Year / Term | CRUD | Read | Read | – | Read | – | – |
| Class / Subject / Allocation | CRUD | Read | Read (own class) | – | Read (own) | – | – |
| Student / Guardian | CRUD | Read | Read (own class) | Read | Read (own class, limited) | Read (self) | Read (own children) |
| Marks | CRUD | Read/Approve/Reject | Read/Comment (own class) | – | Create/Update (own, pre-approval) | Read (own, post-publish) | Read (children's, post-publish) |
| Report Card | Read | Approve/Publish | Comment (own class) | – | – | Read (own, post-publish) | Read (children's, post-publish) |
| Student Fee | CRUD | CRUD | – | CRUD | – | Read (own) | Read (children's) |
| Student Ledger Entry | CRUD | CRUD | – | CRUD | – | Read (own) | Read (children's) |

**Report Card row is built and verified (Sprint 7)** — uses row-level `get_permission_query_conditions` and `has_permission` checks per role.

**Student Fee and Student Ledger Entry rows built and verified (Sprint 8+)** — use role-based CRUD permissions via Role Permissions Manager; no row-level scoping implemented (all Bursars see all fees across all students). Student/Parent access is read-only to their own/linked children's records, enforced server-side.

**Remaining rows (School Settings, Academic Year/Term, Class/Subject, Student/Guardian)** use Role Permissions Manager defaults only; no row-level scoping implemented. Revisit if any of those are later exposed to non-admin roles with sensitive data that needs isolation.
