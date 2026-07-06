# Changelog — Edupro SMS

All notable changes to this project are documented here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/); dates in
YYYY-MM-DD.

## [Unreleased]

### 2026-07-06 — End-to-end strain test, demo data, real SMTP live

- **Full end-to-end scenario test**, one real student threaded through
  every stage: Bursar creates student + guardian → enrolls in class →
  batch bills term fees → three teachers enter marks → Class Teacher
  reviews → Headmaster approves/publishes → PDF renders with QR code →
  student/guardian portals show correct data → partial payment recorded
  → fee statement shows correct running ledger balance. Found and fixed
  real bugs along the way (not simulated — same accounts/roles a real
  school would use):
  - `link_guardian()` never created a linked User for a newly-created
    guardian — guardians created via the Bursar portal had no way to
    ever log in. Fixed in `bursar_student_management.py`.
  - Education's own `Student.validate_user()` calls `User.add_roles("Student")`
    on a brand-new, not-yet-saved User doc — the role never actually
    persisted. Core Education code, can't edit directly; worked around
    with a new `after_insert` hook (`student_hooks.py`,
    `ensure_student_role`) wired in `hooks.py`.
  - `enroll_student()` accepted a `student_group` param but never wrote
    it anywhere real (`Program Enrollment` has no such field — silently
    ignored) — students were billed and marked but never actually on
    their class's roster. Fixed to write the real `Student Group
    Student` child-table row Education expects.
  - Sidebar "Log out" link was a plain `<a href="/api/method/logout">`
    — clicking it navigated straight to the API endpoint and showed raw
    JSON instead of logging out. Fixed in `portal_base.html` with a
    proper POST + redirect.
  - Batch billing's `%example.edupro.test` exclusion filter (meant to
    keep old QA fixtures out of real billing runs) would have silently
    skipped a real student who happened to share that email domain —
    not a bug in the filter itself, just a reminder real student data
    should never use that domain.
- **Demo dataset populated**: 85 students (5 per class) across all 17
  real classes (Form 1-6, all streams), each with a guardian, full
  enrollment, and a billed term fee — generated through the real Bursar
  API, not raw DB inserts. Surfaced two more real bugs: Frappe's core
  `throttle_user_creation()` (>60 Users/60s) needed the framework's own
  `frappe.flags.in_import` bypass, scoped tightly to just the
  User-creating calls (the flag also disables default-value population,
  which broke `Program Enrollment.enrollment_date` until scoped
  correctly); and full-name collisions across different classes broke
  on `Customer`'s auto-naming (keyed by full name) — fixed with a
  school-wide uniqueness check, not just per-class.
- **Real SMTP configured and verified live**: `First Class High
  Outgoing` (`mail.firstclasshigh.ac.zw:465`, SSL) — credentials entered
  directly in Desk, never handled by Claude or committed anywhere.
  `EMAIL_DELIVERY_ENABLED` flipped to `True` in `notify.py`. Verified
  with two real sends (plain SMTP test, and a full report-card-publish
  send with PDF attachment) — both confirmed `Sent` via `Email Queue`.
  Demo/sample guardian emails are not real mailboxes on that domain and
  will bounce (`550 No Such User Here`) if ever triggered — expected,
  not a bug.
- **Planned, not yet implemented**: per-student elective subject groups
  (e.g. Form 1's "pick one practical subject" alongside 7 fixed core
  subjects) — `Program Course` needs an `elective_group` field, and
  report-card/marks-entry logic needs to move from the Program's
  blanket required-course list to each student's own `Program
  Enrollment.courses`. Full plan agreed, awaiting go-ahead to build.

### 2026-07-05 — Phases 2-3 committed, shared portal design system, Bursar suite rebuilt

- **First real commit of `apps/edupro_sms`.** The entire custom app had been
  gitignored (`apps/*`) for this project's whole history — every feature
  below existed only in an uncommitted working tree or an unpushed nested
  git repo. Un-ignored `apps/edupro_sms` specifically and grafted its
  20+-commit standalone history into the main repo via `git subtree`
  (kept `frappe`/`erpnext`/`education` correctly excluded — those are
  vendored inside the Docker image, never on the host).
- **Phase 2 (Finance):** Student Fee / Student Ledger Entry doctypes,
  Billing Configuration, batch billing, fee entry portal, fee dashboard,
  batch report card printing.
- **Phase 3 (Portals + Analytics):** Student/Guardian portal APIs (grades,
  reports, fees, multi-child support), academic trend analytics, at-risk
  detection, grade predictions.
- **Shared portal design system.** `templates/portal_base.html` — the
  real, reusable shell (dark sidebar nav, pill status badges, stat-cards,
  buttons, expand-in-place detail rows) now used by Dashboard, Fees,
  Billing, Students, and Import Data instead of each page rolling its own
  inline Bootstrap styling. Documented in root `DESIGN.md`/`PRODUCT.md`.
- **Rebuilt Fees, Billing, Students, and Import Data on the shared shell**,
  fixing real schema-mismatch bugs discovered in every one of them along
  the way: `Student`/`Guardian` fields that don't exist (`admission_number`,
  `email`, `status`), `Academic Term`/`Academic Year` fields that don't
  exist (`is_active`, `is_current`), `Program Enrollment` used where the
  school's real billing model is flat rate by boarding type, an
  `ImplicitCommitError` from an unnecessary explicit `frappe.db.begin()`,
  `Gender` being a Link doctype (`Male`/`Female`) not `M`/`F`, and
  `first_name`/`last_name` being the real source of truth over
  `student_name` (Education's own `Student.set_title()` recomputes it).
- **CSV/Excel bulk import actually works now.** The upload step was never
  implemented (the browser read the file locally via `FileReader` but only
  ever sent the *filename* to the server — nothing was ever uploaded).
  Wired a real multipart upload to Frappe's `/api/method/upload_file`,
  resolved the returned `file_url` to a filesystem path before parsing,
  and fixed template downloads to actually stream a file (they previously
  returned a plain JSON dict with no download trigger).
- **Two core Education-app permission cascades fixed via fixtures, not
  core edits:** `Student.on_update()` calls `update_linked_customer()` →
  `Customer.save()` with no `ignore_permissions`; `Student.validate()`
  calls `User.add_roles()` → `User.save()`, also with no
  `ignore_permissions`, before the caller's own `ignore_permissions=True`
  save ever runs. Neither can be edited (core files) — granted Bursar
  `Customer` and `User` DocPerms in `hooks.py`'s fixtures instead.
- Verified live end-to-end, not just via code review: real fee payments,
  real batch billing (33 students, $28,250 billed), a real CSV student
  import exercising the full Student → Customer → User → Program
  Enrollment cascade, guardian linking, and program enrollment.

### Added

- Rebranded the teacher-facing `/dashboard` and `/marks-entry` website
  pages with the Edupro brand design system (red/gray palette, Inter font,
  pill buttons, elevated cards, small dense font sizes, inline SVG
  education icons replacing emoji). Scoped under a new `.edu-teacher`
  wrapper class in `dashboard/index.html` so the Headmaster branch of the
  same template is untouched; `marks-entry/index.html` is a single-role
  page so its whole `<style>` block was redone in place. Verified in
  browser with a disposable QA teacher account and a disposable QA
  headmaster account (both since deleted); headmaster dashboard confirmed
  unaffected. See `DECISIONS.md` 0020.

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
- **Independent QA report** (`exports/Edupro_SMS_QA_Report_2026-07-03.pdf`):
  full browser-based test of Student/Parent/Teacher/Headmaster against
  a stricter brief than the same-day Decision 0013 assumed — 10/16
  criteria passed outright, 2 partial, 4 failed. Teacher and Headmaster
  failed "act entirely from the website" and "no Desk access" because
  0013 had deliberately kept Desk for their real work.
- **Resolved the QA report's top 4 findings**, in dependency order:
  1. New `/marks-entry?plan=X` page — teacher marks entry entirely on
     the website. Reuses `Assessment Result.validate()` instead of
     reimplementing max-score/grade/duplicate checks; edits to an
     already-submitted mark go through a real cancel+amend+resubmit
     (required since the doctype is submittable with no
     `allow_on_submit` fields); skips re-amending unchanged rows.
     Cross-class permission denial verified (clean "Not Permitted",
     not a stack trace).
  2. New Pending Approvals section on the Headmaster's `/dashboard` —
     Approve/Reject/Publish buttons drive the existing Report Card
     Approval workflow via `frappe.model.workflow.apply_workflow`, the
     same call Desk's buttons make. Verified the full loop: marks
     entered on the website → report generated → approved and
     published from the website → visible as Published on the parent's
     `/my-reports`, no Desk step anywhere in the chain.
  3. **Desk access removed for Teacher/Headmaster** (`user_type` →
     `Website User`, same as Student/Guardian) — done last, only after
     1 and 2 were built and verified, since removing it first would
     have left both roles with no working tool. See `DECISIONS.md`
     0014 for the full sequencing rationale and a config detail that
     turned out not to need touching (the `add_to_apps_screen`/
     `default_app` redirect from 0013 worked unchanged after the flip).
  4. A guardian's child with no Report Card yet no longer disappears
     from the Grades tab — shows "No report card published yet"
     instead, matching what the Profile tab already displayed.
  Two lower-priority findings from the same report (per-subject marks
  not shown inline on Grades, "Powered by ERPNext" in the login footer)
  remain open in `TASKS.md` Backlog.
- **Portal redesign: shared left-sidebar layout.** New
  `edupro_sms/templates/portal_base.html`, extended by all three portal
  pages (`/my-reports`, `/dashboard`, `/marks-entry`) instead of
  `templates/web.html` directly — branded sidebar (school logo/name,
  role-based nav, user + logout) with consistent chrome across every
  role. Student/Guardian's Grades/Profile/Fees tabs moved from the top
  into the sidebar (same JS, no behavior change); Headmaster's sidebar
  links to anchored sections on the same dashboard page rather than
  separate routes. Also closes the last open footer item: dropped
  "Powered by" (logo + linked company name only) and added the +263
  country code to the helpdesk number.
  Two issues caught before calling this done: the new template was
  initially misplaced one directory too deep (surfaced immediately as
  `TemplateNotFound`, not a silent failure), and the teacher's 8-column
  My Classes table overflowed the narrower content pane with the
  sidebar in place, hiding the "Enter Marks" link off-screen — fixed
  with a `display:block`/`overflow-x:auto` rule so wide tables scroll
  within their own box instead of breaking the page layout.
- **First real school data loaded: subjects-per-class, students, staff.**
  Applied a real ZIMSEC/Cambridge subject-per-Program breakdown (Form
  1-4 get the full 22-subject O-Level offering; the three U6 streams
  get real A-Level-style subsets). Imported all 33 real Form 1 Purple
  students from the school's own register (`form 1 p.xlsx` — "p" =
  Purple) with real names/DOB/address/emergency-contact, and all 38
  real teaching staff from `staff.html` with real emails, assigned as
  Student Group Instructor across classes by subject. Added a
  `Curriculum` DocType + `Program.curriculum` link (Cambridge IGCSE for
  Form 1-4, Cambridge AS Level for the U6 streams), since
  `School Settings.curriculum` is a single whole-school field that
  can't hold two different curricula. Deleted the old sample data
  (Form 4A/4B, its students/marks/report cards) it replaced.
  Root-caused and fixed a real, recurring bug found along the way:
  Education's stock Student/Guardian/Instructor/Headmaster/Class
  Teacher roles all ship with `desk_access=1`, so Frappe's own User
  controller was silently re-flipping every portal account back to
  System User (with an extra "Desk User" role) on every save — not a
  one-off import glitch. Fixed at the role level
  (`desk_access=0`, added to the Role fixture export) instead of
  fighting it per-account. Also hit and fixed a second, unrelated bug:
  hard-deleting a User with an active session crashes the *entire
  site* for that session's cookie (`DoesNotExistError` on session
  resume) until the stale session is cleared from both the DB
  `tabSessions` table and Frappe's Redis session cache — happened twice
  (once from deleting the old sample headmaster, once from the earlier
  sample-student cleanup) before being fully swept.
- **Term 2 2026 report cards generated, approved, and made real for
  Form 1 Purple end-to-end.** Created and submitted 22 Term 2
  Assessment Plans (Exam/Test criteria, one subject per day starting
  2026-07-03, skipping weekends), entered marks for all 726
  student×subject combinations via the real `save_marks` teacher
  workflow (synthetic scores — no real Term 2 exam data exists yet),
  generated all 33 Report Cards, and walked them through
  Review → Approve → Publish using the real website workflow
  (re-verified the Approve/Publish buttons live in-browser, not just
  via script) — confirmed visible as Published to both a real student
  and a real parent. Every Form class now has a distinct real class
  teacher (`Student Group.class_teacher`), each granted the "Class
  Teacher" role for the Review step. Headmaster dashboard's "Teachers"
  column (a full comma-joined list) renamed to "Class Teacher" showing
  just the one homeroom teacher; Student/Guardian Profile tab's
  subjects moved from an unreadable comma-separated string to a proper
  Subject/Teacher table (sourced from each subject's most recent
  Assessment Plan.examiner, the one real persisted subject-to-teacher
  link in the data model) plus the student's Class Teacher.
  Also caught the same `fetch_from`-can-silently-zero-a-field gotcha
  already on record (`DECISIONS.md` 0006/0009): Assessment Plan's
  `academic_term` fetches from `Student Group.academic_term`, which was
  blank, so newly-created plans silently lost their term until the
  Student Group's term was set and the plans backfilled.
- **Replaced the Frappe favicon** with the school's own
  (`Website Settings.favicon`), uploaded as a public file.
- **Term 2 rolled out to the other 14 classes**, each with 2 sample
  students (real Shona name combinations, clearly `@example.edupro.test`
  to distinguish from the real `@firstclasshigh.ac.zw` Form 1 Purple
  roster) — same full cycle as Form 1 Purple: Assessment Plans
  created+activated, marks entered, Report Cards generated and taken
  through Review → Approve → Publish, all 15 classes now consistent
  (61 students, 61 published Term 2 report cards school-wide).
  Caught a real, unexplained data issue mid-rollout: the "Form 1"
  Program had silently dropped from 22 subjects to 7 sometime between
  the previous session and this one (root cause not identified —
  no Version log entries exist for Program, and nothing in this
  session's own scripts explains it) — Form 2/3/4 and both U6 Programs
  were unaffected. Restored the full subject list and redid Form 1
  Green/Blue's Term 2 data (safe to fully redo since it was fresh
  sample data from the same session), then audited every class's
  subject/plan/student/published-card counts against its Program to
  confirm nothing else was quietly wrong before calling this done.
  Also hit the same "new User comes out disabled" bug on this batch
  of 28 accounts (as seen on the earlier 38-teacher import) — same
  fix, explicit `enabled=1` + `update_password()`.
- **Marks simplified to a single Exam out of 100** per subject,
  replacing the Test(40)+Exam(60) split. Since 40+60 already summed to
  100, this was a clean consolidation, not a rescoring: migrated all
  288 Assessment Plans' criteria to one `Exam`/100 row and merged all
  1258 existing Assessment Result Detail rows (summing the old Test+Exam
  scores) directly via ORM inserts against the already-submitted
  (docstatus=1) documents — bypassing the normal cancel/amend dance,
  since this was a controlled internal migration, not a user edit.
  Verified a sample Report Card's total/average against a fresh
  recomputation from its Assessment Results: unchanged, as expected,
  since no total or maximum actually changed. `marks-entry` and the
  Assessment Result controller were already criteria-agnostic, so no
  application code changes were needed there.
- **Student/Guardian "My Reports" Grades tab simplified** to three
  columns — Term, Status (Published/Pending), View/Print — dropping
  Average/Grade/Position from the summary list (still available on the
  printed report card itself).
- **QR authenticity code added to the report card print format**
  (bottom-right, "Scan to verify"). Added a `verification_code` field
  to `Report Card` (random `secrets.token_hex(8)`, set the moment a
  card is first Published — deliberately not the predictable `RC-...`
  doc name, so the QR can't be used to enumerate other students'
  reports), a new public `/verify-report-card?code=...` page (no login
  required) showing only student name, class, term, overall grade, and
  average — full subject-by-subject marks stay behind the portal login.
  QR image is generated server-side (`qrcode` package, added as an
  app dependency) and exposed to the Jinja print format via a
  `hooks.py` `jinja.methods` entry. Backfilled verification codes for
  the 61 already-Published report cards, since the code is only set
  going forward by `on_update_after_submit`.
- **Teacher dashboard reworked from a flat table into a two-step
  Subject → Class selector** (`/dashboard`), for teachers who teach the
  same subject across several classes (e.g. Mathematics in Form 1
  Purple, Form 1 Blue, and Form 3 Green) or several subjects across
  several classes. Backend scoping already supported this correctly
  (`teacher_permissions._assigned_student_groups` returns every
  Student Group tied to the Instructor); this was purely a UI change,
  grouping the same permission-scoped rows by subject client-side.
  Verified against a real 13-class teacher (server-rendered the page
  under their identity without touching their password) and, for a
  real click-through, a disposable QA multi-class teacher account
  added to 3 real classes and fully removed again afterward.
- **Teacher dashboard and Enter Marks page substantially enriched**
  from a mockup the owner supplied, with two scoping calls made where
  the mockup implied more than the current architecture supports (the
  owner didn't respond to a clarifying question, so the recommended/
  lower-risk option was taken in both cases — see `DECISIONS.md` 0016):
  - `/dashboard` (teacher role) gained a real summary bar (Academic
    Year, Current Term — derived from whichever Academic Term's
    start/end dates bracket today — Assigned Subjects, Total Students,
    Marks Entered X/Y, Pending), and the Subject → Class step now
    renders a card grid (icon, student count, progress bar, colored
    Complete/Pending pill) instead of a plain table.
  - Added a real "Grade Boundaries" reference table on both
    `/dashboard` and `/marks-entry`, sourced live from the IGCSE
    Standard Grading Scale's own intervals/descriptions (not
    hardcoded), with a small cosmetic color-band mapping per grade.
  - `/marks-entry` gained a header info block (Class/Subject/
    Assessment Date/Status), a live client-side Grade column and
    green/red pass-fail input styling as marks are typed (computed
    from the same real grade boundaries), an Entered/Missing status
    per row, a summary bar (Entered X/Y, Average, Pass Rate) with a
    missing-marks warning, CSV export/import (round-trips via Student
    ID, not name, so re-uploading is reliable), a Print button, and a
    real grade-distribution bar chart computed from the marks already
    on screen.
  - **Not built, deliberately:** a fake notification bell (nothing
    real behind it), attendance-style "Mark all present/absent" bulk
    actions (wrong concept for a marks-only system), bulk grade-curve/
    ±N adjustment tools, a new Draft → Submit-for-Approval → Request-
    Revisions gate at the subject level (marks still submit directly
    on Save, feeding the existing Report Card → Headmaster approval
    flow unchanged), and a "Strong/Weak topic areas" analysis (no
    per-topic data exists to support that claim).
- **Parent/student "My Reports" page redesigned** with a new default
  "Overview" tab from an owner-supplied mockup, built from real data
  only (existing Grades/Profile/Fees tabs kept as-is):
  - Compact stat-chip strip (Academic Year, Current Term, Children/
    Class, Reports Available, New — unread badge that clears itself,
    see below) instead of large padded cards, per the "slick, space-
    saving" brief.
  - Guardian with 2+ children gets a clickable child-card grid
    (avatar initial, class, latest average, Active/Inactive) that
    jumps to that child's detail block; a Guardian with one child or
    a Student viewing themself skips straight to the detail block.
  - Per child: compact stat chips (Average/Grade/Position/Subjects/
    a derived 1-5 star rating), a Subject Performance table (Score/
    Grade/Pass-Fail/Teacher Comment), View/Print/Download (reusing
    the existing printview) and a new "Email to Parent" resend action.
  - Wired up `Report Card.viewed_by_parent_at` — a field that already
    existed but nothing ever set — so the "New Reports" badge behaves
    like a real notification indicator: it counts unviewed published
    reports, then marks them viewed the moment the Overview page
    shows them, clearing before the next visit.
  - Progress-over-terms panel only renders once 2+ published terms
    exist for a student; today that's every student (only Term 2 2026
    exists school-wide), so it shows an honest "not enough history
    yet" note rather than fabricating a trend.
  - **Not built, deliberately** (same reasoning as the teacher
    dashboard batch above — real subsystems the mockup implied but a
    "redesign" request doesn't justify building unprompted): self-
    service "Add Child", parent-teacher messaging, meeting/slot
    booking, a generic notifications/alerts feed, and email-preference
    toggles. See `DECISIONS.md` 0017.
  - **Root-caused and fixed a real pre-existing bug** while building
    the denser Subject Performance table: the shared portal shell's
    `.portal-main table { display: block; }` rule (added earlier to
    let wide tables scroll instead of breaking the layout) silently
    splits `<thead>` and `<tbody>` into two independent anonymous
    tables that size their columns separately — harmless on tables
    where every column happens to need similar width, but a 5-column
    table with very differently-sized content renders data visibly
    under the WRONG headers. Confirmed via `getBoundingClientRect()`
    on header vs. data cells before/after the fix. Replaced it with
    the standard pattern (a `.table-scroll` wrapper div added by a
    small script in `portal_base.html`, table itself left as a real
    `<table>`) — fixes every table across the whole portal, not just
    the new one.
- **Headmaster dashboard redesigned** from another owner-supplied
  mockup, same "build the real redesign, skip the implied subsystems"
  discipline as decisions 0016/0017 (full reasoning in `DECISIONS.md`
  0018):
  - Summary strip: Academic Year, Current Term, Classes, Teachers,
    Students, Reports Published X/Y, Pending Approval, and a real
    Overall Grade computed from every class's average — no fabricated
    term-over-term trend arrows (only one term of real data exists
    school-wide).
  - **Class Performance Overview** table: one row per class (teacher,
    students, average %, grade, Complete/In Progress/Pending status),
    with a client-side filter box and CSV export, each row linking
    into a new drill-down page.
  - New `/class-review?group=X` page: class stats (average, grade,
    pass rate, position among all classes this term), a real grade-
    distribution bar chart, and every student ranked by average with
    a link to their own published report.
  - **Report Approval Workflow** replaced the old flat per-student
    Pending Approvals table with a per-class rollup (X awaiting
    Approve, Y awaiting Publish) plus a new bulk
    `apply_class_report_card_action` (in `approvals.py`) that loops
    the *same* `apply_workflow` call already used for individual
    report cards over every card in a class currently in the right
    state — no new workflow/state machine, just a bulk wrapper around
    the existing one. Verified end-to-end on 2 sample-data report
    cards (temporarily rolled back to Reviewed, bulk-Approved, bulk-
    Published, landing back at their real Published state).
  - **Subject Performance Analysis** (Strong Subjects / Improvement
    Areas): real per-Course averages across every submitted
    Assessment Result this term — unlike the per-topic "Algebra vs.
    Geometry" analysis skipped for the teacher dashboard, whole-
    subject averages (Mathematics, Physics, ...) are genuinely
    computable from existing data.
  - **Recent Activity**: discovered `Report Card` doesn't have change
    tracking enabled (zero rows in Frappe's own `Version` log despite
    61 real workflow transitions this session), so a planned
    "reconstruct the exact event history" approach was dropped in
    favor of what's actually verifiable — each card's own `modified`
    timestamp + current `workflow_state` ("X's report is now
    Published"), plus classes whose assessment date has passed with
    zero marks entered.
  - **Not built, deliberately:** a fake notification bell, a separate
    freeform "Headmaster Comments" log (duplicates the per-Report-
    Card comment fields that already exist), the elaborate Report
    Generation builder with Attendance/Behavior toggles (no
    attendance/behavior data model exists at all -- literally a
    future `edupro_attendance` app, not in scope), a mass "Send
    Broadcast" email composer, and "Notify Teachers"/multi-term trend
    charts (same single-term data limitation noted above).
- **Major restructuring: class taxonomy, dual Term/Exam marks, and a
  real curriculum-board/grading-band system.** The single largest
  change this project has taken in one batch — see `DECISIONS.md`
  0019 for the full reasoning behind every non-obvious call made here.
  - **Class list now matches the owner's exact spec.** Form 1
    (Purple/Green/Blue) and Form 2 (Blue/Green) kept as-is — Form 1
    Purple's 33 real students were completely untouched throughout.
    Form 2 Purple and all of Form 3/4's old Blue/Green/Purple classes
    were deleted (all sample data, confirmed via a real/sample student
    audit before deleting anything). Form 3, 4, and a brand new Form 5
    were rebuilt as Arts/Commercials/Science streams with genuinely
    different subject lists per stream (mirroring the existing Upper 6
    pattern — clearly a Claude-authored best-guess split, flagged for
    the owner to adjust). Upper 6 Arts/Commercials/Science were
    **renamed** (not recreated) to Form 6 Arts/Commercials/Science,
    keeping their existing students/subjects. Net: 17 classes total.
  - **Marks are now Term Mark + Exam Mark**, each out of 100 with its
    own independently computed grade (reverting the earlier single-
    Exam/100 consolidation from decision-batch "0016" — the owner
    confirmed wiping and starting fresh rather than trying to migrate
    the old single mark). This maps directly onto Education's existing
    two-criteria-per-plan model (same shape as the original Test/Exam
    split, just relabeled and reweighted 100/100 instead of 40/60) —
    no new data model was needed, `marks_entry.py`'s save/load logic
    was already criteria-agnostic. `/marks-entry` now shows a live
    grade *per column*, not one combined grade.
  - **Six curriculum Grading Scales added**, replacing the single
    "IGCSE Standard" placeholder: Cambridge Form 1-2/O Level/A Level
    and the ZIMSEC equivalents, entered verbatim from the owner's
    tables (including literal quirks like Cambridge O Level's grade
    *code* being "A*/A" for the whole 80-100 band, and "Ungraded" as
    the bottom-band code rather than a description).
  - **New curriculum-board + grading-band architecture.**
    `School Settings.curriculum_board` (Cambridge/ZIMSEC, default
    Cambridge) is the school-wide toggle the owner asked for. The
    existing `Curriculum` doctype was repurposed from holding two
    Cambridge-only records into three grading *bands* (Form 1-2/
    O Level/A Level) linked from `Program.curriculum` — Form level
    decides the band, the School Settings toggle decides the board;
    `grading.get_grading_scale_for_program()` combines the two to
    pick one of the six scales. Every class's real Assessment Plans
    were rebuilt against the correct scale for its band.
  - **Comments auto-load** from the grading scale's own Remark text
    for a subject's overall grade (e.g. a Cambridge Form 1-2 "C"
    auto-fills "Good") — populated when Report Cards are generated,
    but a teacher's own manually-entered comment is never overwritten.
  - **Delivered empty, matching "teacher must start entering marks."**
    All 222 Assessment Plans across all 17 classes (including Form 1
    Purple's real roster) were created with zero marks entered — this
    was verified end-to-end first (real marks entered for a disposable
    sample class, taken through generate → approve → publish, print
    format and live grade columns confirmed correct in a real browser
    session) and then that test data was fully wiped again so the
    delivered state is genuinely ready for real teachers to log in and
    start entering Term 2 marks themselves.

---

## 2026-07-03

### Added

- Initial project scaffolding decided: Frappe Framework, Docker-on-Windows
  dev environment, custom app `edupro_sms`. See `DECISIONS.md` 0001–0003.
