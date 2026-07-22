# 11 — Roles & Permissions

The role model is central enough to the whole system to need its own
source of truth — referenced from every other doc.

## 11.1 Role Definitions & Capabilities

### System Administrator (Frappe Role: `System Manager`)

**Primary responsibility:** configure and maintain the system.

- Full CRUD on all system data.
- Configure system-wide settings, manage user accounts and roles.
- View audit logs, backup and restore.
- **Cannot** enter marks or approve reports unless also explicitly
  assigned a Teacher/Headmaster role.

### Teacher (Frappe Role: `Teacher`)

**Primary responsibility:** enter marks and subject-specific feedback.

- View assigned class(es)/subject(s) only (via `Class Subject
  Assignment`).
- Enter Term Mark and Exam Mark scores.
- Add subject-specific comments.
- Save marks as Draft; submit for approval.
- **Cannot** view marks for other classes/subjects, approve reports, or
  add Class Teacher/Headmaster comments.

Access is scoped in `teacher_permissions.py` to an exact `(student_group,
course)` match against `Class Subject Assignment` — a teacher assigned
only French in a class cannot see or enter marks for Mathematics in that
same class, even if they're that class's Class Teacher.

### Class Teacher (Frappe Role: `Class Teacher`, layered on top of `Teacher`)

**Primary responsibility:** manage a specific class.

- All Teacher capabilities, scoped to their own class(es).
- Add Class Teacher comment (general feedback).
- View all subjects for their class.
- Review marks before Headmaster approval.
- **Cannot** approve reports, manage other classes.

Determined by two independent grants: the `Student Group.class_teacher`
Link field *and* the Frappe `Class Teacher` role on the Instructor's
User — both are checked by `approvals._is_class_teacher_of()`, which
gates the class-review page, report-card comments, and the Review
workflow step. `teacher_assignment.assign_class_teacher()` sets both.

### Headmaster (Frappe Role: `Headmaster`)

**Primary responsibility:** final quality assurance and approval.

- View all classes and their status.
- Review individual student reports, add Headmaster comment.
- Approve/reject entire class reports.
- Generate final PDFs, trigger email to parents.
- View school fees and payment status; manage fees/ledger entries
  (create, edit, share) — see `docs/12_Finance_Billing.md`.
- **Cannot** enter marks or edit existing marks.

### Bursar (Frappe Role: `Bursar`)

**Primary responsibility:** day-to-day financial management.

- View and manage student fees (`Student Fee` CRUD).
- Record payments and create ledger entries.
- Print fee statements and payment receipts.
- **Cannot** enter marks, approve reports, or access academic data.

### Student (Frappe Role: `Student`, portal user)

**Primary responsibility:** access personal academic information.

- Login to `/my-reports`.
- View own report card (HTML + PDF) — only `Published` reports are
  visible, enforced server-side.
- View current and historical terms.
- Print/download report — permission-checked; a cross-student attempt
  returns HTTP 403.
- **Cannot** view other students' reports or access admin functions.

### Guardian (Frappe Role: `Guardian`, portal user)

**Primary responsibility:** monitor children's academic progress.

- View all linked children (via `Student.guardians`), same `/my-reports`
  page, grouped per child.
- Toggle between children's reports.
- Receive email notifications on Publish (`docs/06_Email_System.md`).
- Download/print PDF per child.
- **Cannot** view other guardians' children or access admin functions —
  enforced server-side (row-level query conditions + `has_permission`,
  fails closed for unmatched users).

## 11.2 DocType Permission Matrix

| DocType | Admin | Headmaster | Class Teacher | Bursar | Teacher | Student | Guardian |
|---|---|---|---|---|---|---|---|
| School Settings | CRUD | Read | – | – | – | – | – |
| Academic Year / Term | CRUD | Read | Read | – | Read | – | – |
| Student Group / Course / Class Subject Assignment | CRUD | Read | Read (own class) | – | Read (own) | – | – |
| Student / Guardian | CRUD | Read | Read (own class) | Read | Read (own class, limited) | Read (self) | Read (own children) |
| Assessment Result | CRUD | Read/Approve/Reject | Read/Comment (own class) | – | Create/Update (own, pre-approval) | Read (own, post-publish) | Read (children's, post-publish) |
| Report Card | Read | Approve/Publish | Comment (own class) | – | – | Read (own, post-publish) | Read (children's, post-publish) |
| Student Fee | CRUD | CRUD | – | CRUD | – | Read (own) | Read (children's) |
| Student Ledger Entry | CRUD | CRUD | – | CRUD | – | Read (own) | Read (children's) |

Report Card, Student Fee, and Student Ledger Entry rows use row-level
`get_permission_query_conditions`/`has_permission` scoping. Remaining
rows use Role Permissions Manager defaults only.
