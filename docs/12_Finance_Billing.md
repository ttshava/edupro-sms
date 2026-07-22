# 12 — Finance & Billing

School fees management, integrated with the main academic reporting
platform so guardians can view fees alongside student reports. Future
evolution: a separate `edupro_finance` app with full GL/accounting.

## 12.1 Overview

**Billing Model:** Flat-rate termly fees determined by a student's
boarding type (Day Boarder or Full Boarder). One `Student Fee` record
per student per academic term.

**Payment Tracking:** Every billing event and payment creates a
`Student Ledger Entry` — a time-series ledger rendered as a running
Debit/Credit/Balance statement in the Fee Statement print format.

**Roles:** System Manager (full), Headmaster (manage), Bursar
(day-to-day management), Student/Guardian (read-only, own/linked
children only).

**Out of scope:** GL accounts, cost centers, multi-currency, invoicing,
payment gateway integration, financial reports beyond the ledger.

## 12.2 Billing Rules

| Boarding Type | Fee Amount (USD) | Notes |
|---|---|---|
| Day Boarder | 750 | Default if `Student.boarding_type` not set |
| Full Boarder | 1450 | |

Rates are set in `edupro_sms/fees.py::BOARDING_FEE`. Changes apply to
new fees only — existing `Student Fee` records aren't retroactively
recalculated.

## 12.3 Data Model

See `docs/03_DocTypes.md` for full field lists on `Student Fee` and
`Student Ledger Entry`.

## 12.4 Workflows

### Billing a Student

1. Create a `Student Fee` record: Student, Academic Term, Boarding Type
   (auto-populates `amount`), Billed On, Due Date.
2. Save — a `Student Ledger Entry` (debit) is auto-created: "Term X
   fees billed."
3. Fee status = `Billed` (balance = amount).

### Recording a Payment

1. Open the `Student Fee` record.
2. Increase `amount_paid` (add to the current total, don't replace it).
3. Save — a `Student Ledger Entry` (credit) is auto-created: "Payment
   received."
4. Status auto-updates: `Partially Paid` (balance > 0) or `Paid`
   (balance = 0).

### Viewing Fee History (Portal)

Student/Guardian → `/my-reports` → Fees tab: list of `Student Fee`
records with status pills, and a "View Statement" link to the Fee
Statement print format.

## 12.5 Print Formats

See `docs/05_Print_Formats.md` §5.2–5.3 for Fee Statement and Payment
Receipt layout.

## 12.6 Roles & Permissions

| Role | Create | Read | Write | Delete |
|---|---|---|---|---|
| System Manager | ✅ | ✅ | ✅ | ✅ |
| Headmaster | ✅ | ✅ | ✅ | ❌ |
| Bursar | ✅ | ✅ | ✅ | ❌ |
| Student | ❌ | ✅ (own only) | ❌ | ❌ |
| Guardian | ❌ | ✅ (children's only) | ❌ | ❌ |

## 12.7 Integration with Academic Reporting

Fees are independent of the report-card approval workflow — a student
can have an approved report card with outstanding fees, or vice versa.
Gating report-card release on fee status is a business-policy decision,
not currently implemented.

The Headmaster dashboard (`/dashboard`) shows whole-school Revenue
Collected / Outstanding Balance, plus a per-class breakdown, sourced
from `fees.py::get_school_fee_totals()` / `get_class_fee_summary()`.

## 12.8 Special Cases

| Scenario | Handling |
|---|---|
| Student transferred mid-term | `Student Fee` for the partial term created manually, prorated or full rate per school policy |
| Fee dispute / adjustment | Bursar creates a manual `Student Ledger Entry` with a descriptive note |
| Waived fees (scholarship) | Create a `Student Fee` at 0 amount, or a full-credit ledger entry |
| Late payment surcharge | Not modeled — would need a manual ledger entry or a future rules engine |

## 12.9 Status

Live for First Class High School — real termly billing and collection
across all 492 students.
