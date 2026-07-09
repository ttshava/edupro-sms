# 12 — Finance & Billing

School fees management system. Integrated with the main academic reporting platform (Sprint 8+), allowing guardians to view fees and payment status alongside student reports. Future evolution: separate `edupro_finance` app with full GL/accounting (post-MVP).

## 12.1 Overview

**Billing Model:** Flat-rate termly fees determined by student's boarding type (Day Boarder or Full Boarder). One `Student Fee` record per student per academic term.

**Payment Tracking:** Every billing event and payment receipt creates a `Student Ledger Entry` — a time-series accounting record. Rendered as a running ledger (Debit/Credit/Balance) in the Fee Statement print format, similar to a bank statement.

**Roles:** System Manager (full), Headmaster (manage), **Bursar** (new role, manages fees), Student/Guardian (read-only view of their own fees).

**Out of scope (post-MVP):** GL accounts, cost centers, allocation codes, multi-currency, invoicing, payment gateway integration, financial reports beyond ledger.

---

## 12.2 Billing Rules

| Boarding Type | Fee Amount (USD) | Notes |
|---|---|---|
| Day Boarder | 750 | Default; applied if `Student.boarding_type` not set |
| Full Boarder | 1450 | |

**Customization:** Edit `edupro_sms/edupro_sms/fees.py::BOARDING_FEE` dict to adjust rates. Changes take effect immediately for new fees; existing `Student Fee` records are not retroactively recalculated.

**Billing cycle:** One fee per academic term. Triggered manually or via a `Bill Students for Term` action (TBD — currently must be created manually or via console). Due date defaults to term end (configurable per `Student Fee.due_date`).

---

## 12.3 Data Model

### Student Fee

One record per Student + Academic Term. Holds the billing amount, payment status, and due date.

| Field | Type | Notes |
|---|---|---|
| student | Link → Student | required; naming key |
| student_name | Data | fetch_from student.student_name, read-only |
| academic_year | Link → Academic Year | read-only, set from context |
| academic_term | Link → Academic Term | required; naming key |
| boarding_type | Select | Day Boarder / Full Boarder — determines `amount` |
| amount | Currency | billed amount (calculated from boarding_type at creation) |
| amount_paid | Currency | default 0; incremented manually or via payment entry |
| balance | Currency | amount - amount_paid (always read-only, auto-calculated) |
| status | Select (read-only) | Billed / Partially Paid / Paid (auto-set based on balance) |
| billed_on | Date | date the fee was issued |
| due_date | Date | payment due date; no enforcement (informational only, MVP) |

**Naming:** `SF-{student}-{academic_term}` (e.g. `SF-STU-001-2026 (Term 1)`).

**Lifecycle:** Created manually or via a future "Bill Students" batch action. Can be edited until any payment is received (`amount_paid > 0`). Once `status = Paid`, locked (edit disabled, marked submitted/docstatus=1).

**Permissions:**
- System Manager: full CRUD + delete
- Headmaster: create, read, write, share (no delete)
- Bursar: create, read, write, share (no delete)
- Student: read-only (own fee only)
- Guardian: read-only (linked children's fees only)

### Student Ledger Entry

One record per ledger event (bill issued, payment received). Auto-created by `fees.py::_log_ledger_entry()` when:
- A new `Student Fee` is created (debit entry)
- A payment is manually recorded (credit entry)

| Field | Type | Notes |
|---|---|---|
| student | Link → Student | required; indexed for fast lookups |
| student_name | Data | fetch_from student.student_name, read-only |
| posting_datetime | Datetime | required; indexed; auto-set to now() on creation — timestamp of the ledger event |
| academic_term | Link → Academic Term | optional context (which term this entry relates to) |
| reference_student_fee | Link → Student Fee | optional; links back to the `Student Fee` that triggered this entry (null for orphaned entries) |
| description | Data | e.g. "Term 2 2026 fees billed", "Payment received via bank transfer", "Adjustment/credit" |
| debit | Currency | default 0; amount owed by student (fee billed) — increases student's balance |
| credit | Currency | default 0; amount paid by student — decreases student's balance |
| balance | Currency | read-only; running balance (sum of all debits - sum of all credits, up to this row) |

**Naming:** Hash-based (random, no business key).

**Lifecycle:** Immutable once created — no edit/delete. Represents a permanent audit trail of all financial events for a student.

**Permissions:** Same as Student Fee (System Manager full, Headmaster/Bursar manage, Student/Guardian read-only).

**Sort order:** by `posting_datetime` ASC (oldest first, like a ledger).

---

## 12.4 Workflows

### Billing a Single Student

(Manual; future: batch action)

1. Create a new `Student Fee` record:
   - Student: link to the Student
   - Academic Term: select the term
   - Boarding Type: auto-populated from `Student.boarding_type`
   - Amount: auto-calculated from boarding type
   - Billed On: set to today
   - Due Date: default end-of-term (customizable)
2. Save. A `Student Ledger Entry` (debit) is auto-created: `"Term X fees billed"`.
3. Fee status = `Billed` (balance = amount).

### Recording a Payment

(Manual; future: payment gateway / import)

1. Open the `Student Fee` record.
2. Edit `amount_paid` (add to current total, don't replace).
3. Save. A `Student Ledger Entry` (credit) is auto-created: `"Payment received"`.
4. Fee status auto-updates: `Partially Paid` (if balance > 0) or `Paid` (if balance = 0).

### Viewing Fee History (Student/Guardian Portal)

(TBD Sprint 9+)

- Student/Guardian login → `/my-reports` → "Fees" tab (placeholder exists)
- Shows: list of `Student Fee` records for the student/child
- Actions: View / Print fee statement (renders `Student Ledger Entry` rows as a running ledger)
- Filters: by academic year, status

---

## 12.5 Print Formats

### Fee Statement

Renders a single `Student Fee` record as a formal ledger statement, showing the running balance.

**Header:**
- School name, logo, motto from `School Settings`
- Title: "FEE STATEMENT"

**Student Block:**
- Name, admission number, class, academic year

**Ledger Section:**
- Table: one row per `Student Ledger Entry` (filtered to this student, sorted by posting_datetime ASC)
- Columns: Date, Description, Debit, Credit, Balance
- Rows are timestamped so exact payment dates are visible

**Summary Block:**
- Total Debits (total fees billed)
- Total Credits (total fees paid)
- Balance Due (amount still owed)
- Status badge: Paid / Partially Paid / Billed

**Footer:**
- Bursar contact details (name, email, phone) from `School Settings`
- Generation date

---

## 12.6 Roles & Permissions

| Role | Create | Read | Write | Delete | Manage (Bursar) |
|---|---|---|---|---|---|
| System Manager | ✅ | ✅ | ✅ | ✅ | N/A |
| Headmaster | ✅ | ✅ | ✅ | ❌ | Oversee, approve adjustments |
| Bursar | ✅ | ✅ | ✅ | ❌ | Full day-to-day management |
| Student | ❌ | ✅* | ❌ | ❌ | View own fees only |
| Guardian | ❌ | ✅* | ❌ | ❌ | View linked children's fees |

*Read-only access to fees and ledger entries for students/guardians linked to them.

---

## 12.7 Integration with Academic Reporting

**Student Portal (`/my-reports`):** Fees tab shows a list of `Student Fee` records with status pills (Paid/Partially Paid/Billed) and a "View Statement" link to the Fee Statement print format.

**Guardian Portal:** Same as student, but scoped to their linked children (already scoped via `guardian_permissions.py`).

**Headmaster Dashboard:** (TBD Sprint 9+) Summary panel: "Total Fees This Term", "Paid", "Outstanding" (sum across all students). Link to a Fees report for bulk actions.

**No direct tie to Report Card approval:** fees are independent — a student can have an approved report card with outstanding fees, or vice versa. A future enhancement (post-MVP) could add a gate (e.g. "don't release report cards until fees are paid"), but that's a business policy decision, not a data model one.

---

## 12.8 Special Cases

| Scenario | Handling |
|---|---|
| Student transferred mid-term | `Student Fee` for the partial term is created manually, prorated or at full rate (policy decision). Ledger remains intact, showing all historical events. |
| Fee dispute / adjustment | Bursar creates a manual `Student Ledger Entry` with description "Adjustment: dispute resolved" (debit or credit as needed). No special doctype, just a ledger entry. |
| Waived fees (scholarship) | Create a `Student Fee` at 0 amount, or a full-credit ledger entry at creation time (description: "Scholarship: full waiver"). |
| Late payment surcharge | (Post-MVP) — currently not modeled; would require a rules engine or a manual ledger entry (above). |
| Multi-currency (future) | Out of scope. Assume all fees in the school's local currency. |

---

## 12.10 Headmaster Dashboard Finance Summary (added 2026-07-09)

The main Headmaster/Deputy Head dashboard (`/dashboard`) now includes,
alongside the academic stat cards: **Subjects** (Course count), **Revenue
Collected** and **Outstanding Balance** (whole-school totals, sourced
from `fees.get_school_fee_totals()` — `sum(amount)`/`sum(amount_paid)`/
`sum(balance)` across every `Student Fee` record), and a **Finance —
Outstanding Balance by Class** table (`fees.get_class_fee_summary()`,
grouping the same per-student totals by `Student Group Student.parent`)
with a link out to `/bursar_fees/` for the existing student-by-student
drill-down (Bursar/Headmaster/System Manager already had access there —
it just wasn't linked from the dashboard nav before).

Two Headmaster-only pages predate this and are **not** part of the
correct data path — `headmaster_analytics/` and
`headmaster_dashboard_fees/` are backed by `analytics_api.py` and
`fee_dashboard_api.py`, which query a `Mark` doctype and `Student
Fee.program`/`Student Ledger Entry.reference_date` fields that don't
exist in this schema (real marks live in `Assessment Result`, real fees
have no `program` field). Neither page is linked from the dashboard nav.
Treat both API files as dead code pending a rewrite, not as the source
of truth for finance data — use `fees.py`'s functions instead.

## 12.11 Status & Roadmap

**Current:** Core billing model, flat rates, ledger tracking, print
format, portal read-only access, Headmaster dashboard finance summary
(§12.10). Real billing data live for First Class High School — Term 1–2
2026 billed and collected for all 491 students.

**Next:** Guardians can view fees and payment history on `/my-reports`
(build if not already covered by the student/parent portal fees tab).
Rewrite or remove `analytics_api.py`/`fee_dashboard_api.py` (§12.10).

**Post-MVP (`edupro_finance` app):** GL account mapping, cost centers, multi-term billing rules, payment gateway integration, financial reports (income statement, receivables aging), arrears handling, refunds.
