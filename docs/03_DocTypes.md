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
| Student | `Student` | |
| Parent/Guardian | `Guardian` + `Student Guardian` (child table on Student) | already supports multiple guardians per student |
| Enrollment / Subject Allocation | `Program Enrollment` + `Program Enrollment Course` | `Program` = a curriculum track (see Stream decision below); enrollment links a Student to a Program for an Academic Year, with a Program Enrollment Course row per subject |
| Grade Boundary | `Grading Scale` + `Grading Scale Interval` | one Grading Scale record holds all IGCSE grade intervals (A*–F); interval uses a single `threshold` percent per row (ranges are implied between consecutive thresholds), not an explicit min/max pair |
| Assessment weighting default | `Course.assessment_criteria` (child table, `Course Assessment Criteria`) | **correction (Sprint 3):** Test 40%/Exam 60% weighting is natively supported *per Course* via this child table (`assessment_criteria` Link + `weightage` Percent) — not something that only lives on the Assessment Plan. Set once per Course; each term's Assessment Plan should mirror it. |
| Assessment | `Assessment Plan` + `Assessment Plan Criteria` (child table) | one Assessment Plan per Class+Subject+Term. **Correction (Sprint 5):** the Plan's criteria child table uses raw `maximum_score` (points, e.g. Test=40/Exam=60 on a 100-point scale), not `weightage` (Percent) like Course does — the two are related but different fields; when creating a Plan, convert the Course's percentage weighting into actual points for that term's total. **Also (Sprint 5):** `Assessment Plan` models a literal scheduled exam session (`schedule_date`/`from_time`/`to_time` are required) and Education blocks overlapping time slots for the same Student Group — each subject within a class needs its own date/time slot; different classes can safely share slots. |
| Marks | `Assessment Result` + `Assessment Result Detail` (child table) | one Assessment Result per Student per Assessment Plan; `details` child table holds per-criteria (Test/Exam) scores. `total_score`/`grade`/per-criteria `grade` are all auto-calculated in `AssessmentResult.validate()` from the linked Grading Scale — confirmed via the controller source and a live test record (verified 35+52=87/100 → grade A, matching the 80–89 band), no custom calculation code needed. `special_case` Custom Field (Absent/Exempt/Medical Withdrawal) added Sprint 5. |

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
| logo | Attach Image | used in print formats/emails |
| motto | Data | |
| curriculum | Select | default `IGCSE` |
| timezone | Select | |
| status | Select | Active / Inactive / Suspended |

### Approval workflow (on `Assessment Result`)

**Built (Sprint 6, `.claude/DECISIONS.md` 0008):** the workflow lives on
a new `Report Card` DocType, not on `Assessment Result` directly —
`class_teacher_comment`/`headmaster_comment` are per-student, not
per-subject, so `Assessment Result` stays a simple submit-per-subject
doctype with no custom workflow of its own. Full state machine in
`docs/04_Workflows.md`.

`special_case` (Select: none/Absent/Exempt/Medical Withdrawal) — Custom
Field on `Assessment Result`, built Sprint 5.

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

Weights (test 40% / exam 60%) are the IGCSE-standard default, modeled as
two `Assessment Criteria` rows per `Assessment Plan` — configurable per
subject/assessment, not hardcoded.
