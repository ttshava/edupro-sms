# 05 — Print Formats

## 5.1 Report Card Print Format — built, Sprint 6

`IGCSE Report Card` — a Frappe Print Format (Jinja/HTML+CSS) on the
`Report Card` DocType (`docs/03_DocTypes.md`), `standard=1` so it's
version-controlled in `edupro_sms/edupro_sms/print_format/igcse_report_card/`.
Verified: generates a real PDF end-to-end via `frappe.get_print` +
`frappe.utils.pdf.get_pdf`.

Layout, top to bottom (all implemented):

1. **Header** — school name + motto from `School Settings` (via
   `frappe.db.get_single_value` — `frappe.get_single` is blocked in the
   print format Jinja sandbox, see `.claude/DECISIONS.md` 0008), "TERM
   REPORT CARD — {term}, {year}".
2. **Student details block** — student name, class, term, academic year.
3. **Academic performance table** — one row per subject (from the
   `assessment_results` child table): Subject, Score (total/max), Grade,
   Comment. Footer row: total, average %, overall grade, class position.
4. **Class Teacher comment** block.
5. **Headmaster comment** block.
6. **Signature blocks** — Class Teacher / Headmaster signature lines
   (plain lines for MVP; actual signature image attachments on `School
   Settings` are a nice-to-have, not built).
7. **Footer** — generation date, school phone/email from `School Settings`.

**Not yet built:** admission number, date of birth, gender on the student
details block (Student doctype has these — just not wired into the
template yet); Download/Print/Email action buttons in the portal context
(Sprint 7, once portals exist).

**Reuse note:** Education's `Student Report Generation Tool` has its own
`get_formatted_result` data-fetching helper
(`education.education.report.course_wise_assessment_report`) — not used
here since `generate_report_cards` (docs/03, docs/04) already produces
the aggregated data our print format needs directly from `Report Card`.

## 5.2 Fee Statement Print Format (built Sprint 8+)

`Fee Statement` — a Frappe Print Format (Jinja/HTML+CSS) on the `Student Fee` DocType. Renders as a student ledger statement showing the running Debit/Credit/Balance for a single student across all their fees and payments (sourced from `Student Ledger Entry` records).

Layout, top to bottom (all implemented):

1. **Header** — school name + motto from `School Settings`, "FEE STATEMENT".
2. **Student details block** — student name, admission number, class.
3. **Ledger table** — one row per `Student Ledger Entry` (ordered by `posting_datetime` ASC): Date, Description, Debit (amount owed), Credit (amount paid), Balance (running).
4. **Summary block** — total owed, total paid, balance due.
5. **Footer** — bursar contact details from `School Settings`.

## 5.3 Marks Entry Screen (Desk, reference layout)

Not a Print Format, but documented here since it's the primary
data-entry surface teachers use — implement as a custom Desk page/list
view for the `Assessment Result` DocType, filtered to the teacher's
assigned Student Group + Course:

- Header: class, term, subject, entry deadline, current status
  (Draft/Pending Approval/etc.), Save Draft / Submit for Approval actions.
- Table: one row per student — Test score, Exam score, auto-calculated
  Total, auto-calculated Grade, comment icon opening the subject comment
  field.
- Bulk actions: Add Student (edge case, e.g. late transfer-in), Bulk
  Upload (CSV/Excel) — nice-to-have, not blocking MVP if time-constrained,
  Print View.
- Inline validation: flag students with missing marks before allowing
  Submit for Approval.

## 5.4 PDF Generation Notes

- Uses Frappe's native Print Format → PDF rendering (wkhtmltopdf under the
  hood), not a separate PDF library — keeps it inside the framework's
  print system per `.claude/CODING_STANDARDS.md`. Verified working.
- **Gotcha (see `.claude/DECISIONS.md` 0008):** wkhtmltopdf needs a
  container-reachable base URL to fetch the print CSS. The default
  `frappe.utils.get_url()` (`http://edupro.localhost`, no port) isn't
  reachable from inside the backend container. Fixed with
  `bench set-config host_name "http://frontend:8080"`.
- **Not yet built:** triggering generation as a background job
  (currently invoked synchronously via `bench execute`/console — fine for
  one-off testing, but bulk generation for a whole class needs to move to
  `frappe.enqueue` per `.claude/CODING_STANDARDS.md` before Sprint 8).
  Target: < 5 sec/student (`docs/08_Deployment.md`).
