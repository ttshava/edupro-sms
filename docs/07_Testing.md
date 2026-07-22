# 07 — Testing

## 7.1 Strategy

- Use Frappe's built-in test framework (`FrappeTestCase`) for DocType
  controller logic — validation, grade calculation, class position
  calculation, workflow transitions, permission checks.
- Prioritize tests for anything with real business logic (grading,
  approval workflow, permissions) over CRUD-only DocTypes, which Frappe
  already exercises generically.
- Run via `bench run-tests --app edupro_sms` inside the dev container
  (needs `bench set-config allow_tests true` once per site).

## 7.2 Automated Coverage

`edupro_sms/edupro_sms/doctype/report_card/test_report_card.py` covers
the full Report Card lifecycle:

| Scenario | Expected Result |
|---|---|
| Teacher enters marks for many students | All marks saved, no data loss |
| Teacher submits marks with missing data | System blocks submission, shows warning |
| Headmaster approves a class | Workflow advances, record locks |
| Headmaster rejects a class | Goes back to Pending Approval, stays editable |
| Guardian with multiple children | Sees all of them (once Published) |
| Student portal login | Only sees own report — verified with a negative case too |
| PDF generation timing | Under target (see `docs/08_Deployment.md` §8.3) |
| Email parents | Sent, delivery status logged |
| Duplicate prevention | Blocked for the same student + assessment plan |
| Grade calculation | Matches IGCSE boundaries exactly at every threshold |
| Position calculation | Correct ranking; ties share a rank, next distinct rank skips |
| Historical term view | Previous term's data stays intact and queryable |

**Gotcha:** `FrappeTestCase`'s rollback isn't fully isolated between
test *methods* within one run — only `bench run-tests`' outer
transaction fully cleans up. A test asserting on data spanning an entire
`student_group` + `academic_term` (e.g. class-position ranking) needs
its own isolated Student Group, or it will see other tests' students.

## 7.3 Test Data

Use fixtures/factory helpers for common records (Academic Year, Class,
Student) rather than duplicating setup per test. Keep test data clearly
separate from real school data.

## 7.4 User Acceptance Testing Checklist

Full path: create academic year/term → set up classes/subjects → enroll
students → enter marks → submit → Class Teacher review → Headmaster
approve → publish → generate report cards → email parents →
student/parent portal view.

- [ ] **Admin**: log in, fill in real `School Settings`
- [ ] **Admin**: create the academic year + terms for the actual
      school calendar
- [ ] **Admin**: create real Student Groups (classes), Programs
      (streams), Courses (subjects)
- [ ] **Admin**: create Instructor, Guardian, Student records; set each
      Student Group's `class_teacher`
- [ ] **Teacher**: log in, open an Assessment Result, enter Term/Exam
      scores, submit — confirm the UI is usable without prior
      explanation
- [ ] **Headmaster**: run `generate_report_cards` for a class/term
- [ ] **Class Teacher**: review a Report Card, add a comment, click
      "Review"
- [ ] **Headmaster**: approve a Report Card (add comment, click
      "Approve"), confirm it locks; reject a different one and confirm
      the rejection reason is visible and it can be resubmitted
- [ ] **Headmaster**: click "Publish", confirm the report becomes
      visible on the portal and an email actually arrives
- [ ] **Student**: log into `/my-reports`, view and print/download the
      report card
- [ ] **Guardian**: log into `/my-reports` with an account linked to
      2+ children, confirm both show correctly
- [ ] **Visual/UX pass**: check the `IGCSE Report Card` print format
      renders cleanly (fonts, spacing, page breaks) when actually
      printed or saved as PDF from a browser
- [ ] **Headmaster dashboard**: open "Report Card Status by Class",
      confirm it's discoverable and readable

## 7.5 CI

Not currently set up.
