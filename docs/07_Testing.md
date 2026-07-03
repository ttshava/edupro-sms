# 07 — Testing

## 7.1 Strategy

- Use Frappe's built-in test framework (`FrappeTestCase`) for DocType
  controller logic — validation, grade calculation, class position
  calculation, workflow transitions, permission checks.
- Run via `bench run-tests --app edupro_sms` inside the Docker container.
- Prioritize tests for anything with business logic (grade calculation,
  approval workflow, permissions) over CRUD-only DocTypes, which Frappe
  already covers generically.
- Target: > 80% code coverage on `edupro_sms` app code.

## 7.2 Required Test Scenarios

| ID | Description | Expected Result |
|---|---|---|
| TC-01 | Teacher enters marks for 30 students | All marks saved, no data loss |
| TC-02 | Teacher submits marks with missing data | System blocks submission, shows warning |
| TC-03 | Headmaster approves a class | All reports generated, status updated |
| TC-04 | Headmaster rejects a class | Reports go back to draft/pending, notification sent |
| TC-05 | Parent portal login with 3 children | Shows all 3 children, can switch views |
| TC-06 | Student portal login | Only sees own report |
| TC-07 | Generate PDF for 200 students | All generated within 5 minutes |
| TC-08 | Email 200 parents | All sent, delivery status logged |
| TC-09 | Duplicate prevention | System prevents duplicate Marks entries (same student+subject+term) |
| TC-10 | Grade calculation | All grades match IGCSE boundaries (`docs/03`) |
| TC-11 | Position calculation | Correct ranking, handles ties (`docs/04` §4.2) |
| TC-12 | Historical term view | Can access reports from previous terms |

## 7.3 Test Data

- Use fixtures/factory helpers for common records (Academic Year, Class,
  Student) rather than duplicating setup per test.
- Keep test data clearly separate from any real pilot-school data.

## 7.4 User Acceptance Testing (Sprint 8)

Full path: create academic year/term → enroll students → allocate
subjects → enter marks → submit → Class Teacher review → Headmaster
approve → generate report cards → email parents → student/parent portal
view. Write the detailed UAT checklist once MVP features are complete.

## 7.5 CI

Not yet set up. TBD once the repo is on a Git host with CI available.
