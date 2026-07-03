# 03 — DocTypes

Living reference for every DocType in `edupro_sms`, translated from the
source functional spec's data models into Frappe idioms (Link fields
instead of raw foreign-key ids, Frappe's `name` instead of a generic `id`
UUID, child tables instead of separate join-table entities where
appropriate). Update this file as each DocType is actually built — keep it
in sync with the real schema, not just the plan.

Per `.claude/DECISIONS.md` 0004, there is **no `School` DocType and no
`school`/`school_id` field anywhere** — multi-tenancy is one site per
school. If 0004 is overturned, every entity below needs a `school` Link
field added.

Per `.claude/DECISIONS.md` 0005 (open), these may end up extending Frappe's
Education app instead of being built fresh — treat the list below as the
target data model regardless of which implementation path is chosen.

---

## School Settings *(Single DocType, one per site)*

| Field | Type | Notes |
|---|---|---|
| school_name | Data | |
| school_code | Data | |
| address | Small Text | |
| phone | Data | |
| email | Data | |
| logo | Attach Image | used in print formats/emails |
| motto | Data | |
| curriculum | Select | default `IGCSE` |
| timezone | Select | |
| status | Select | Active / Inactive / Suspended |

## Academic Year

| Field | Type | Notes |
|---|---|---|
| name (autoname) | e.g. `2025-2026` | |
| start_date | Date | |
| end_date | Date | |
| is_current | Check | only one Academic Year should be current at a time — enforce in `validate` |
| status | Select | Active / Closed |

## Term

| Field | Type | Notes |
|---|---|---|
| academic_year | Link → Academic Year | |
| term_name | Data | e.g. "Term 1" |
| term_number | Int | 1–3 for IGCSE |
| start_date | Date | |
| end_date | Date | |
| marks_entry_deadline | Date | enforced server-side, not just UI hint |
| status | Select | Draft / Active / Closed |
| is_active | Check | |

## Class

| Field | Type | Notes |
|---|---|---|
| academic_year | Link → Academic Year | |
| class_name | Data | e.g. "Form 4A" |
| class_code | Data | |
| level | Select | IGCSE / AS / A-Level |
| stream | Select | Science / Commerce / Arts / General — kept as a field, not a separate DocType, for MVP simplicity |
| class_teacher | Link → Teacher | drives Class Teacher role permissions for this class |
| capacity | Int | |
| status | Select | Active / Inactive |

`current_enrollment` from the source spec is **derived** (count of active
Enrollment records for the class), not a stored field — avoid duplicated
state that can drift.

## Subject

| Field | Type | Notes |
|---|---|---|
| subject_code | Data | e.g. IGCSE code "0455" |
| subject_name | Data | |
| full_name | Data | e.g. "IGCSE Economics 0455" |
| category | Select | Sciences / Humanities / Languages / Mathematics / Creative Arts |
| max_score | Int | default 200 |
| test_weight | Percent | default 40 |
| exam_weight | Percent | default 60 — `validate`: test_weight + exam_weight = 100 |
| status | Select | Active / Inactive |

## Class Subject Allocation

| Field | Type | Notes |
|---|---|---|
| class | Link → Class | |
| subject | Link → Subject | |
| teacher | Link → Teacher | who teaches this subject for this class |

## Teacher

| Field | Type | Notes |
|---|---|---|
| user | Link → User | ties to Frappe login/auth |
| first_name / last_name | Data | |
| email / phone | Data | |
| status | Select | Active / Inactive |

Class Teacher is **not a separate DocType** — it's a Teacher referenced by
`Class.class_teacher`. The "Class Teacher" role/permission set applies
contextually to whichever classes list that teacher.

## Parent / Guardian

| Field | Type | Notes |
|---|---|---|
| user | Link → User | |
| first_name / last_name | Data | |
| relationship | Select | Father / Mother / Guardian |
| email / phone | Data | |
| address | Small Text | |
| occupation | Data | |
| status | Select | Active / Inactive |

Linked to students via the **Student.guardians** child table (supports
multiple parents per student, and one parent linked to multiple children —
see Student below).

## Student

| Field | Type | Notes |
|---|---|---|
| user | Link → User | for student portal login |
| first_name / last_name | Data | |
| date_of_birth | Date | |
| gender | Select | Male / Female / Other |
| admission_number | Data (unique) | |
| admission_date | Date | |
| email / phone | Data | |
| address | Small Text | |
| guardians | Table → Student Guardian (child) | supports multiple parents/guardians per student |
| status | Select | Active / Inactive / Graduated / Transferred / Withdrawn |

### Student Guardian *(child table)*

| Field | Type | Notes |
|---|---|---|
| guardian | Link → Parent | |
| is_primary | Check | |

## Enrollment

Tracks a student's class assignment per academic year (supports promotion
history — see `docs/04_Workflows.md` FAQ on promotion).

| Field | Type | Notes |
|---|---|---|
| student | Link → Student | |
| class | Link → Class | |
| academic_year | Link → Academic Year | |
| status | Select | Active / Transferred / Withdrawn |

## Grade Boundary

IGCSE grading scale — see `docs/03` §Grading below for the standard values;
kept as data (not hardcoded) so it's configurable per subject/school if
needed.

| Field | Type | Notes |
|---|---|---|
| grade | Data | A*, A, B, C, D, E, F |
| min_percentage | Float | inclusive lower bound |
| max_percentage | Float | inclusive upper bound |
| descriptor | Data | e.g. "Outstanding" |

## Marks

| Field | Type | Notes |
|---|---|---|
| student | Link → Student | |
| subject | Link → Subject | |
| class | Link → Class | |
| term | Link → Term | |
| test_score | Float | out of `Subject.max_score * test_weight%` |
| exam_score | Float | out of `Subject.max_score * exam_weight%` |
| total_score | Float (read-only, calculated) | test_score + exam_score |
| percentage | Float (read-only, calculated) | (total_score / max_score) * 100 |
| grade | Data (read-only, calculated) | looked up from Grade Boundary |
| subject_comment | Small Text | |
| special_case | Select | none / Absent / Exempt / Medical Withdrawal — see `docs/04` |
| status | Select | Draft / Pending Approval / Reviewed / Approved / Rejected / Published |
| entered_by | Link → User | |
| approved_by | Link → User | |

Calculations happen server-side (controller `validate`), never trusted from
client input.

## Report Card

Aggregation of a student's Marks for a Class + Term.

| Field | Type | Notes |
|---|---|---|
| student | Link → Student | |
| class | Link → Class | |
| term | Link → Term | |
| marks | Table → Report Card Subject Line (child, fetched from Marks) | |
| total_score | Float (calculated) | |
| average_percentage | Float (calculated) | |
| overall_grade | Data (calculated) | |
| position | Int (calculated) | class rank — see `docs/04` for tie handling |
| number_of_students | Int (calculated) | |
| class_teacher_comment | Small Text | |
| headmaster_comment | Small Text | |
| status | Select | Draft / Pending Approval / Approved / Published / Sent |
| pdf | Attach | generated PDF |
| sent_to_parent_at | Datetime | |
| viewed_by_parent_at | Datetime | |
| approved_by | Link → User | |
| approved_at | Datetime | |

---

## IGCSE Grading System

### Grade Boundaries (default seed data for Grade Boundary DocType)

| Grade | Percentage Range | Performance Level | Descriptor |
|---|---|---|---|
| A* | 90–100 | Outstanding | Exceptional performance |
| A | 80–89 | Excellent | High level of competence |
| B | 70–79 | Good | Sound level of understanding |
| C | 60–69 | Satisfactory | Acceptable standard |
| D | 50–59 | Below Average | Limited understanding |
| E | 40–49 | Poor | Basic understanding |
| F | 0–39 | Fail | Insufficient understanding |

### Calculation Rules

```
Per subject:
    total_score = test_score + exam_score
    percentage  = (total_score / max_score) * 100
    grade       = lookup(percentage, Grade Boundary)

Per report card:
    total_score        = sum(subject total_scores)
    average_percentage = (total_score / total_max_possible) * 100
    overall_grade       = lookup(average_percentage, Grade Boundary)
    position             = rank(student by average_percentage within class)
```

Weights (test 40% / exam 60%) are the IGCSE-standard default but are
configurable per Subject, not hardcoded — see `Subject.test_weight` /
`exam_weight` above.
