# 04 — Workflows

Canonical state machines for `edupro_sms`. Implement exactly this — if code
and this doc ever disagree, fix the code (or open a decision in
`.claude/DECISIONS.md` if the doc genuinely needs to change).

## 4.1 Marks Entry & Approval Workflow

States (on `Marks`, rolling up to `Report Card`):

```
DRAFT
  → (Teacher enters test/exam scores + subject comment, saves)
  ↓ Teacher: "Submit for Approval"
    (validation: no blank scores; percentages/grades auto-calculated)
PENDING_APPROVAL
  ↓ Class Teacher: reviews all subjects for their class, adds
    Class Teacher comment, verifies calculations
REVIEWED
  ↓ Headmaster: reviews class reports, adds Headmaster comment
    ┌───────────────┐
    │   Approve?    │
    └───────────────┘
     YES │        │ NO
         ↓        ↓
    APPROVED   REJECTED
    (marks      (sent back with reason;
     locked;     Teacher fixes and
     PDF gen;    resubmits → back to
     email       PENDING_APPROVAL)
     queued)
         ↓
    PUBLISHED
    (Student + Parent portal access;
     print/download available)
```

**Locking rule:** once `APPROVED`, `Marks` and the derived `Report Card`
are locked server-side (see `.claude/CODING_STANDARDS.md`). Only System
Manager can override, with an audit trail entry.

**Rejection:** returns the *whole class's* batch (or the specific
student/subject, TBD at implementation — default to whatever granularity
the Headmaster rejected at) to `PENDING_APPROVAL` with the rejection reason
visible to the Teacher.

## 4.2 Report Card Generation Workflow

Triggered by: Headmaster selects Class + Term and clicks "Generate
Reports."

```
1. VALIDATION CHECK
   - All marks submitted?
   - All marks approved?
   - No missing scores?
   - No calculation errors?
   (Block generation and show a clear list of what's missing if any check fails.)

2. CALCULATE & AGGREGATE (per student)
   - Sum subject totals
   - Calculate average percentage
   - Determine overall grade
   - Calculate class position (see tie handling below)
   - Save to Report Card

3. GENERATE PDF (per student)
   - Frappe Print Format — see docs/05_Print_Formats.md
   - Store PDF, generate thumbnail for preview

4. EMAIL PARENTS (background job — RQ, not synchronous)
   - For each student: resolve linked guardian(s), send personalized
     email with PDF attached (docs/06_Email_System.md), log delivery
     status per recipient

5. UPDATE PORTAL ACCESS
   - Enable Student + Parent portal view
   - status → PUBLISHED
```

**Class position tie handling:** students with equal `average_percentage`
share the same position number (standard competition ranking, e.g. two
students tied at rank 3 both show "3", next student is "5" not "4").

## 4.3 Special Cases (Marks)

| Scenario | Rule |
|---|---|
| Absent from exam | `special_case = Absent` → score = 0 |
| Absent from test | `special_case = Absent` → score = 0 |
| Exempt from subject | `special_case = Exempt` → excluded from totals entirely |
| Incomplete marks | Cannot submit for approval — validation blocks it |
| Medical withdrawal | `special_case = Medical Withdrawal` → report shows "Withdrawn" for that subject |

## 4.4 Lifecycle FAQs

**Student transferred mid-term:** set `Student.status = Transferred`; keep
all historical Marks/Report Cards; generate a partial report (marks up to
transfer date) rather than deleting anything.

**Class promotion to next academic year:** create a new `Enrollment`
record for the new Academic Year + Class; the Student record itself is
unchanged (same `name`/identity), preserving full history across years.

**Can Teachers edit marks after approval?** No — locked (see §4.1). Only
System Manager can override, with audit trail.
