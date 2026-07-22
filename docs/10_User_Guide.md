# 10 — User Guide

End-user walkthroughs by role. Role capabilities/permissions are defined
authoritatively in `docs/11_Roles_And_Permissions.md` — this file is the
"how to" companion, not the source of truth for what each role can do.

## For System Administrators

- Setting up `School Settings` (name, logo, motto, curriculum board)
- Managing user accounts and role assignments
- Viewing audit logs (Frappe's built-in document versioning)

## For Headmasters

- Reviewing a class's submitted marks
- Adding a Headmaster comment
- Approving vs. rejecting a class's reports
- Generating and printing report cards
- Triggering parent emails (via Publish)
- Viewing the finance dashboard (revenue collected, outstanding balance)

## For Class Teachers

- Reviewing all subjects for their class before Headmaster approval
- Adding a Class Teacher comment
- Viewing their "My Class" section on the teacher dashboard

## For Teachers

- Entering Term Mark and Exam Mark for an assigned class + subject
- Adding subject-specific comments
- Saving as draft vs. submitting for approval

## For Bursars

- Billing students for a term (`Student Fee`)
- Recording payments
- Printing fee statements and payment receipts

## For Students

- Logging into `/my-reports`
- Viewing current and historical report cards
- Downloading/printing a PDF report
- Viewing fee statements

## For Guardians

- Logging into `/my-reports`
- Switching between multiple linked children
- Downloading/printing each child's report
- Understanding the report card email notification

## FAQ

**What if a student is transferred mid-term?** See
`docs/04_Workflows.md` §4.4.

**What about promotion to the next academic year?** See
`docs/04_Workflows.md` §4.4.

**Can teachers edit marks after approval?** No — see
`docs/04_Workflows.md` §4.1.

**How are multiple guardians per student handled?** A Student can have
multiple linked Guardians (child table); all linked guardians can view
that student's reports and receive report emails.

**What if a report card email doesn't arrive?** Check the guardian's
email address is a real, deliverable mailbox — `docs/06_Email_System.md`
§6.5 covers bounce handling.
