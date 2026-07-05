# Phase 2: Implementation Tasks — All 4 Features

**Status:** 🟢 IN PROGRESS  
**Target Duration:** 3-4 weeks  
**Start Date:** July 5, 2026  
**Total Tasks:** 16  

---

## Feature #2: Batch Billing Action (4-5 days)

### Task 2.1: Billing Configuration DocType & API
**Objective:** Create DocType for managing fee rates per term/program/boarding  
**Status:** ✅ COMPLETE (488 lines)  
**Estimated:** 2 days | **Actual:** 0.5 days

**What to Build:**
- New DocType: `Billing Configuration`
- Fields:
  - Academic Term (Link → Academic Term)
  - Program (Link → Program)
  - Boarding Type (Select: Day Boarder, Full Boarder)
  - Amount (Currency)
  - Status (Select: Draft, Active, Inactive)
- Unique constraint: (Term, Program, Boarding Type) combo must be unique
- Whitelisted method: `get_billing_rates(term, program)`

**Files to Create:**
- `edupro_sms/doctype/billing_configuration/` (DocType JSON)
- `edupro_sms/batch_billing_api.py` (Main API)

**Subtasks:**
- [ ] Create DocType JSON
- [ ] Add permissions for Bursar
- [ ] Create whitelisted method for fetching rates
- [ ] Add validation (duplicate term+program+boarding)
- [ ] Test with sample data

---

### Task 2.2: Batch Billing API & Logic
**Objective:** Implement the core batch billing engine  
**Status:** ✅ COMPLETE (Included in Task 2.1)  
**Estimated:** 1.5 days | **Actual:** 0 days (part of 2.1)

**What to Build:**
- Whitelisted method: `create_batch_student_fees(term, program, boarding_filter)`
  - Params:
    - term: Academic Term name (e.g., "Term 1 2026")
    - program: Program name (e.g., "IGCSE Science") or "ALL"
    - boarding_filter: "Day Boarder", "Full Boarder", or "ALL"
  - Logic:
    1. Get billing rates for (term, program, boarding)
    2. Query Program Enrollment: WHERE academic_term = term AND program = program
    3. For each enrollment, check if Student Fee already exists (no duplicates)
    4. For non-duplicate enrollments, create Student Fee with amount from rates
    5. Log all operations (success/skip/fail)
    6. Return summary: {created: X, skipped: Y, failed: Z, total_amount: $}
  - Rollback on error (transaction safety)

**Files to Modify:**
- `edupro_sms/batch_billing_api.py` (add main method)

**Subtasks:**
- [ ] Query enrollment logic
- [ ] Duplicate detection (don't re-bill)
- [ ] Student Fee creation (set amount, dates)
- [ ] Audit logging
- [ ] Transaction rollback on error
- [ ] Test with 100+ students

---

### Task 2.3: Bursar Batch Billing UI
**Objective:** Website page for Bursar to trigger batch billing  
**Status:** ✅ COMPLETE (407 lines)  
**Estimated:** 1.5 days | **Actual:** 0.75 days

**What to Build:**
- Website page: `/bursar-billing/`
- HTML form:
  - Dropdown: Select Academic Term (auto-load from DB)
  - Dropdown: Select Program (auto-load) + "All Programs" option
  - Checkbox: Filter by Boarding Type (Day Boarder, Full Boarder, or All)
  - Preview button: "Preview billing (no changes)"
  - Confirm button: "Create Fees"
- Preview modal:
  - Shows: "X students will be billed $Y each = $TOTAL"
  - Allow user to confirm or cancel
- Results display:
  - "Billing complete: 200 created, 5 skipped, 0 failed"
  - "Total amount billed: $1,000,000"
  - Show summary table (created, skipped, failed counts)

**Files to Create:**
- `edupro_sms/www/bursar-billing/index.html` (UI)
- `edupro_sms/www/bursar-billing/index.py` (Context)

**Subtasks:**
- [ ] Form with dropdowns
- [ ] Preview modal
- [ ] API call to batch_billing_api
- [ ] Results display
- [ ] Permission check (Bursar only)
- [ ] Error handling & messages

---

### Task 2.4: Feature #2 Testing & Documentation
**Objective:** Test batch billing & document for users  
**Status:** ✅ COMPLETE (Test suite + Docs)  
**Estimated:** 0.5 days | **Actual:** 0.5 days

**Subtasks:**
- [ ] Test batch billing with 100+ students
- [ ] Test duplicate prevention (re-run same billing)
- [ ] Test fee amounts (verify correct calculation)
- [ ] Test performance (time to bill 500 students)
- [ ] Test rollback (error handling)
- [ ] Update USER_QUICKSTART.md with Bursar batch billing guide

---

## Feature #3: Bursar Fee Entry Portal (4-5 days)

### Task 3.1: Fee Entry & Payment Recording API
**Objective:** Build API for Bursar to manage fees and payments  
**Status:** ✅ COMPLETE (383 lines)  
**Estimated:** 1.5 days | **Actual:** 0.5 days

**What to Build:**
Whitelisted methods:
- `get_student_fees(program=None, status=None, limit=100)`
  - Returns: [{student_id, student_name, admission_number, amount, status, due_date, balance}]
  - Filters: By program, by payment status (Unpaid, Partial, Paid)
- `update_student_fee(fee_id, amount, status)`
  - Update fee amount or payment status
  - Create audit log entry
- `record_payment(fee_id, amount, payment_date, payment_method, notes)`
  - Creates Student Ledger Entry (debit from outstanding)
  - Updates fee status if fully paid
  - Returns updated balance

**Files to Create/Modify:**
- `edupro_sms/fee_entry_api.py` (new)
- Modify Student Fee DocType: Add payment_status, payment_date fields

**Subtasks:**
- [ ] Query student fees (by program, status)
- [ ] Update fee amount (validation)
- [ ] Record payment (create ledger, update status)
- [ ] Audit logging
- [ ] Permission checks (Bursar only)

---

### Task 3.2: Fee List & Search UI
**Objective:** Website page for Bursar to view/manage student fees  
**Status:** ✅ COMPLETE (550 lines)  
**Estimated:** 1.5 days | **Actual:** 0.75 days

**What to Build:**
- Website page: `/bursar-fees/`
- Table: Student Name, Admission #, Amount, Status (badge), Due Date, Balance
- Search box: Search by student name
- Filters:
  - Status dropdown: All, Unpaid, Partial, Paid
  - Program dropdown: All programs
  - Boarding Type: All, Day Boarder, Full Boarder
- Pagination: 20 fees per page
- Quick actions: Edit, View Statement, Record Payment (buttons)

**Files to Create:**
- `edupro_sms/www/bursar-fees/index.html` (UI)
- `edupro_sms/www/bursar-fees/index.py` (Context)

**Subtasks:**
- [ ] Fee list table
- [ ] Real-time search
- [ ] Status filtering
- [ ] Pagination
- [ ] Action buttons
- [ ] Permission check

---

### Task 3.3: Fee Edit & Payment Recording Forms
**Objective:** Forms for editing fees and recording payments  
**Status:** ✅ COMPLETE (Included in Task 3.2)  
**Estimated:** 1.5 days | **Actual:** 0 days (part of 3.2)

**What to Build:**
- Edit Fee Modal:
  - Fields: Amount, Charges, Status (dropdown)
  - Save button (calls update_student_fee API)
  - Cancel button
- Record Payment Modal:
  - Fields: Payment Date, Amount Paid, Payment Method (Cash/Check/Transfer)
  - Notes (optional)
  - Save button (calls record_payment API)
  - Shows updated balance after payment
- Fee Statement PDF link:
  - Generates PDF with fee details for parent

**Files to Create:**
- `edupro_sms/www/bursar-fees/edit-fee.html` (modal)
- `edupro_sms/www/bursar-fees/record-payment.html` (modal)

**Subtasks:**
- [ ] Edit fee form + API integration
- [ ] Record payment form + API integration
- [ ] Fee statement PDF generation
- [ ] Error handling & messages
- [ ] Success confirmation

---

### Task 3.4: Feature #3 Testing & Documentation
**Objective:** Test fee entry portal & document  
**Status:** ✅ COMPLETE (Test suite + Docs)  
**Estimated:** 0.5 days | **Actual:** 0.5 days

**Subtasks:**
- [ ] Test fee listing (search, filter, pagination)
- [ ] Test fee editing (amount update)
- [ ] Test payment recording (ledger created)
- [ ] Test performance (50+ fees load quickly)
- [ ] Update USER_QUICKSTART.md with Bursar fee entry guide

---

## Feature #4: Headmaster Fee Dashboard (2-3 days)

### Task 4.1: Fee Dashboard Calculations API
**Objective:** Build backend for financial calculations  
**Status:** 🟡 READY TO START  
**Estimated:** 1 day

**What to Build:**
- Whitelisted method: `get_fee_dashboard_data(term=current, program=None)`
  - Calculate:
    - Total Billed: Sum of all fees for term
    - Total Collected: Sum of paid amounts
    - Outstanding: Total Billed - Total Collected
    - Collection %: (Collected / Billed) * 100
  - By Program breakdown (pie chart data)
  - Collection trend (line chart data - by week)
  - Unpaid students list (sortable)

**Files to Create:**
- `edupro_sms/fee_dashboard_api.py` (new)

**Subtasks:**
- [ ] Calculate totals (billed, collected, outstanding)
- [ ] Calculate collection percentage
- [ ] Breakdown by program
- [ ] Collection trend calculation
- [ ] Unpaid students query
- [ ] Permission check (Headmaster only)

---

### Task 4.2: Headmaster Fee Dashboard UI
**Objective:** Dashboard page for Headmaster to see financial overview  
**Status:** 🟡 READY TO START  
**Estimated:** 1.5 days

**What to Build:**
- Website page: `/headmaster-dashboard/fees/` (add to existing dashboard)
- Summary Cards (4 cards, 3 columns):
  - Card 1: Total Billed ($500,000) — color: blue
  - Card 2: Total Collected ($320,000) — color: green
  - Card 3: Outstanding ($180,000) — color: red
  - Card 4: Collection % (64%) — color: orange
- Charts (3 charts):
  - Pie Chart: Billing by Program (IGCSE Science: 40%, IGCSE Commerce: 35%, etc.)
  - Line Chart: Collection Trend (Week 1: 50%, Week 2: 55%, Week 3: 62%, Week 4: 64%)
  - Pie Chart: Fee Status (Paid: 64%, Partial: 20%, Unpaid: 16%)
- Unpaid Students Table:
  - Columns: Student Name, Admission #, Amount, Days Overdue
  - Sortable, filterable
  - First 10 rows + pagination
- Filters:
  - Term dropdown (select term)
  - Program dropdown (All programs)

**Files to Create:**
- `edupro_sms/www/headmaster-dashboard/fees/index.html` (add to existing)
- Include Chart.js for graphs

**Subtasks:**
- [ ] Summary cards display
- [ ] Pie charts (billing by program, status)
- [ ] Line chart (collection trend)
- [ ] Unpaid students table
- [ ] Filters & real-time updates
- [ ] Responsive design

---

### Task 4.3: Feature #4 Testing & Documentation
**Objective:** Test fee dashboard & document  
**Status:** 🟡 READY TO START  
**Estimated:** 0.5 days

**Subtasks:**
- [ ] Test calculations (totals, percentages)
- [ ] Test charts render correctly
- [ ] Test with 1000+ fees (performance)
- [ ] Test filtering by term/program
- [ ] Update USER_QUICKSTART.md with Headmaster dashboard guide

---

## Feature #5: Batch Report Card Printing (3-4 days)

### Task 5.1: Batch Report Card PDF Generation API
**Objective:** Generate merged PDF of multiple report cards  
**Status:** 🟡 READY TO START  
**Estimated:** 1.5 days

**What to Build:**
- Whitelisted method: `generate_batch_report_cards(criteria)`
  - Params:
    - student_group: Form 1A or "ALL"
    - academic_term: Term 1 or specific term
    - status: "Published" or "ALL"
  - Logic:
    1. Query Report Cards matching criteria
    2. For each report, generate individual PDF using existing print format
    3. Merge all PDFs into single document
    4. Return file path
  - Error handling: Log failures, rollback if merge fails

**Files to Create:**
- `edupro_sms/batch_print_api.py` (new)

**Dependencies:**
- PyPDF2 or reportlab for PDF merging
- Existing report card print format

**Subtasks:**
- [ ] Query report cards by criteria
- [ ] Generate individual PDFs
- [ ] Merge PDFs into single file
- [ ] Error handling
- [ ] File cleanup (temp files)

---

### Task 5.2: Batch Print Selection & Progress UI
**Objective:** Website page for selecting criteria & generating batch PDF  
**Status:** 🟡 READY TO START  
**Estimated:** 1.5 days

**What to Build:**
- Website page: `/headmaster-batch-print/`
- Selection Form:
  - Dropdown: Select Class/Student Group (auto-load from DB) + "All Classes"
  - Dropdown: Select Term (auto-load)
  - Checkbox: Include only Published reports (yes/no)
  - "Preview" button: Shows "X report cards will be printed"
  - "Generate PDF" button: Starts generation
- Progress Bar:
  - Shows "Generating PDF with X reports..."
  - Real-time progress (1%, 25%, 50%, 100%)
- Results:
  - "PDF generated successfully"
  - Download link
  - File size info
  - Timestamp

**Files to Create:**
- `edupro_sms/www/headmaster-batch-print/index.html` (UI)
- `edupro_sms/www/headmaster-batch-print/index.py` (Context)

**Subtasks:**
- [ ] Form with dropdowns
- [ ] Preview modal
- [ ] API call to batch_print_api
- [ ] Progress bar with real-time updates
- [ ] Download link
- [ ] Permission check (Headmaster only)

---

### Task 5.3: Feature #5 Testing & Documentation
**Objective:** Test batch printing & document  
**Status:** 🟡 READY TO START  
**Estimated:** 1 day

**Subtasks:**
- [ ] Test with 20+ report cards
- [ ] Test PDF merge (verify all pages included)
- [ ] Test PDF opens/prints correctly
- [ ] Test performance (time for 50 reports)
- [ ] Test with different classes/terms
- [ ] Update USER_QUICKSTART.md with Headmaster batch print guide

---

## Integration & Final QA (3-4 days)

### Task Integration.1: End-to-End Testing
**Objective:** Test all 4 features working together  
**Status:** 🟡 READY TO START  
**Estimated:** 1.5 days

**Scenarios:**
- [ ] Batch billing → Bursar sees fees in portal → Headmaster sees totals in dashboard
- [ ] Record payment → Dashboard updates in real-time
- [ ] Generate batch print → Verify PDFs include all report cards

---

### Task Integration.2: Performance & Polish
**Objective:** Optimize and finalize all features  
**Status:** 🟡 READY TO START  
**Estimated:** 1 day

**Subtasks:**
- [ ] Performance testing (500+ fees)
- [ ] UI polish (responsive design)
- [ ] Error message improvements
- [ ] Documentation review

---

## 📊 Overall Task Summary

| Phase | Task | Days | Status |
|-------|------|------|--------|
| #2 | 2.1 Billing Config API | 2 | 🟡 Ready |
| #2 | 2.2 Batch Billing Logic | 1.5 | 🟡 Ready |
| #2 | 2.3 Batch Billing UI | 1.5 | 🟡 Ready |
| #2 | 2.4 Testing & Docs | 0.5 | 🟡 Ready |
| #3 | 3.1 Fee Entry API | 1.5 | 🟡 Ready |
| #3 | 3.2 Fee List UI | 1.5 | 🟡 Ready |
| #3 | 3.3 Edit & Payment Forms | 1.5 | 🟡 Ready |
| #3 | 3.4 Testing & Docs | 0.5 | 🟡 Ready |
| #4 | 4.1 Dashboard API | 1 | 🟡 Ready |
| #4 | 4.2 Dashboard UI | 1.5 | 🟡 Ready |
| #4 | 4.3 Testing & Docs | 0.5 | 🟡 Ready |
| #5 | 5.1 Batch Print API | 1.5 | 🟡 Ready |
| #5 | 5.2 Batch Print UI | 1.5 | 🟡 Ready |
| #5 | 5.3 Testing & Docs | 1 | 🟡 Ready |
| Integration | Integration.1 E2E Testing | 1.5 | 🟡 Ready |
| Integration | Integration.2 Polish | 1 | 🟡 Ready |
| **TOTAL** | | **21 days** | **🟢 Ready to Start** |

---

**Document Version:** 1.0  
**Date:** July 5, 2026  
**Status:** 🟢 READY FOR IMPLEMENTATION
