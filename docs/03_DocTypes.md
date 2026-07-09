# 03 — DocTypes

**Superseded the from-scratch plan on 2026-07-03** — see
`.claude/DECISIONS.md` 0007. `edupro_sms` extends Frappe's Education app
rather than modeling Class/Subject/Marks/etc. from zero. This file now
documents: (1) which Education DocTypes we use as-is, (2) how IGCSE
concepts map onto them, (3) what's custom-built in `edupro_sms`.

Per `.claude/DECISIONS.md` 0004, there is **no `School` DocType and no
`school`/`school_id` field anywhere** — multi-tenancy is one site per
school.

---

## Reused from the Education app (installed, small Custom Field additions where noted)

| IGCSE concept | Education DocType | Notes |
|---|---|---|
| Academic Year | `Academic Year` | used as-is |
| Term | `Academic Term` | used as-is; `marks_entry_deadline` doesn't exist natively — add via Custom Field if enforced server-side, or track informally for MVP |
| Class | `Student Group` | one Student Group per class/section; `group_based_on = Batch`. **Custom Field added (Sprint 4):** `class_teacher` (Link → Instructor) — Education's `Student Group Instructor` child table has no lead/primary flag, so this is a dedicated field for permission scoping and the approval workflow's "Class Teacher" step. Fixture: `edupro_sms/fixtures/custom_field.json`. |
| Subject | `Course` | one Course per IGCSE subject |
| Teacher | `Instructor` | |
| Student | `Student` | **Custom Field added (Sprint 8+):** `boarding_type` (Select: Day Boarder/Full Boarder) — used for fee calculation in the finance module (`docs/12_Finance_Billing.md`) |
| Parent/Guardian | `Guardian` + `Student Guardian` (child table on Student) | already supports multiple guardians per student |
| Enrollment / Subject Allocation | `Program Enrollment` + `Program Enrollment Course` | `Program` = a curriculum track (see Stream decision below); enrollment links a Student to a Program for an Academic Year, with a Program Enrollment Course row per subject |
| Grade Boundary | `Grading Scale` + `Grading Scale Interval` | one Grading Scale record holds all IGCSE grade intervals (A*–F); interval uses a single `threshold` percent per row (ranges are implied between consecutive thresholds), not an explicit min/max pair |
| Assessment weighting default | `Course.assessment_criteria` (child table, `Course Assessment Criteria`) | **corrected 2026-07-09 (real convention, confirmed against `report_card.py`'s `_subject_row()` and the school's actual grading practice):** two independently-graded criteria, **`Term Mark`** and **`Exam Mark`**, each out of 100 — not a weighted split summing to 100. `weightage` is set 50/50 per Course as a default; each term's Assessment Plan mirrors the two criteria names exactly (the names are load-bearing — `report_card.py` looks them up by exact string `"Term Mark"`/`"Exam Mark"` to render the per-criterion breakdown on the printed report). |
| Assessment | `Assessment Plan` + `Assessment Plan Criteria` (child table) | one Assessment Plan per Class+Subject+Term — **corrected 2026-07-09:** criteria child table is `[{"assessment_criteria": "Term Mark", "maximum_score": 100}, {"assessment_criteria": "Exam Mark", "maximum_score": 100}]`, `maximum_assessment_score = 200`. **Mandatory field gotcha:** `Assessment Plan.assessment_group` (Link → `Assessment Group`, a separate tree doctype from `Academic Term`) is required and easy to miss — inserts fail with a plain `assessment_group` validation error otherwise. This school's leaf groups are named `"{academic_year} Term {n}"` (e.g. `"2026 Term 2"`), children of a root `"All Assessment Groups"` group. `Assessment Plan` also models a literal scheduled exam session (`schedule_date`/`from_time`/`to_time` are required) and Education blocks overlapping time slots for the same Student Group — each subject within a class needs its own date/time slot; different classes can safely share slots. |
| Marks | `Assessment Result` + `Assessment Result Detail` (child table) | one Assessment Result per Student per Assessment Plan; `details` child table holds per-criteria (Term Mark/Exam Mark) scores. `total_score`/`grade`/per-criteria `grade` are all auto-calculated in `AssessmentResult.validate()` from the linked Grading Scale — confirmed via the controller source and a live test record (verified 35+52=87/100 → grade A, matching the 80–89 band), no custom calculation code needed. `special_case` Custom Field (Absent/Exempt/Medical Withdrawal) added Sprint 5 — **implementation status (Sprint 8+):** Absent/Exempt/Medical Withdrawal now affect Report Card calculations correctly (see `docs/04_Workflows.md` §4.3). |

**Stream decision (Sprint 3, `.claude/DECISIONS.md`):** not a Custom
Field. Each stream (Science/Commerce/Arts/General) is its own `Program`
record (e.g. "IGCSE Science", "IGCSE Commerce"), since `Program.courses`
(child table `Program Course`) is exactly "which subjects this track
takes" — different streams genuinely take different subject sets, so
that's a Program-level concern, not a label. `Student Group` (the actual
class, e.g. "Form 4A") links to a `Program` via its existing `program`
field — multiple Student Groups (parallel sections) can share one
Program.

## Custom-built in `edupro_sms`

### School Settings *(Single DocType, one per site)*

Nothing in Education covers this — still needed for per-site branding.

| Field | Type | Notes |
|---|---|---|
| school_name | Data | |
| school_code | Data | |
| address | Small Text | |
| phone | Data | |
| email | Data | |
| logo | Attach Image | used in print formats/emails; must be set to public so Guest users can view it on `/login` |
| motto | Data | |
| curriculum_board | Select | Cambridge / ZIMSEC (default Cambridge) — determines which set of grading scales are active for this school |
| timezone | Select | |
| status | Select | Active / Inactive / Suspended |

### Approval workflow (on `Assessment Result`)

**Built (Sprint 6, `.claude/DECISIONS.md` 0008):** the workflow lives on
a new `Report Card` DocType, not on `Assessment Result` directly —
`class_teacher_comment`/`headmaster_comment` are per-student, not
per-subject, so `Assessment Result` stays a simple submit-per-subject
doctype with no custom workflow of its own. Full state machine in
`docs/04_Workflows.md`.

`special_case` (Select: none/Absent/Exempt/Medical Withdrawal) — Custom Field on `Assessment Result`, built Sprint 5. Affects Report Card generation (Sprint 8+): Absent/Exempt/Medical Withdrawal entries are now correctly handled per `docs/04_Workflows.md` §4.3.

### Report Card *(built Sprint 6 — `is_submittable`, one per Student + Academic Term)*

Aggregates a student's already-submitted `Assessment Result`s for a term.
Generated via `generate_report_cards(student_group, academic_term)`
(whitelisted, `report_card.py`), which skips (and reports) any student
missing a required course rather than generating a partial report.

| Field | Type | Notes |
|---|---|---|
| student | Link → Student | |
| student_group | Link → Student Group | |
| academic_year | Link → Academic Year | fetch_from student_group |
| academic_term | Link → Academic Term | |
| assessment_results | Table → Report Card Assessment Result | snapshot rows: assessment_result, course, total_score, maximum_score, grade, comment |
| total_score / maximum_score / average_percentage / overall_grade | calculated | summed/derived from `assessment_results` |
| position / number_of_students | Int (calculated) | standard competition ranking — ties share a rank, next distinct rank skips (`docs/04`) |
| class_teacher_comment / headmaster_comment | Small Text | filled in during the Reviewed/Approved workflow steps |
| rejection_reason | Small Text | shown when `workflow_state = Rejected` |
| pdf | Attach | generated via the `IGCSE Report Card` print format |
| sent_to_parent_at / viewed_by_parent_at | Datetime | wired in Sprint 7 |
| workflow_state | Link → Workflow State | driven by the "Report Card Approval" workflow |

Workflow states map `doc_status` so **Approved and Published are real
submitted/locked records** (docstatus=1), not just a status label —
verified by attempting an edit post-Published and getting
`UpdateAfterSubmitError`.

### Class Subject Assignment *(built Sprint 8+ — many per Class/Subject/Academic Year)*

Maps the relationship: which Instructor teaches which Course to which Student Group in which Academic Year. Used for permission scoping (an Instructor sees only their assigned classes/subjects) and for data entry routing (teacher sees only their assigned marks-entry forms).

| Field | Type | Notes |
|---|---|---|
| student_group | Link → Student Group | the class |
| course | Link → Course | the subject |
| academic_year | Link → Academic Year | |
| instructor | Link → Instructor | the assigned teacher |
| instructor_name | Data | fetch_from instructor.instructor_name, read-only |

**Naming:** Hash-based (no business key). **Permissions:** System Manager (full CRUD), Headmaster (create/read/write/share), Instructor (read-only).

### Curriculum *(built Sprint 3, repurposed in Sprint 8+ for grading bands)*

**Not** the academic program/stream (that's `Program`). Instead, represents a **grading band** — a set of curriculum/Form level mappings for applying the correct Grading Scale.

Originally intended as: `"Cambridge IGCSE"`, `"Cambridge AS Level"` (2 records).
Repurposed in `.claude/DECISIONS.md` 0019 to: `"Form 1-2"`, `"O Level"`, `"A Level"` (3 grading bands).

| Field | Type | Notes |
|---|---|---|
| name | Data | e.g. "Form 1-2", "O Level", "A Level" |
| title | Data | descriptive label |

Referenced by `Program.curriculum` (Link field) — enables the grading scale lookup in `edupro_sms/grading.py::get_grading_scale_for_program()` to select the correct scale for a student based on their Program's band + the school's `curriculum_board` setting.

---

## Finance Module (built Sprint 8+, documented in `docs/12_Finance_Billing.md`)

Two DocTypes implement the school fees system:

### Student Fee *(one per Student + Academic Term)*

A billing record — one fee per student per term, determined by the student's `boarding_type` (Day Boarder=750, Full Boarder=1450, configurable via `fees.py::BOARDING_FEE`).

| Field | Type | Notes |
|---|---|---|
| student | Link → Student | required |
| student_name | Data | fetch_from student.student_name, read-only |
| academic_year | Link → Academic Year | read-only, set from context |
| academic_term | Link → Academic Term | required |
| boarding_type | Select | Day Boarder / Full Boarder — determines `amount` |
| amount | Currency | billed amount (calculated from boarding_type) |
| amount_paid | Currency | default 0, updated on payment entry |
| balance | Currency | amount - amount_paid, read-only |
| status | Select | Billed / Partially Paid / Paid (read-only, auto-set) |
| billed_on | Date | |
| due_date | Date | |

**Naming:** `SF-{student}-{academic_term}` (e.g. `SF-STU-001-2026 (Term 1)`). **Permissions:** System Manager (full), Headmaster (create/read/write/share), Bursar (create/read/write/share), Student/Guardian (read-only).

**Note:** Deliberately not built on Education's Fee Structure/Fee Schedule/Fees chain — that pipeline generates ERPNext Sales Invoices with GL posting, which this school doesn't use. Mirrors `Report Card`'s design choice (see `.claude/DECISIONS.md` 0008).

### Student Ledger Entry *(many per Student, auto-created)*

A time-series accounting ledger — one row per billing event (fee billed, payment received). Rendered as a running Debit/Credit/Balance statement in the Fee Statement print format, similar to a bank statement.

| Field | Type | Notes |
|---|---|---|
| student | Link → Student | required |
| student_name | Data | fetch_from student.student_name, read-only |
| posting_datetime | Datetime | required, indexed; auto-set to now() on creation |
| academic_term | Link → Academic Term | optional, context link |
| reference_student_fee | Link → Student Fee | optional, links back to the fee record that triggered this entry |
| description | Data | e.g. "Term 2 fees billed", "Payment received" |
| debit | Currency | default 0; amount owed by student (fee billed) |
| credit | Currency | default 0; amount paid by student |
| balance | Currency | running balance (total debits - total credits), read-only |

**Naming:** Hash-based. **Permissions:** System Manager (full), Headmaster (create/read/write/share), Bursar (create/read/write/share), Student/Guardian (read-only). **Sort order:** by `posting_datetime` ASC (oldest first, like a ledger).

---

## IGCSE Grading System

### Grade Boundaries (seed data for `Grading Scale` / `Grading Scale Interval`)

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
    total_score = test_score + exam_score   (from Assessment Result Detail rows)
    percentage  = (total_score / maximum_score) * 100
    grade       = lookup(percentage, Grading Scale)

Per report card (aggregated across a term's Assessment Results):
    total_score        = sum(subject total_scores)
    average_percentage = (total_score / total_max_possible) * 100
    overall_grade       = lookup(average_percentage, Grading Scale)
    position             = rank(student by average_percentage within Student Group)
```

Term Mark and Exam Mark, each out of 100 (200 combined), are this
school's actual convention (corrected 2026-07-09 — see §row above),
modeled as two `Assessment Criteria` rows per `Assessment Plan` —
configurable per subject/assessment, not hardcoded.
