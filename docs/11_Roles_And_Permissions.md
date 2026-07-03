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

### Class Teacher (Frappe Role: `Class Teacher`, layered on top of `Teacher`)

**Primary responsibility:** manage a specific class.

- All Teacher capabilities, scoped to their own class(es).
- Add Class Teacher comment (general feedback).
- View all subjects for their class.
- Review marks before Headmaster approval.
- Recommend promotion/retention.
- **Cannot** approve reports, manage other classes.

Determined by `Class.class_teacher` — permission scoping should be
contextual (via `get_permission_query_conditions`, see
`.claude/CODING_STANDARDS.md`) rather than a flat role grant, since "which
class" varies per teacher.

### Headmaster (Frappe Role: `Headmaster`)

**Primary responsibility:** final quality assurance and approval.

- View all classes and their status.
- Review individual student reports.
- Add Headmaster comment.
- Approve entire class reports (bulk).
- Reject reports with a feedback reason.
- Generate final PDFs for printing.
- Trigger email to parents.
- **Cannot** enter marks or edit existing marks.

### Student (Frappe Role: `Student`, portal user)

**Primary responsibility:** access personal academic information.

- Login to student portal.
- View own report card (HTML + PDF).
- View current and historical terms.
- Print report.
- **Cannot** view other students' reports or access admin functions.

### Parent (Frappe Role: `Parent`, portal user)

**Primary responsibility:** monitor children's academic progress.

- View all linked children (via `Student.guardians`).
- Toggle between children's reports.
- View summary dashboard across all children.
- Receive email notifications.
- Download/print PDF per child.
- **Cannot** view other parents' children or access admin functions.

## 11.2 DocType Permission Matrix (fill in during Sprint 2)

| DocType | Admin | Headmaster | Class Teacher | Teacher | Student | Parent |
|---|---|---|---|---|---|---|
| School Settings | CRUD | Read | – | – | – | – |
| Academic Year / Term | CRUD | Read | Read | Read | – | – |
| Class / Subject / Allocation | CRUD | Read | Read (own class) | Read (own) | – | – |
| Student / Guardian | CRUD | Read | Read (own class) | Read (own class, limited) | Read (self) | Read (own children) |
| Marks | CRUD | Read/Approve/Reject | Read/Comment (own class) | Create/Update (own, pre-approval) | Read (own, post-publish) | Read (children's, post-publish) |
| Report Card | Read | Approve/Publish | Comment (own class) | – | Read (own, post-publish) | Read (children's, post-publish) |

This table is the target — implement it via the Role Permissions Manager
+ permission-query hooks where row-level scoping (own class / own
children) is needed, per `.claude/CODING_STANDARDS.md`.
