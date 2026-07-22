# 03 — DocTypes

`edupro_sms` extends Frappe's **Education** app rather than modeling
Class/Subject/Marks/etc. from zero. This file documents: (1) which
Education DocTypes are reused as-is, (2) how IGCSE concepts map onto
them, (3) what's custom-built in `edupro_sms`.

Per `docs/02_Database.md`, there is **no `School` DocType and no
`school`/`school_id` field anywhere** — multi-tenancy is one site per
school.

All custom DocTypes below live under
`edupro_sms/edupro_sms/doctype/<name>/` (the app's Frappe *module*
folder — see the root [`README.md`](../README.md) for why the path is
nested).

---

## Reused from the Education app

| IGCSE concept | Education DocType | Notes |
|---|---|---|
| Academic Year | `Academic Year` | used as-is |
| Term | `Academic Term` | used as-is |
| Class | `Student Group` | one Student Group per class/section (`group_based_on = Batch`). **Custom Field:** `class_teacher` (Link → Instructor) — used for permission scoping and the approval workflow's "Class Teacher" step. |
| Subject | `Course` | one Course per IGCSE subject |
| Teacher | `Instructor` | |
| Student | `Student` | **Custom Field:** `boarding_type` (Select: Day Boarder/Full Boarder) — drives fee calculation, `docs/12_Finance_Billing.md` |
| Guardian | `Guardian` + `Student Guardian` (child table on Student) | supports multiple guardians per student out of the box |
| Enrollment | `Program Enrollment` + `Program Enrollment Course` | `Program` = a curriculum track/stream; enrollment links a Student to a Program for an Academic Year, with one `Program Enrollment Course` row per subject |
| Grade Boundary | `Grading Scale` + `Grading Scale Interval` | one Grading Scale record holds all IGCSE grade intervals (F–A*); each interval is a single percentage threshold, with ranges implied between consecutive thresholds |
| Assessment weighting | `Course.assessment_criteria` (child table, `Course Assessment Criteria`) | Two independently-graded criteria per subject: **`Term Mark`** and **`Exam Mark`**, each out of 100. The names are load-bearing — report-card generation looks them up by exact string. |
| Assessment | `Assessment Plan` + `Assessment Plan Criteria` (child table) | one Assessment Plan per Class + Subject + Term. Requires an `assessment_group` (Link → `Assessment Group`, a tree doctype — leaf groups named e.g. `"2026 Term 2"`). Also models a literal exam session (`schedule_date`/`from_time`/`to_time`); Education blocks overlapping time slots for the same Student Group. |
| Marks | `Assessment Result` + `Assessment Result Detail` (child table) | one Assessment Result per Student per Assessment Plan; `details` holds per-criteria (Term Mark/Exam Mark) scores. `total_score`/`grade` are auto-calculated from the linked Grading Scale. **Custom Field:** `special_case` (Absent/Exempt/Medical Withdrawal) — see `docs/04_Workflows.md` §4.3. |

**Stream / Program design:** each stream (e.g. Science/Commerce/Arts) is
its own `Program` record, since `Program.courses` is exactly "which
subjects this track takes." A `Student Group` (the actual class, e.g.
"Form 4A") links to one `Program` via its `program` field; multiple
parallel sections can share one Program.

---

## Custom-built in `edupro_sms`

### School Settings *(Single DocType, one per site)*

Per-site branding — nothing in Education covers this.

| Field | Type | Notes |
|---|---|---|
| school_name | Data | |
| school_code | Data | |
| address | Small Text | |
| phone | Data | |
| email | Data | |
| logo | Attach Image | used in print formats/emails; must be public so Guest users can view it on `/login` |
| motto | Data | |
| curriculum_board | Select | Cambridge / ZIMSEC (default Cambridge) — determines which Grading Scale is active |
| timezone | Select | |
| status | Select | Active / Inactive / Suspended |

### Report Card *(is_submittable, one per Student + Academic Term)*

Aggregates a student's submitted `Assessment Result`s for a term via
`generate_report_cards(student_group, academic_term)` — a whitelisted
server method that skips (and reports by name) any student missing a
required course, rather than silently generating a partial report.

| Field | Type | Notes |
|---|---|---|
| student | Link → Student | |
| student_group | Link → Student Group | |
| academic_year | Link → Academic Year | fetched from student_group |
| academic_term | Link → Academic Term | |
| assessment_results | Table → Report Card Assessment Result | snapshot rows: assessment_result, course, total_score, maximum_score, grade, comment |
| total_score / maximum_score / average_percentage / overall_grade | calculated | derived from `assessment_results` |
| position / number_of_students | Int, calculated | standard competition ranking — ties share a rank, next distinct rank skips |
| class_teacher_comment / headmaster_comment | Small Text | filled in during the Reviewed/Approved workflow steps |
| rejection_reason | Small Text | shown when `workflow_state = Rejected` |
| pdf | Attach | generated via the `IGCSE Report Card` print format |
| sent_to_parent_at / viewed_by_parent_at | Datetime | |
| workflow_state | Link → Workflow State | driven by the "Report Card Approval" workflow |

Approved and Published report cards are real submitted/locked records
(`docstatus=1`) — editing one throws `UpdateAfterSubmitError`, the same
guarantee Frappe gives any submittable doctype.

### Report Card Assessment Result *(child table)*

Snapshot row of one subject's result at report-generation time —
decoupled from the live `Assessment Result` so a report stays accurate
even if the underlying mark is later amended.

### Class Subject Assignment *(one per Class/Subject/Academic Year)*

Maps which Instructor teaches which Course to which Student Group in
which Academic Year. Used for permission scoping (an Instructor sees
only their assigned classes/subjects) and data-entry routing.

| Field | Type | Notes |
|---|---|---|
| student_group | Link → Student Group | the class |
| course | Link → Course | the subject |
| academic_year | Link → Academic Year | |
| instructor | Link → Instructor | the assigned teacher |
| instructor_name | Data | fetch_from instructor.instructor_name, read-only |

**Naming:** hash-based. **Permissions:** System Manager (full CRUD),
Headmaster (create/read/write/share), Instructor (read-only).

### Curriculum *(grading band)*

Not the academic stream (that's `Program`) — a **grading band**: `"Form
1-2"`, `"O Level"`, `"A Level"`. Referenced by `Program.curriculum`,
which drives the grading-scale lookup in `edupro_sms/grading.py`.

| Field | Type | Notes |
|---|---|---|
| name | Data | e.g. "Form 1-2", "O Level", "A Level" |
| title | Data | descriptive label |

---

## Finance Module

Two DocTypes implement school fees — see `docs/12_Finance_Billing.md`
for the full billing model.

### Student Fee *(one per Student + Academic Term)*

| Field | Type | Notes |
|---|---|---|
| student | Link → Student | required |
| student_name | Data | fetch_from student.student_name, read-only |
| academic_year | Link → Academic Year | read-only, set from context |
| academic_term | Link → Academic Term | required |
| boarding_type | Select | Day Boarder / Full Boarder — determines `amount` |
| amount | Currency | billed amount |
| amount_paid | Currency | default 0, updated on payment entry |
| balance | Currency | amount − amount_paid, read-only |
| status | Select | Billed / Partially Paid / Paid (read-only, auto-set) |
| billed_on | Date | |
| due_date | Date | |

**Naming:** `SF-{student}-{academic_term}`. **Permissions:** System
Manager (full), Headmaster (create/read/write/share), Bursar
(create/read/write/share), Student/Guardian (read-only, own/linked
children only).

### Student Ledger Entry *(many per Student, auto-created)*

A time-series ledger — one row per billing event (fee billed, payment
received), rendered as a running Debit/Credit/Balance statement.

| Field | Type | Notes |
|---|---|---|
| student | Link → Student | required |
| student_name | Data | fetch_from student.student_name, read-only |
| posting_datetime | Datetime | required, indexed; auto-set to now() |
| academic_term | Link → Academic Term | optional context |
| reference_student_fee | Link → Student Fee | optional, links back to the triggering fee record |
| description | Data | e.g. "Term 2 fees billed", "Payment received" |
| debit | Currency | default 0; amount owed |
| credit | Currency | default 0; amount paid |
| balance | Currency | running balance, read-only |

**Naming:** hash-based. **Permissions:** same as Student Fee. **Sort:**
`posting_datetime` ascending (oldest first, like a bank statement).

---

## IGCSE Grading System

### Grade Boundaries

| Grade | Threshold (%) | Performance Level | Descriptor |
|---|---|---|---|
| F | 0 | Fail | Insufficient understanding |
| E | 40 | Poor | Basic understanding |
| D | 50 | Below Average | Limited understanding |
| C | 60 | Satisfactory | Acceptable standard |
| B | 70 | Good | Sound level of understanding |
| A | 80 | Excellent | High level of competence |
| A* | 90 | Outstanding | Exceptional performance |

### Calculation Rules

```
Per subject (Assessment Result):
    total_score = term_mark + exam_mark   (Assessment Result Detail rows)
    percentage  = (total_score / maximum_score) * 100
    grade       = lookup(percentage, Grading Scale)

Per report card (aggregated across a term's Assessment Results):
    total_score        = sum(subject total_scores)
    average_percentage = (total_score / total_max_possible) * 100
    overall_grade       = lookup(average_percentage, Grading Scale)
    position             = rank(student by average_percentage within Student Group)
```

Term Mark and Exam Mark, each out of 100 (200 combined), is this
school's convention — modeled as two `Assessment Criteria` rows per
`Assessment Plan`, configurable per subject rather than hardcoded.
