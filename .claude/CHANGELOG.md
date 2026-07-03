# Changelog — Edupro SMS

All notable changes to this project are documented here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/); dates in
YYYY-MM-DD.

## [Unreleased]

### Added

- Project documentation scaffolding: `.claude/CLAUDE.md`,
  `PROJECT_CONTEXT.md`, `TASKS.md`, `DECISIONS.md`, `CODING_STANDARDS.md`,
  `CHANGELOG.md`, and `docs/01`–`10` skeletons.
- Ingested full IGCSE functional specification (roles, data model, IGCSE
  grading, approval workflow, print/email specs, testing, deployment) into
  `docs/01`–`11`, replacing the earlier generic skeletons with real specs.
  `docs/` is now the technical source of truth per module; `.claude/`
  updated to point into it rather than duplicate content.
- Added `docs/11_Roles_And_Permissions.md` (new — role capability matrix,
  not in the original 10-file skeleton).
- Logged two open architecture decisions in `DECISIONS.md`: 0004
  (multi-tenancy via site-per-school, not shared `School` table — default
  recommendation, pending owner confirmation) and 0005 (evaluate reusing
  Frappe's Education app before building DocTypes from scratch — open,
  decide before Sprint 2).
- Updated MVP scope, role list (added Class Teacher), and sprint plan in
  `PROJECT_CONTEXT.md`/`TASKS.md` to match the ingested spec.
- Resolved both open decisions: 0004 (site-per-school multi-tenancy)
  accepted; 0005 (Frappe Education app) accepted as "spike first in
  Sprint 1, then decide build path" — see `DECISIONS.md`.
- Stood up the local Frappe environment (`DECISIONS.md` 0006): custom
  Docker image `edupro-sms:v15` with Frappe 15.113.4, ERPNext 15.115.0,
  Education 15.5.3, Python 3.11.15; site `edupro.localhost` running at
  http://localhost:8080 with developer mode on. `frappe_docker/` lives at
  the project root (gitignored), not the originally-planned `docker/`
  subfolder. Fixed two build blockers along the way: Education app has no
  plain `version-15` branch (used `version-15.2`), and frappe_docker's
  shell scripts needed CRLF→LF conversion after a Windows git checkout.
- Fixed `.gitignore`: it had been saved in UTF-16 (PowerShell `Out-File`
  default encoding) instead of UTF-8, so none of its patterns were
  actually being applied — git was about to track the entire vendored
  `frappe_docker` clone. Rewritten in plain UTF-8.
- Created the `edupro_sms` custom app and installed it on `edupro.localhost`
  (v0.0.1). Caught and fixed a persistence bug right after creating it:
  `bench new-app` run inside the container writes to the container's
  writable layer, which isn't backed by any volume for `apps/` — a
  `docker compose down` would have deleted it. Copied the app out to
  `apps/edupro_sms/` on the host and added a bind-mount override
  (`frappe_docker/overrides.local/compose.edupro-sms-app.yaml`) so it's
  now live-edited from the host and safe across container recreation. See
  `DECISIONS.md` 0006.
- Ran the Education-app spike (0005) and resolved it: **extend the
  Education app** rather than build DocTypes from scratch (`DECISIONS.md`
  0007). Education already implements ~70% of the planned MVP data model
  (Academic Year/Term, Grading Scale ≈ Grade Boundary, Guardian, Instructor,
  Student Group ≈ Class, Course ≈ Subject, Program Enrollment, Assessment
  Plan/Result ≈ Assessment/Marks). Rewrote `docs/03_DocTypes.md` around
  this mapping, updated `docs/04_Workflows.md` and `docs/05_Print_Formats.md`
  to reference `Assessment Result` instead of a bespoke Marks doctype, and
  rewrote `TASKS.md` Sprints 2–6 — most of that work is now
  "configure/seed existing DocTypes," with real new build concentrated in
  Sprint 6 (approval workflow, comments, class position, our report card
  print format).
- Fixed a second, deeper persistence bug found while setting up Sprint 2:
  the bench Python virtualenv (`env/`) is baked into the image and **not
  shared between containers** — each of backend/queue-short/queue-long/
  scheduler/configurator gets its own independent copy, so installing
  `edupro_sms` into one didn't make it importable in another. A normal
  `docker compose down && up -d` (not just `--force-recreate`) would have
  silently broken the app. Fixed with a shared named volume `bench-env`
  plus a `configurator` command that reinstalls `edupro_sms` into it on
  every startup. Verified across two full restart cycles. See
  `DECISIONS.md` 0006 and `docs/08_Deployment.md` §8.1.
- **Sprint 2 complete:** created `Headmaster` and `Class Teacher` roles
  (fixtures), created the `School Settings` Single DocType, seeded
  `Grading Scale` "IGCSE Standard" with the 7 IGCSE grade intervals
  (fixture), and confirmed `Academic Year`/`Academic Term` fit the IGCSE
  3-term structure with no gaps. See `TASKS.md` Sprint 2.
- **Sprint 3 complete:** decided Stream = separate `Program` per stream,
  not a Custom Field (`Program.courses` already models per-stream subject
  lists). Corrected `docs/03_DocTypes.md`: Test/Exam weighting is natively
  per-Course (`Course.assessment_criteria`), not only per-Assessment-Plan
  as first assumed. Seeded starter data (sample, not fixtures — real
  pilot-school data replaces this during onboarding): 6 Courses with real
  Cambridge IGCSE codes, Academic Year 2026 + 3 terms, Programs "IGCSE
  Science"/"IGCSE Commerce", Student Groups "Form 4A"/"Form 4B". See
  `TASKS.md` Sprint 3.
- **Sprint 4 complete:** added `Student Group.class_teacher` Custom Field
  (Link → Instructor, fixture, committed to `edupro_sms`) since Education
  has no native lead-teacher concept on a class. Seeded starter data
  (sample, not fixtures): 2 Instructors (set as class teachers for Form
  4A/4B), 3 Guardians, 4 Students enrolled via Program Enrollment.
  Verified the Student↔Guardian reverse-sync works automatically (linking
  a guardian on a Student auto-populates that Guardian's own `students`
  child table) and that one guardian can correctly link to multiple
  children. See `TASKS.md` Sprint 4.
- **Sprint 5 complete:** discovered `Assessment Plan` models a literal
  scheduled exam session and blocks overlapping time slots for the same
  Student Group — staggered sample plan dates to work around it (a real
  constraint worth knowing before Sprint 6's workflow design). Corrected
  `docs/03_DocTypes.md`: Assessment Plan criteria use raw `maximum_score`
  points, not the `weightage` percent Course uses. Added `Assessment
  Result.special_case` Custom Field (fixture, committed). Confirmed
  grade/total auto-calculation works natively with zero custom code —
  verified against both the controller source and a live test record
  (35+52=87/100 → grade A). See `TASKS.md` Sprint 5.
- **Sprint 6 complete — first sprint with real new `edupro_sms` logic.**
  Pivoted from the original plan (workflow on `Assessment Result`) to a
  new `Report Card` DocType (one per Student+Term), confirmed with the
  owner first (`DECISIONS.md` 0008) — `class_teacher_comment`/
  `headmaster_comment` are per-student, not per-subject, so the workflow
  needed to live above the subject level. Built: `Report Card` +
  `Report Card Assessment Result` child table, `generate_report_cards()`
  with class position (standard competition ranking), the "Report Card
  Approval" Workflow (Pending Approval → Reviewed → Approved/Rejected →
  Published, with real docstatus locking), and the `IGCSE Report Card`
  Print Format. All verified end-to-end: two students generated and
  correctly ranked, one walked through all four workflow transitions,
  locking confirmed via a real blocked edit attempt, and a real PDF
  generated (saved to `exports/sample_report_card_kwabena_owusu.pdf`).
  Hit and fixed five real Frappe gotchas along the way (Workflow
  State/Action master records, `allow_on_submit` for docstatus=1→1
  transitions, a silent `fetch_from` chain that zeroed out
  `academic_term` on all Sprint 5 Assessment Plans, PDF generation
  needing a container-reachable `host_name`, and `frappe.get_single`
  being blocked in the print format sandbox) — all documented in
  `DECISIONS.md` 0008 so they aren't rediscovered.
- **Sprint 7 complete: portals and parent email.** Added row-level
  permission scoping on `Report Card` (`get_permission_query_conditions`
  + `has_permission`) — Class Teacher sees only their own classes,
  Student/Guardian see only their own/their children's *Published*
  reports, unmatched roles fail closed. Built a `/my-reports` portal page
  (`edupro_sms/www/my-reports/`) grouping reports per child for
  guardians. Built parent email delivery (`notify.py`) — HTML template,
  PDF attached, background job, auto-triggered on Publish. Verified
  everything over real HTTP with cookie-based login, including negative
  cases (a cross-student print attempt correctly returns 403). Verified
  the email pipeline's content is correct (recipient, subject, body,
  attachment) via a placeholder Email Account, then removed it — real
  SMTP is a deployment-time task. Hit a real gotcha: gunicorn workers
  cache imported Python modules, so `bench clear-cache` doesn't pick up
  controller code changes — a code fix was invisible over HTTP until the
  containers were actually restarted. Documented as a standing workflow
  step in `docs/08_Deployment.md` §8.1 and `DECISIONS.md` 0009.
- **Sprint 8 complete — MVP feature-complete on sample data, all 9
  planned sprints (0–8) done.** Added `test_report_card.py`
  (`FrappeTestCase`, all 12 required scenarios from `docs/07_Testing.md`,
  12/12 pass), a "Report Card Status by Class" Script Report for the
  Headmaster dashboard, a performance spot-check at 20-student scale
  (0.37s/student PDF generation vs. a 5s target — ~13× headroom), and a
  real UAT checklist (`docs/07_Testing.md` §7.4) for a human browser
  pass. Recorded full MVP readiness status in `docs/08_Deployment.md`
  §8.5. Found two more gotchas of the same "looks fine, isn't" pattern as
  earlier sprints: `FrappeTestCase` doesn't fully isolate data between
  test *methods* within one run (ranking-sensitive tests need their own
  isolated Student Group), and `frappe.db.rollback()` doesn't reliably
  undo a script's changes once any document has been submitted — a
  performance-check script left real leftover data despite an explicit
  rollback call, caught by verifying with count queries rather than
  trusting it, then cleaned up explicitly. Both documented in
  `DECISIONS.md` 0010.
- Set up working logins for all 7 sample portal accounts (`docs/08` §8.1
  "Sample portal accounts") and cleaned up 20 leftover ghost `User`
  accounts the earlier performance-check script's cleanup had missed
  (Student creation auto-provisions a User that `frappe.delete_doc`
  doesn't cascade-delete). Fixed `user_type` on all real portal accounts
  from the default `System User` to `Website User` — cosmetic for
  permissions (role-based) but fixes the post-login redirect landing on
  a failing Desk permission check instead of the portal.
- Fixed the ERPNext Setup Wizard blocking Desk (`setup-wizard/0`,
  `AttributeError: 'NoneType' object has no attribute 'replace'` on
  submit — a missing "Country" field in ERPNext's fixture installer).
  Not a bug worth fixing upstream: Edupro SMS deliberately doesn't use
  ERPNext's Company setup at all (`docs/02_Database.md` §2.2,
  `DECISIONS.md` 0004). Took three attempts to actually kill it — the
  first two (`System Settings.setup_complete`, then the real
  `Installed Application.is_setup_complete` flag + a placeholder
  Company record) fixed *navigation* but missed a save-triggered
  redirect loop entirely. The actual root cause: a stray
  `desktop:home_page` default value literally set to `"setup-wizard"`,
  found by grepping a HAR export's raw boot JSON (not the bundled JS
  source, which had misleadingly similar field-name matches). Fixed
  with `frappe.db.set_default("desktop:home_page", "Workspaces")`, plus
  added a `boot_session` hook (`edupro_sms/edupro_sms/boot.py`) as
  defense-in-depth. Confirmed by the owner in-browser, testing the
  exact reported action (Save), not just page navigation. Full,
  undiluted three-attempt story in `DECISIONS.md` 0011 — worth reading
  as a lesson in not declaring a browser-side bug fixed from
  terminal-only verification.
- Post-MVP feature/bugfix batch — a 9-item punch list from real pilot
  usage. All 9 verified via real HTTP logins simulating each affected
  role, not just permission unit checks (see `DECISIONS.md` 0011 for why
  that bar exists):
  1. **Multi-class teacher dashboard** — the "My Classes" report
     (`edupro_sms/edupro_sms/report/my_classes/`, Sprint 8) already
     handled an Instructor teaching several Student Groups generically;
     verified for real by assigning Kwame Boateng to a second class
     (Form 4A, in addition to his existing Form 4B) and confirming all 8
     Assessment Plan rows across both classes appear on his dashboard.
  2. **Login page branding** — new `edupro_sms/edupro_sms/branding.py`,
     an `on_update` doc event on `School Settings` that syncs
     `Website Settings.app_name`/`app_logo`/`copyright` (Frappe's login
     page reads these directly — no core template override needed) and
     flips the school logo file to public (a private file 404s for the
     Guest user viewing `/login`). Runs on every `School Settings` save,
     so it's reproducible per-school across future site installs, not a
     one-off manual fix.
  3. **Headmaster full visibility** — confirmed no permission
     restriction exists for Headmaster on Student/Instructor/Student
     Group (sees all 4 students, both instructors, both classes; done in
     Sprint/task 13, re-verified here).
  4. **Teachers can enter/edit marks** — `create`/`write` = `True` on
     Assessment Result for both Instructors confirmed at the doctype
     level; per-class doc-level scoping already proven in task 15
     (`teacher_permissions.py`).
  5. **Student Grades tab was empty** — root cause was students/guardians
     landing on Frappe Education's own built-in `edu-portal`, which
     Edupro SMS doesn't control or populate; not a marks/report-card bug.
     Fixed in task 17 by redirecting Student/Guardian home page to
     `/my-reports` instead. Verified both branches here: a student with
     a Published Report Card sees it (grade, %, Published badge); a
     student with none sees a clean "No report cards available yet"
     message, not a blank page.
  6. **No teacher logins existed** — fixed in task 14 (added
     `Instructor.user` custom field, created accounts); re-verified with
     a real HTTP login as Kwame Boateng.
  7. **Student portal menu showed Attendance/Schedule** — moot once
     `/my-reports` fully replaces `edu-portal` navigation (task 17); the
     new page only ever renders Grades/Profile/Fees. Confirmed no
     Attendance/Schedule string appears anywhere in the rendered page or
     in `Portal Menu Item`.
  8. **Student profile (class, subjects, parent email)** — new Profile
     tab on `/my-reports`
     (`www/my-reports/index.py`/`index.html`): for a Student, their own
     class/subjects/guardian emails; for a Guardian, one block per linked
     child. Verified for both roles, including a Guardian with two
     children in different classes.
  9. **Headmaster dashboard not visible** — root cause: no Headmaster
     user account existed at all (fixed in task 13, along with a
     `headmaster@example.edupro.test` login and the "Edupro SMS"
     Workspace with dashboard shortcuts). Re-verified the workspace loads
     and renders its Report Card Status/My Classes/Student Group/
     Instructor/School Settings shortcuts.
  Also added, incidental to item 8: a **Fees tab placeholder** ("coming
  soon") on `/my-reports`, since fee tracking isn't built yet — deferred
  to a future `edupro_finance` app per MVP scope, not silently dropped
  from the student menu.
- **Website dashboard for Headmaster/Instructor, logo on report cards**
  — two follow-up requests after the pilot feedback batch:
  1. Headmaster and Instructor now land on a new `/dashboard` website
     page after login instead of Desk (`www/dashboard/`) — a school-wide
     overview (student/teacher/class counts, Report Card status
     breakdown) for Headmaster, assigned classes + marks-entry progress
     for Instructor (reuses the My Classes report's row logic rather
     than duplicating it). They keep full Desk access for actual work
     (marks entry, report card approval) per an explicit scope decision
     — see `DECISIONS.md` 0013 for why this needed
     `add_to_apps_screen` + a `User.validate` hook rather than the
     `role_home_page` hook already used for Student/Guardian (that hook
     only applies to Website Users; Headmaster/Instructor stay System
     Users on purpose). Fixed a side effect this caused for
     Administrator/other System Managers (landed on the `/apps` picker
     instead of Desk) via `System Settings.default_app`.
  2. School logo added to the `IGCSE Report Card` print format header,
     verified against a real wkhtmltopdf-generated PDF (not just the
     HTML preview) — reuses the same public logo file the login page
     branding already relies on.

---

## 2026-07-03

### Added

- Initial project scaffolding decided: Frappe Framework, Docker-on-Windows
  dev environment, custom app `edupro_sms`. See `DECISIONS.md` 0001–0003.
