# 10 — User Guide

End-user walkthroughs, written once the MVP is functional enough to walk
through real workflows with screenshots. Role capabilities/permissions are
defined authoritatively in `docs/11_Roles_And_Permissions.md` — this file
is the "how to" companion, not the source of truth for what each role can
do.

## For System Administrators

- Setting up a new school site, `School Settings`
- Managing user accounts and role assignments
- Viewing audit logs

## For Headmasters

- Reviewing a class's submitted marks
- Adding a Headmaster comment
- Approving vs. rejecting a class's reports (bulk approval)
- Generating and printing report cards
- Triggering parent emails

## For Class Teachers

- Reviewing all subjects for their class before Headmaster approval
- Adding a Class Teacher comment
- Recommending promotion/retention

## For Teachers

- Entering test and exam scores for an assigned class+subject
- Adding subject-specific comments
- Saving as draft vs. submitting for approval
- Responding to a rejected submission

## For Students

- Logging into the student portal
- Viewing current and historical report cards
- Downloading/printing a PDF report

## For Parents

- Logging into the parent portal
- Switching between multiple linked children
- Viewing the summary dashboard across all children
- Downloading/printing each child's report
- Understanding the report card email notification

## FAQ (from the source spec, ported for reference)

**What if a student is transferred mid-term?** See
`docs/04_Workflows.md` §4.4.

**What about promotion to the next academic year?** See
`docs/04_Workflows.md` §4.4.

**Can teachers edit marks after approval?** No — see
`docs/04_Workflows.md` §4.1.

**What if a school doesn't use the 40/60 test/exam split?** Weights are
configurable per Subject — see `docs/03_DocTypes.md` (Subject
`test_weight`/`exam_weight`).

**How are multiple parents per student handled?** A Student can have
multiple linked Guardians (child table); all linked guardians can view
that student's reports and receive report emails — see
`docs/03_DocTypes.md` (Student Guardian).

---

Not yet written in full — populate with real screenshots during Sprint 8
(UAT).
