# 05 — Print Formats

## 5.1 Report Card Print Format

Built as a Frappe Print Format (Jinja/HTML+CSS) on the `Report Card`
DocType. Layout, top to bottom:

1. **Header** — school logo, school name, motto, "TERM {n} REPORT CARD",
   academic year.
2. **Student details block** — name, admission number, class, term dates,
   date of birth, gender.
3. **Academic performance table** — one row per subject:

   | Subject | Test (/max) | Exam (/max) | Total | Grade | Comment |
   |---|---|---|---|---|---|

   Footer row: overall total, average percentage, overall grade, class
   position (`position`/`number_of_students`).
4. **Class Teacher comment** block.
5. **Headmaster comment** block.
6. **Signature blocks** — Class Teacher signature, Headmaster signature
   (use `School Settings` attached signature images where available).
7. **Footer** — generation date, school contact info (phone, email).

Action buttons available wherever the report is viewed (Desk, portal):
Download PDF, Print, Email to Parent (Headmaster/Admin only), Back.

## 5.2 Marks Entry Screen (Desk, reference layout)

Not a Print Format, but documented here since it's the primary
data-entry surface teachers use — implement as a custom Desk page/list
view for the `Marks` DocType, filtered to the teacher's assigned
class+subject:

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

## 5.3 PDF Generation Notes

- Use Frappe's native Print Format → PDF rendering (wkhtmltopdf under the
  hood), not a separate PDF library — keeps it inside the framework's
  print system per `.claude/CODING_STANDARDS.md`.
- Generation happens as part of the Report Card Generation Workflow
  (`docs/04_Workflows.md` §4.2), triggered per-class in a background job so
  generating 200 PDFs doesn't block the request. Target: < 5 sec/student
  (`docs/08_Deployment.md`).
