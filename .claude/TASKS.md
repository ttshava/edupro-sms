# Tasks — Edupro SMS

Sprints follow the module build order, updated to reflect the full IGCSE
functional spec (see `docs/`). Check items off as they're completed;
update `CHANGELOG.md` when a sprint's work ships.

## Sprint 0 — Documentation & Environment Scaffolding

- [x] Create `.claude/` documentation set
- [x] Ingest full functional spec into `docs/01`–`11`
- [x] Decide `.claude/DECISIONS.md` 0004 (site-per-school, accepted) and
      0005 (spike first in Sprint 1, accepted)
- [ ] Install Docker Desktop, VS Code, Git, Claude Desktop

## Sprint 1 — Project Setup

- [x] Install Frappe v15 via Docker (`frappe_docker/` at project root —
      see `docs/08_Deployment.md` §8.1 and `DECISIONS.md` 0006)
- [x] Configure site (`edupro.localhost`, one site = one school, per 0004)
      with ERPNext v15 + Education v15.2 installed, Python 3.11.15
- [x] Create custom app `edupro_sms`, installed on the site, source lives
      at `apps/edupro_sms/` on the host (bind-mounted, own git repo —
      see `DECISIONS.md` 0006 addendum)
- [x] Configure Git (project repo already existed; `edupro_sms` has its
      own repo with an initial `bench new-app` commit)
- [x] Spike: install/inspect Frappe's Education app, evaluate options
      (a) build fresh (b) extend Education app (c) cherry-pick — outcome
      recorded as `DECISIONS.md` 0007: **extend the Education app**.
      Sprints 2–6 below are rewritten to match (2026-07-03) — they used to
      plan a from-scratch data model; most of that already exists in
      Education (`Academic Year`, `Academic Term`, `Student Group`,
      `Course`, `Instructor`, `Guardian`, `Grading Scale`, `Assessment
      Plan`/`Assessment Result`). See `docs/03_DocTypes.md` for the full
      mapping.

## Sprint 2 — Roles & School Settings ✅ done 2026-07-03

- [x] Roles: `Headmaster` and `Class Teacher` created (desk_access=1,
      exported as fixtures in `edupro_sms/fixtures/role.json`).
      `Instructor`/`Student`/`Guardian`/`System Manager`/`Academics User`
      already existed from Frappe/Education — confirmed via
      `frappe.client.get_list`, not assumed. Permission scoping (Class
      Teacher → own class only) deferred to Sprint 6, when the workflow
      needs it.
- [x] `School Settings` Single DocType created in `edupro_sms` (fields:
      school_name, school_code, phone, email, address, motto, logo,
      curriculum, timezone, status). Permissions: System Manager (CRUD),
      Headmaster (read). Not yet populated with real pilot-school data —
      do that once the pilot school is confirmed.
- [x] Seeded `Grading Scale` "IGCSE Standard" with the 7 IGCSE intervals
      (A*–F), exported as a fixture (`edupro_sms/fixtures/grading_scale.json`)
- [x] Confirmed `Academic Year` (name/start/end) and `Academic Term`
      (linked to Academic Year, freeform name/title/dates) have no
      hardcoded term-count constraint — fit IGCSE's 3-term structure as
      created data (3x Academic Term per Academic Year), no gaps. Only
      known gap: no `marks_entry_deadline` field — deferred to Sprint 6
      as a Custom Field when the workflow needs to enforce it.

## Sprint 3 — Academic Structure (via Education DocTypes) ✅ done 2026-07-03

- [x] Stream decision: separate `Program` per stream (not a Custom
      Field) — `Program.courses` already models "which subjects this
      track takes." See `docs/03_DocTypes.md`.
- [x] Correction: Test/Exam weighting is natively per-Course
      (`Course.assessment_criteria`), not only per-Assessment-Plan as
      originally assumed — `docs/03_DocTypes.md` updated.
- [x] Seeded starter data (sample/starter, not fixtures — school-specific,
      replace with real pilot-school data during onboarding):
      `Assessment Criteria` (Test, Exam); 6 `Course` records with real
      Cambridge IGCSE codes (Mathematics 0580, English 0500, Physics
      0625, Chemistry 0620, Biology 0610, Economics 0455), each with
      Test 40%/Exam 60% and `default_grading_scale = IGCSE Standard`;
      `Academic Year` "2026" + 3 `Academic Term`s; `Program`s "IGCSE
      Science" and "IGCSE Commerce" with their course lists; `Student
      Group`s "Form 4A" (Science) and "Form 4B" (Commerce)
- [ ] `Program Enrollment` + `Program Enrollment Course` (subject
      allocation) — deferred to Sprint 4, needs actual Student records
      to enroll first

## Sprint 4 — People (via Education DocTypes) ✅ done 2026-07-03

- [x] Class Teacher designation: Education's `Student Group Instructor`
      child table has no lead/primary flag, so added a Custom Field
      `Student Group.class_teacher` (Link → Instructor) — the correct way
      to extend a DocType we don't own. Exported as a fixture
      (`edupro_sms/fixtures/custom_field.json`). Committed to `edupro_sms`.
- [x] Sample `Instructor` records (Grace Mensah → Form 4A class teacher,
      Kwame Boateng → Form 4B class teacher) — starter data, not fixtures.
- [x] Sample `Guardian` + `Student Guardian` linking — confirmed the
      reverse sync works automatically (populating `Student.guardians`
      auto-populates the linked `Guardian.students` child table too,
      verified directly against the DB). One guardian (Ama Owusu) deliberately
      linked to two students to prove the multi-child scenario.
- [x] Sample `Student` + `Program Enrollment` records: 4 students (2 per
      class), each enrolled in their Program with courses copied from the
      Program's course list, and added to their Student Group.

All Sprint 4 people data is starter/sample (clearly fictional, fake
`@example.edupro.test` emails) — replace with real pilot-school people
during onboarding, same caveat as Sprint 3's academic structure data.

## Sprint 5 — Assessments & Marks (via Education DocTypes) ✅ done 2026-07-03

- [x] Discovered a real constraint: `Assessment Plan` models a literal
      scheduled exam session — Education blocks overlapping time slots
      for the same Student Group, so each subject within a class needs
      its own date/time (different groups can safely reuse slots).
      Staggered sample plans across 2026-04-01 through 04-05.
- [x] Created 8 `Assessment Plan`s (Term 1, Form 4A ×5 subjects, Form 4B
      ×3 subjects) with Test (max 40) + Exam (max 60) as two `Assessment
      Plan Criteria` rows, total normalized to 100 for clean percentages
      — starter data, not fixtures.
- [x] Confirmed `Assessment Result` entry flow works as-is: created one
      demo result (Kwabena Owusu, Mathematics, Test 35 + Exam 52) and
      verified auto-calculation — total 87/100, grade **A** (matches the
      80–89 IGCSE band exactly). No custom calculation code needed;
      confirmed via the controller source
      (`assessment_result.py` `validate_grade()`), not just assumed.
- [x] `special_case` Custom Field (Absent/Exempt/Medical Withdrawal) added
      to `Assessment Result`, exported as a fixture, committed.

## Sprint 6 — Approval Workflow & Reporting (custom `edupro_sms` build) ✅ done 2026-07-03

This was the sprint with real new work — everything before it was
largely configuring Education's existing DocTypes. Design pivoted from
the original plan: workflow lives on a new `Report Card` DocType, not on
`Assessment Result` — see `.claude/DECISIONS.md` 0008 for why, confirmed
with the owner before building.

- [x] `Report Card` DocType (submittable, one per Student+Term) +
      `Report Card Assessment Result` child table, committed to `edupro_sms`
- [x] `generate_report_cards(student_group, academic_term)` — aggregates
      submitted Assessment Results, skips+reports students missing
      required courses rather than generating partial reports
- [x] Class position calculation (standard competition ranking, ties
      share a rank) — verified with 2 students, correct 1st/2nd ranking
- [x] `class_teacher_comment`, `headmaster_comment`, `rejection_reason`
      fields on Report Card (not Assessment Result — see 0008)
- [x] "Report Card Approval" Workflow: Pending Approval → Reviewed →
      Approved/Rejected → Published, `doc_status` mapped so
      Approved/Published are real locked/submitted records — verified
      end-to-end (all 4 transitions) plus locking (`UpdateAfterSubmitError`
      on a post-Publish edit attempt)
- [x] `IGCSE Report Card` Print Format — built, generates a real PDF
      (verified, saved a sample at `exports/sample_report_card_kwabena_owusu.pdf`)
- [x] PDF generation — working via `frappe.get_print` + `get_pdf`;
      needed a `host_name` fix for container-internal asset resolution
      (`.claude/DECISIONS.md` 0008)

**Not yet built (carried to later sprints):** a Desk UI trigger button
for `generate_report_cards` (currently console/API only — Sprint 8
polish); background-job wrapping for bulk generation
(`docs/05_Print_Formats.md` §5.3); `special_case` effects on totals
(Absent/Exempt/Medical Withdrawal don't yet change the calculation,
`docs/04_Workflows.md` §4.3); admission number/DOB/gender on the print
format's student details block.

## Sprint 7 — Portals & Communication ✅ done 2026-07-03

- [x] Permission scoping on `Report Card` (blocking prerequisite, not
      originally its own line item — see `.claude/DECISIONS.md` 0009):
      Class Teacher/Student/Guardian row-level access, fails closed for
      unmatched roles. Verified over real HTTP with positive AND
      negative test cases.
- [x] Student portal: view own report card — `/my-reports`
      (`edupro_sms/www/my-reports/`)
- [x] Parent (Guardian) portal: view all linked children, grouped per
      child on the same page — verified with a guardian linked to two
      students
- [x] Print function (portal) — permission-checked print/download link
      per report; Desk-side print already worked natively via the
      standard Frappe print view once the `IGCSE Report Card` format
      existed (Sprint 6), nothing extra needed there
- [x] Email Queue & Parent Emailing — `notify.py`, HTML template per
      `docs/06_Email_System.md`, PDF attached, enqueued via
      `frappe.enqueue`, auto-triggered on the Publish transition
      (`on_update_after_submit`)
- [x] Delivery status logging — `sent_to_parent_at` set on success;
      failures caught per-guardian and logged via `frappe.log_error`
      (not silently dropped, not batch-crashing)

**Real gotcha hit:** gunicorn workers cache imported Python modules —
`bench clear-cache` doesn't restart them. A `.py` change was invisible
over HTTP until the containers were actually restarted. See
`.claude/DECISIONS.md` 0009 and `docs/08_Deployment.md` §8.1 — this is
now a standard step after any Python code change, not a one-off.

**Not yet built (carried forward):** friendlier Headmaster-facing
delivery report (vs. reading Error Log directly — Sprint 8 candidate);
real SMTP configuration (`docs/06_Email_System.md` §6.6 — deployment-time
task, pipeline itself is verified); a guardian "summary dashboard" view
distinct from the per-child list (current page covers the MVP need).

## Sprint 8 — Dashboards, Testing & MVP Release ✅ done 2026-07-03

- [x] Headmaster dashboard — "Report Card Status by Class" Script Report
      (per-class breakdown of not-generated/Pending/Reviewed/Approved/
      Rejected/Published), verified via the real Desk report-run API
- [x] Test scenarios TC-01–TC-12 automated and passing (12/12,
      `test_report_card.py`) — see `docs/07_Testing.md` §7.2
- [x] Performance check: 20-student synthetic batch, all metrics well
      within target (PDF: 0.37s/student vs 5s target; generation:
      12ms/student). Not load-tested at 200+ students or with concurrent
      users — flagged, not blocking, see `docs/08_Deployment.md` §8.3
- [x] UAT checklist written (`docs/07_Testing.md` §7.4) — the
      programmatic/HTTP-level path has been verified every sprint since
      Sprint 3; the checklist itself still needs a human to click
      through in a real browser before go-live
- [x] MVP release readiness recorded (`docs/08_Deployment.md` §8.5) —
      functionally complete on sample data; real pilot-school launch
      needs real data entry, real SMTP config, and the browser UAT pass,
      none of which are architectural gaps

**This closes the planned MVP sprints (0–8).** Remaining work before a
real pilot-school launch is deployment/data/config work, not further
`edupro_sms` feature development — see `docs/08_Deployment.md` §8.5 for
the full readiness breakdown and the Backlog below for genuinely
post-MVP feature work.

## Post-MVP fix batch — pilot feedback ✅ done 2026-07-03

Nine-item punch list from real pilot usage. See `CHANGELOG.md` 2026-07-03
for the full verification detail per item.

- [x] Multi-class teacher dashboard (verified with a real 2-class Instructor)
- [x] Login page branding synced from `School Settings`
      (`edupro_sms/edupro_sms/branding.py`)
- [x] Headmaster full visibility (students/teachers/classes) — re-verified
- [x] Teacher marks entry/edit permission — re-verified
- [x] Student Grades tab empty — root cause was `edu-portal`, not marks;
      fixed via `/my-reports` redirect (task 17)
- [x] Teacher logins — re-verified
- [x] Student portal menu Attendance/Schedule — moot after `/my-reports`
      replaces `edu-portal`; confirmed absent
- [x] Student profile tab (class, subjects, parent email) — new tab on
      `/my-reports`, verified for both Student and Guardian roles
- [x] Headmaster dashboard visibility — root cause was a missing
      Headmaster account (task 13); workspace shortcuts re-verified
- [x] Fees placeholder tab added (not silently dropped; fee tracking is
      genuinely post-MVP, see Backlog below)

## Follow-up: Headmaster/Teacher dashboard + report card logo ✅ done 2026-07-03

- [x] Headmaster and Instructor land on a new `/dashboard` website page
      after login instead of Desk (`www/dashboard/`), while keeping full
      Desk access for actual work (marks entry, approvals) — see
      `DECISIONS.md` 0013
- [x] School logo added to the `IGCSE Report Card` print format header,
      verified against a real generated PDF

## Independent QA pass ✅ done 2026-07-03

Full browser-based test of all 4 portal roles against a stated brief
("student/parent must view subjects+marks, print PDF, no Desk";
"teacher must enter marks on the website, no Desk"; "headmaster must
approve on the website, no Desk"). Report:
`exports/Edupro_SMS_QA_Report_2026-07-03.pdf`. Result: 10/16 criteria
passed outright, 2 partial, 4 failed. Student and Parent portals are
in good shape (two minor UX gaps). Teacher and Headmaster fail their
"no Desk" and "act entirely from the website" requirements — this is
**not a bug**, it's the direct, known consequence of Decision 0013
(deliberately kept Desk access for marks entry/approval instead of
building website equivalents). See Backlog below for the open items
this surfaced, and 0013 for why the conflict exists before "fixing" it.

## Backlog (post-MVP)

### 2026-07-03 QA pass — top 4 findings ✅ resolved same day

The scope conflict got resolved as option (b): built real website
replacements first, then removed Desk access — see `DECISIONS.md`
0014 for the full sequencing rationale and what was verified.

- [x] Teacher marks entry moved to the website (`/marks-entry?plan=X`)
- [x] Headmaster approve/reject/publish moved to the website
      (`/dashboard` Pending Approvals section)
- [x] Desk access removed for Teacher/Headmaster (now `Website User`,
      same as Student/Guardian) — done last, only after the two items
      above were built and verified as full replacements
- [x] Parent's child with no Report Card yet no longer disappears from
      the Grades tab — shows "No report card published yet" instead

### Remaining lower-priority items from that QA pass

- Student/Parent Grades tab shows only a per-term aggregate, not a
  per-subject mark breakdown — that detail currently only exists
  inside the printable report card.
- [x] ~~Login footer still reads "Powered by ERPNext"~~ — rebranded
      2026-07-03 (footer redesign, see Changelog)

## First real school data + Term 2 report cards end-to-end ✅ done 2026-07-03

- [x] Real subject-per-Program breakdown applied (Form 1-4 full
      O-Level offering; U6 streams get real A-Level subsets)
- [x] All 33 Form 1 Purple students imported from the real register
- [x] All 38 real teaching staff imported, assigned by subject
- [x] `Curriculum` DocType + `Program.curriculum` (Cambridge IGCSE /
      Cambridge AS Level) — School Settings' single curriculum field
      can't hold two curricula at once
- [x] Root-caused and fixed: Student/Guardian/Instructor/Headmaster/
      Class Teacher roles all ship with `desk_access=1`, silently
      re-flipping portal accounts to System User on every save — fixed
      at the role level, not per-account
- [x] Term 2 2026: 22 Assessment Plans created+activated, 726 marks
      entered via the real teacher workflow, 33 Report Cards generated
      and taken through Review → Approve → Publish on the real website
      UI, confirmed visible to a real student and parent
- [x] Every class has a real, distinct Class Teacher; Headmaster
      dashboard and student Profile tab updated to show it plus a
      presentable Subject/Teacher table
- [x] Frappe favicon replaced with the school's own
- [x] Term 2 rolled out to the other 14 classes with 2 Shona-named
      sample students each (61 students / 61 published report cards
      school-wide) — caught and fixed an unexplained Program subject
      count drop (Form 1: 22→7) mid-rollout, audited every class
      afterward to confirm nothing else was affected

## Marks/reporting refinements ✅ done 2026-07-04

- [x] Marks simplified to a single Exam out of 100 per subject
      (was Test/40 + Exam/60) — migrated all 288 Assessment Plans and
      1258 existing Assessment Result rows, no Report Card totals
      changed since 40+60 already summed to 100
- [x] My Reports Grades tab simplified to Term / Status
      (Published/Pending) / View/Print
- [x] QR authenticity code on the report card print format, linking to
      a public no-login `/verify-report-card` page (minimal info only)
- [x] Teacher dashboard reworked into a Subject → Class selector for
      teachers who teach the same subject across multiple classes

## Portal redesign: left-sidebar layout ✅ done 2026-07-03

- [x] Shared `edupro_sms/templates/portal_base.html` sidebar shell,
      adopted by `/my-reports`, `/dashboard`, `/marks-entry`
- [x] Student/Guardian Grades/Profile/Fees moved into sidebar nav
- [x] Headmaster sidebar links to anchored sections (Overview/Classes/
      Report Cards/Approvals) on the same dashboard page
- [x] Footer: dropped "Powered by", added +263 country code to helpdesk
      number

### MVP polish (small, non-blocking — do before or shortly after pilot launch)

- Desk UI button/page to trigger `generate_report_cards` (currently
  console/API only)
- Background-job wrapping (`frappe.enqueue`) for bulk PDF generation and
  email at real class scale (currently synchronous, fine at tested scale)
- `special_case` (Absent/Exempt/Medical Withdrawal) doesn't yet affect
  Report Card totals — field exists, calculation logic doesn't use it
- Friendlier Headmaster-facing email delivery report (vs. reading Error
  Log directly)
- Permission scoping beyond `Report Card` (School Settings, Academic
  Year/Term, Class/Subject, Student/Guardian currently use Role
  Permissions Manager defaults only — fine for MVP since only Report
  Card is portal-facing)
- Admission number/DOB/gender on the report card print format's student
  details block

### New apps and features (genuinely post-MVP)

- `edupro_finance` app
- `edupro_attendance` app
- `edupro_transport` app
- Native mobile apps, SMS integration, parent-teacher chat
- AI-powered recommendations
- Timetable generation, online exams
- Multi-school analytics/reporting across sites (only relevant if 0004 is
  revisited)
