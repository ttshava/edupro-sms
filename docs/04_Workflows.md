# 04 — Workflows

Canonical state machines for `edupro_sms`. If code and this doc ever
disagree, fix the code — this is the intended behavior.

The approval workflow lives on `Report Card` (one per Student + Academic
Term), not on `Assessment Result` directly, since Class Teacher/
Headmaster comments are per-student, not per-subject. `Assessment
Result` (Frappe Education's doctype) stays a simple per-subject submit:
Draft → Submitted, with no custom workflow of its own.

## 4.1 Subject Marks Entry (Assessment Result)

```
DRAFT
  → Teacher enters Term Mark + Exam Mark (+ subject comment), saves
  ↓ Teacher: "Submit" (standard Frappe submit — docstatus 0 → 1)
    (Education's own validation: scores ≤ maximum; no duplicate result
     for the same student+plan; grade/total auto-calculated from the
     Grading Scale)
SUBMITTED (docstatus = 1, locked)
```

That's it at the subject level — no Pending/Reviewed/Approved states
here. The multi-step approval happens once a student's full set of
results for a term exists (§4.2).

## 4.2 Report Card Generation & Approval Workflow

Triggered by a Headmaster or Class Teacher selecting a Class + Term and
running `generate_report_cards(student_group, academic_term)` (a
whitelisted server method).

```
1. VALIDATION (per student)
   - Does every active student in the Student Group have a submitted
     (docstatus=1) Assessment Result for every required course in their
     Program?
   - Missing any → student is SKIPPED and reported back by name; no
     batch-wide block. Other students in the same class still generate.

2. CALCULATE & AGGREGATE (per student — creates/updates a Report Card
   in "Pending Approval")
   - Sum subject totals into total_score / maximum_score
   - average_percentage, overall_grade (via Grading Scale)
   - Snapshot each subject's result into assessment_results (course,
     total_score, maximum_score, grade, comment)

3. CLASS POSITION (once per batch, across all Report Cards just
   generated/updated for that Student Group + Term)
   - Standard competition ranking by average_percentage descending:
     ties share a rank, the next distinct rank skips accordingly
     (two students tied at 3rd both show "3", next shows "5")

4. APPROVAL WORKFLOW ("Report Card Approval", on Report Card)

   PENDING APPROVAL  (docstatus=0, set automatically on generation)
     ↓ Class Teacher: "Review" — adds class_teacher_comment
   REVIEWED  (docstatus=0)
     ↓ Headmaster: "Approve" — adds headmaster_comment
       ┌─────────────┐
       │  Approve?   │
       └─────────────┘
        YES │      │ NO ("Reject", with rejection_reason)
            ↓      ↓
       APPROVED   REJECTED
       (docstatus=1,   (docstatus=0; Class Teacher/
        LOCKED)         Headmaster: "Resubmit" →
            ↓            back to PENDING APPROVAL)
       Headmaster: "Publish"
            ↓
       PUBLISHED  (docstatus=1, locked, final)

5. PDF GENERATION
   - `IGCSE Report Card` print format (`docs/05_Print_Formats.md`)

6. EMAIL PARENTS + PORTAL ACCESS
   - Triggered automatically on Publish — `docs/06_Email_System.md`
```

**Locking rule:** Approved and Published Report Cards have `docstatus=1`.
Editing any field throws `UpdateAfterSubmitError`. Only System Manager
can override, via cancel + amend, with Frappe's standard amendment audit
trail.

**Rejection** operates on the whole Report Card (i.e. the whole
student's term report), not a single subject — the workflow lives above
the per-subject `Assessment Result` level, so "reject this student's
report" is naturally one action.

## 4.3 Special Cases (Assessment Result)

| Scenario | Rule |
|---|---|
| Absent from exam or test | `special_case = Absent` → score = 0 (included in totals as 0) |
| Exempt from subject | `special_case = Exempt` → excluded from totals entirely (not summed, not counted in the average) |
| Incomplete marks | Cannot submit for approval — validation blocks it |
| Medical withdrawal | `special_case = Medical Withdrawal` → shown as "Withdrawn" for that subject on the report (summed as 0 in totals) |

`special_case` is a Custom Field on `Assessment Result`, exported as a
fixture. The effects on Report Card generation are implemented in
`edupro_sms/report_card.py::generate_report_cards()` and reflected in
the `IGCSE Report Card` print format.

## 4.4 Lifecycle FAQs

**Student transferred mid-term:** set `Student.status = Transferred`;
keep all historical Assessment Results/Report Cards; generate a partial
report (marks up to transfer date) rather than deleting anything.

**Class promotion to next academic year:** create a new `Program
Enrollment` record for the new Academic Year + Student Group; the
Student record itself is unchanged (same identity), preserving full
history across years.

**Can teachers edit marks after approval?** No — once a student's
Report Card reaches Approved/Published, the underlying `Assessment
Result` scores are historically accurate for that snapshot, and the
Report Card itself is locked. Editing an `Assessment Result` afterward
doesn't retroactively change a locked Report Card — only System Manager
can override via cancel + amend.
