# 07 — Testing

## 7.1 Strategy

- Use Frappe's built-in test framework (`FrappeTestCase`) for DocType
  controller logic — validation, grade calculation, class position
  calculation, workflow transitions, permission checks. **Built, Sprint 8**
  — `edupro_sms/edupro_sms/doctype/report_card/test_report_card.py`
  covers all 12 required scenarios (§7.2), 12/12 passing.
- Run via `bench run-tests --app edupro_sms` inside the Docker container
  (needs `bench set-config allow_tests true` once per site).
- Prioritize tests for anything with business logic (grade calculation,
  approval workflow, permissions) over CRUD-only DocTypes, which Frappe
  already covers generically — matches what got built: all coverage is on
  `Report Card`, since that's where the actual `edupro_sms` business logic
  lives (Sprints 2–5 mostly configured Education's own already-tested
  DocTypes).
- Formal coverage percentage not measured (no coverage tool wired up yet)
  — the 12 scenarios exercise every code path in `report_card.py` and
  `notify.py` at least once, which is the practical target for this size
  of codebase.
- **Gotcha:** `FrappeTestCase`'s rollback isn't fully isolated between
  test *methods* within one run — only `bench run-tests`' outer
  transaction fully cleans up. A test asserting on data that spans the
  *entire* `student_group` + `academic_term` (like class position
  ranking) will see other tests' students unless it uses its own isolated
  Student Group. See the test file's `setUp`/TC-11 for the pattern.

## 7.2 Required Test Scenarios — automated, Sprint 8, all pass

`edupro_sms/edupro_sms/doctype/report_card/test_report_card.py` — run via
`bench --site edupro.localhost run-tests --app edupro_sms --module edupro_sms.edupro_sms.doctype.report_card.test_report_card`
(needs `bench set-config allow_tests true` once per site first).

| ID | Description | Expected Result | Status |
|---|---|---|---|
| TC-01 | Teacher enters marks for many students | All marks saved, no data loss | ✅ pass (5-student batch; scales linearly, see `docs/08` §8.3 for a 20-student timing run) |
| TC-02 | Teacher submits marks with missing data | System blocks submission, shows warning | ✅ pass — `generate_report_cards` skips the student and reports it by name, doesn't silently create a partial report |
| TC-03 | Headmaster approves a class | Workflow advances, record locks | ✅ pass — verified `UpdateAfterSubmitError` on a post-Approve edit attempt |
| TC-04 | Headmaster rejects a class | Goes back to Pending Approval, stays editable | ✅ pass |
| TC-05 | Guardian with 3 children | Sees all 3 (once Published) | ✅ pass |
| TC-06 | Student portal login | Only sees own report | ✅ pass — both positive and negative (`has_permission` False on another student's report) |
| TC-07 | PDF generation timing | < 5 sec/student | ✅ pass — 3-student in-test batch; see `docs/08` §8.3 for the larger 20-student benchmark (0.37s/student) |
| TC-08 | Email parents | All sent, delivery status logged | ⏭️ skips cleanly with no outgoing Email Account configured (expected on a fresh site — passes once one exists, verified manually in Sprint 7 with a placeholder account) |
| TC-09 | Duplicate prevention | Blocked (same student+plan) | ✅ pass — Education's own `validate_duplicate` |
| TC-10 | Grade calculation | Matches IGCSE boundaries exactly at every threshold | ✅ pass — tested at and just below each boundary (89.99% ≠ A*, etc.) |
| TC-11 | Position calculation | Correct ranking, ties share a rank | ✅ pass — 2 tied at 1st, next distinct rank correctly skips to 3rd |
| TC-12 | Historical term view | Previous term's data stays intact and queryable | ✅ pass |

**Real constraint found while writing these (see `.claude/DECISIONS.md`
0008/0009):** `Student Group.academic_term` locks every Assessment Plan
under that group to one term — testing "the same class across two terms"
needs two Student Group records, not one. This is also true for real
usage, not just tests — a school modeling multiple terms for one physical
class needs a new Student Group per term (or Sprint 8+ follow-up work to
reconsider this binding).

## 7.3 Test Data

- Use fixtures/factory helpers for common records (Academic Year, Class,
  Student) rather than duplicating setup per test.
- Keep test data clearly separate from any real pilot-school data.

## 7.4 User Acceptance Testing (Sprint 8)

Full path: create academic year/term → set up classes/subjects → enroll
students → enter marks → submit → Class Teacher review → Headmaster
approve → publish → generate report cards → email parents →
student/parent portal view.

**This path has already been exercised end-to-end with real (sample)
data across Sprints 3–8** — see `.claude/CHANGELOG.md` for each sprint's
verification. What follows is the checklist for a human to actually
click through in a browser before pilot-school go-live — everything
below has been verified *programmatically* (via `bench console` and raw
HTTP requests with `curl`), but not through an actual browser UI, which
can surface UX issues (confusing labels, broken CSS, awkward flows) that
API-level testing can't catch.

### Checklist

- [ ] **Admin**: log into Desk (http://localhost:8080), fill in real
      `School Settings` (currently has placeholder data only)
- [ ] **Admin**: create a real Academic Year + 3 Terms for the actual
      pilot school's calendar
- [ ] **Admin**: create real Student Groups (classes), Programs
      (streams), Courses (subjects) — replacing the sample "Form 4A"/
      "IGCSE Science" data
- [ ] **Admin**: create real Instructor, Guardian, Student records (or
      import), set each Student Group's `class_teacher`
- [ ] **Teacher**: log into Desk with a Teacher-role account, open an
      Assessment Result, enter Test/Exam scores, submit — confirm the UI
      is usable without prior explanation (this is the "learn in under
      15 minutes" success metric from `docs/01` §1.5)
- [ ] **Headmaster**: run `generate_report_cards` (currently no Desk
      button — see `TASKS.md` Sprint 8 gaps — call via
      Desk's "Execute" / bench console for now)
- [ ] **Class Teacher**: review a Report Card in Desk, add a comment,
      click "Review"
- [ ] **Headmaster**: approve a Report Card in Desk (add comment, click
      "Approve"), confirm it locks; try rejecting a different one and
      confirm the rejection reason is visible and it can be resubmitted
- [ ] **Headmaster**: click "Publish", confirm the report becomes
      visible on the portal and (with real SMTP configured, `docs/06`
      §6.6) that an email actually arrives
- [ ] **Student**: log into `/my-reports` in an actual browser, view and
      print/download the report card
- [ ] **Guardian**: log into `/my-reports` with an account linked to 2+
      children, confirm both show correctly
- [ ] **Visual/UX pass**: check the `IGCSE Report Card` print format
      renders cleanly (fonts, spacing, page breaks) when actually printed
      or saved as PDF from a browser, not just via the CLI PDF pipeline
- [ ] **Headmaster dashboard**: open "Report Card Status by Class" from
      the Desk report list, confirm it's discoverable and readable to
      someone who hasn't seen it before

## 7.5 CI

Not yet set up. TBD once the repo is on a Git host with CI available.
