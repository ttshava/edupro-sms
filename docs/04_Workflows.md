# 04 — Workflows

Canonical state machines for `edupro_sms`. Implement exactly this — if code
and this doc ever disagree, fix the code (or open a decision in
`.claude/DECISIONS.md` if the doc genuinely needs to change).

**Since `.claude/DECISIONS.md` 0008 (2026-07-03, built and verified in
Sprint 6):** the approval workflow lives on a new `Report Card` DocType
(one per Student + Academic Term), not on `Assessment Result` directly.
`Assessment Result` (Frappe Education's doctype — see `docs/03_DocTypes.md`)
stays a simple per-subject submit: Draft → Submitted, no custom workflow.
The multi-step Class Teacher/Headmaster approval chain and the
class/headmaster comments operate at the Report Card level, since those
comments are per-student, not per-subject. This is a deliberate departure
from the original single-workflow-on-Marks sketch — see 0008 for the full
reasoning.

## 4.1 Subject Marks Entry (Assessment Result)

```
DRAFT
  → Teacher enters Test + Exam scores (+ subject comment), saves
  ↓ Teacher: "Submit" (standard Frappe submit — docstatus 0 → 1)
    (Education's own validation: scores ≤ maximum; no duplicate result
     for the same student+plan; grade/total auto-calculated from the
     Grading Scale — confirmed via `assessment_result.py`, no custom
     calc code needed)
SUBMITTED (docstatus = 1, locked)
```

That's it at the subject level — no Pending/Reviewed/Approved states
here. The multi-step approval happens once a student's full set of
results for a term exists (see §4.2).

## 4.2 Report Card Generation & Approval Workflow

Triggered by: Headmaster (or Class Teacher) selects a Class + Term and
runs `generate_report_cards(student_group, academic_term)` — a
whitelisted server method (Desk UI trigger point TBD, currently invoked
programmatically; see `TASKS.md` Sprint 8 polish item).

```
1. VALIDATION (per student, in generate_report_cards)
   - For each active student in the Student Group: do they have a
     submitted (docstatus=1) Assessment Result for every required course
     in their Program?
   - Missing any → student is SKIPPED and reported back by name, not
     silently included with a partial total. No batch-wide block —
     other students in the same class still generate normally.

2. CALCULATE & AGGREGATE (per student, creates/updates a Report Card
   in "Pending Approval")
   - Sum subject totals into total_score / maximum_score
   - average_percentage, overall_grade (via Grading Scale)
   - Snapshot each subject's result into the assessment_results child
     table (course, total_score, maximum_score, grade, comment)

3. CLASS POSITION (once per batch, across all Report Cards just
   generated/updated for that Student Group + Term)
   - Standard competition ranking by average_percentage descending:
     ties share a rank, the next distinct rank skips accordingly
     (two students tied at 3 both show "3", next shows "5" not "4")

4. APPROVAL WORKFLOW ("Report Card Approval", on Report Card)

   PENDING APPROVAL  (doc_status=0, set automatically on generation)
     ↓ Class Teacher: "Review" — adds class_teacher_comment
   REVIEWED  (doc_status=0)
     ↓ Headmaster: "Approve" — adds headmaster_comment
       ┌─────────────┐
       │  Approve?   │
       └─────────────┘
        YES │      │ NO ("Reject", with rejection_reason)
            ↓      ↓
       APPROVED   REJECTED
       (doc_status=1,  (doc_status=0; Class Teacher/
        LOCKED —        Headmaster: "Resubmit" →
        verified via     back to PENDING APPROVAL)
        UpdateAfterSubmitError
        on edit attempt)
            ↓ Headmaster: "Publish"
       PUBLISHED  (doc_status=1, locked, final)

5. PDF GENERATION (on demand today; hook into Publish transition planned
   for Sprint 7)
   - `IGCSE Report Card` Print Format (docs/05_Print_Formats.md),
     rendered via frappe.get_print + get_pdf — verified working
     end-to-end with a real generated PDF

6. EMAIL PARENTS + PORTAL ACCESS — Sprint 7, not built yet
```

**Locking rule (verified, not just planned):** Approved and Published
Report Cards have `docstatus=1`. Attempting to edit any field throws
`UpdateAfterSubmitError` — confirmed with a live test (tried changing
`total_score` post-Publish, got exactly that error). Only System Manager
can override via cancel+amend, with Frappe's standard amendment audit
trail.

**Rejection:** operates on the whole Report Card (i.e. the whole
student's term report), not a single subject — since the workflow lives
above the per-subject `Assessment Result` level, "reject this student's
report" is naturally one action, not N per-subject ones.

## 4.3 Special Cases (Assessment Result)

| Scenario | Rule | Implementation Status |
|---|---|---|
| Absent from exam | `special_case = Absent` → score = 0 (treated as 0 in total/grade calc) | ✅ Implemented (Sprint 8+) |
| Absent from test | `special_case = Absent` → score = 0 (treated as 0 in total/grade calc) | ✅ Implemented (Sprint 8+) |
| Exempt from subject | `special_case = Exempt` → excluded from totals entirely (not summed, not counted in average) | ✅ Implemented (Sprint 8+) |
| Incomplete marks | Cannot submit for approval — validation blocks it | ✅ Native to `Assessment Result` |
| Medical withdrawal | `special_case = Medical Withdrawal` → report shows "Withdrawn" for that subject (summed as 0 in totals) | ✅ Implemented (Sprint 8+) |

`special_case` is a Custom Field on `Assessment Result` (built Sprint 5), exported as a fixture. The effects on Report Card generation — which values are included/excluded/displayed — were implemented in Sprint 8+ via `edupro_sms/report_card.py::generate_report_cards()` and the `IGCSE Report Card` print format.

## 4.4 Lifecycle FAQs

**Student transferred mid-term:** set `Student.status = Transferred`; keep
all historical Assessment Results/Report Cards; generate a partial report
(marks up to transfer date) rather than deleting anything.

**Class promotion to next academic year:** create a new `Program
Enrollment` record for the new Academic Year + Student Group; the Student
record itself is unchanged (same `name`/identity), preserving full
history across years.

**Can Teachers edit marks after approval?** No — once a student's Report
Card reaches Approved/Published, `Assessment Result` scores that feed it
are historically accurate for that snapshot, and the Report Card itself
is locked. Editing an underlying `Assessment Result` after that point
doesn't retroactively change the locked Report Card (they're only
resynced by re-running `generate_report_cards`, which only touches
non-submitted Report Cards). Only System Manager can override via
cancel+amend, with audit trail.
