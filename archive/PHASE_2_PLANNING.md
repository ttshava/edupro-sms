# Phase 2 Implementation Plan — v1.1 Features #2-5

**Status:** 🟡 PLANNING  
**Target Duration:** 3-4 weeks  
**Features:** #2 (Batch Billing), #3 (Fee Dashboard), #4 (Batch Printing), #5 (Attendance)  
**Foundation:** ✅ Phase 1 Complete (CSV Import + Student Management)

---

## 📋 Phase 2 Features Overview

All 4 features build on Phase 1 foundation (enrolled students, guardian linking, bulk import).

### Feature #2: Batch Billing Action
**Goal:** Bursar can bill all students in a term at once (vs. one-by-one)

**Problem Solved:**
- Currently: Bursar must create Student Fee manually for each student
- With Feature #2: Bursar clicks "Bill All Students for Term 1" → 200 fees created in seconds

**Workflow:**
```
Bursar Dashboard → Billing Section → "Bill Students for Term X"
  ↓
Select Term (e.g., "Term 1 2026")
Select Program (e.g., "IGCSE Science") or All
Preview: "200 students will be billed $5,000 each"
  ↓
Click "Create Fees"
  ↓
Progress: "Creating 200 fees..."
  ↓
Complete: "200 fees created. Total: $1,000,000"
```

**Impact:**
- Current: 3+ hours (200 clicks × 1 min each)
- With Feature #2: 5 minutes (preview + confirm + process)

### Feature #3: Bursar Portal UI - Fee Entry
**Goal:** Bursar has dedicated UI for entering/editing student fees

**Problem Solved:**
- Currently: Fees managed via Frappe desk (generic, not user-friendly)
- With Feature #3: Bursar has professional portal with fee forms

**Workflow:**
```
Bursar Dashboard → Student Fees
  ↓
View list of all students + their fees for current term
Filter by status: Unpaid, Partially Paid, Paid
Search by student name
  ↓
Click on student → See fee details
  ↓
Edit fee: Change amount, boarding type, adjust charges
Record payment: Mark as Paid, record payment date
  ↓
View fee statement (PDF) for parent
```

**Impact:**
- Professional interface vs. generic Frappe desk
- Faster fee management
- Better visibility into payment status

### Feature #4: Headmaster Fee Dashboard
**Goal:** Headmaster sees financial overview (total billed, collected, outstanding)

**Problem Solved:**
- Currently: Headmaster can't see fee status at a glance
- With Feature #4: Dashboard shows: Total Billed, Total Collected, Outstanding Balance

**Workflow:**
```
Headmaster Dashboard → Fees Tab
  ↓
Shows:
  • Total Billed This Term: $500,000
  • Total Collected: $320,000
  • Outstanding: $180,000
  • Collection Rate: 64%
  
Charts:
  • Billing by program (pie chart)
  • Collection rate trend (line chart)
  • Unpaid students list (sortable table)
```

**Impact:**
- Real-time financial visibility
- Early warning for low collection
- Data-driven decision making

### Feature #5: Batch Report Card Printing
**Goal:** Headmaster can print all report cards at once (vs. one at a time)

**Problem Solved:**
- Currently: Headmaster must open each report card, click print (50 clicks × 10 sec = 8 min for 50 students)
- With Feature #5: Headmaster clicks "Print All" → PDF with all 50 reports

**Workflow:**
```
Headmaster Dashboard → Reports Section
  ↓
Click "Batch Print Report Cards"
  ↓
Select Criteria:
  • Class (Form 1A, Form 1B, etc.) or All
  • Term (Term 1, Term 2, etc.)
  • Status (All, Published only)
  ↓
Preview: "50 report cards will be printed"
  ↓
Click "Generate PDF"
  ↓
Progress: "Generating PDF with 50 reports..."
  ↓
Complete: PDF downloads (30+ pages)
  ↓
Print all at once or email to parents
```

**Impact:**
- Current: 50 individual PDFs (tedious)
- With Feature #5: 1 consolidated PDF (professional, efficient)

---

## 🎯 Phase 2 Task Breakdown

### Feature #2: Batch Billing (Estimated 4-5 days)

**Task 2.1: Batch Billing API** (2 days)
- Whitelisted method: `create_batch_fees(term, program, boarding_type_rates)`
- Logic: Query enrolled students → Create Student Fee for each
- Validation: Check term exists, rates set, no duplicates
- Returns: Count of fees created, total amount billed
- Error handling: Rollback if any fee fails

**Task 2.2: Billing Configuration** (1 day)
- Create "Billing Configuration" DocType
- Fields: Term, Program, Boarding Type, Fee Amount
- Allow Bursar to set rates per term/program/boarding
- Example: "Term 1 2026" × "IGCSE Science" × "Full Boarder" = $5,500

**Task 2.3: Bursar Billing UI** (1.5 days)
- Website page: `/bursar-billing/`
- Show current term billing status
- "Bill Students for Term X" button
- Preview modal (show # of students + total amount)
- Success message with counts
- List of created fees

**Task 2.4: Testing & Docs** (0.5 days)
- Test with 100+ students
- Test duplicate prevention
- Test rollback on error
- Document in USER_QUICKSTART.md

### Feature #3: Bursar Fee Entry Portal (Estimated 4-5 days)

**Task 3.1: Fee Entry API** (1.5 days)
- Methods: `get_student_fees()`, `update_student_fee()`, `record_payment()`
- Query fees by student/term/status
- Update fee amount, payment status, payment date
- Add payment records to Student Ledger Entry
- Validation & audit logging

**Task 3.2: Fee List UI** (1.5 days)
- Website page: `/bursar-fees/`
- Table: Student Name, Admission #, Amount, Status (Unpaid/Partial/Paid), Due Date
- Search by student name
- Filter by status, program, boarding type
- Pagination
- Quick actions: Edit, View Statement, Record Payment

**Task 3.3: Fee Edit & Payment Recording** (1.5 days)
- Edit fee form: Change amount, boarding type, adjust charges
- Payment recording form: Date, Amount, Method (Cash/Check/Transfer)
- Update Student Ledger Entry automatically
- Generate fee statement PDF
- Success/error messages

**Task 3.4: Testing & Docs** (0.5 days)
- Test fee editing
- Test payment recording
- Test ledger updates
- Update USER_QUICKSTART.md

### Feature #4: Headmaster Fee Dashboard (Estimated 2-3 days)

**Task 4.1: Fee Dashboard API** (1 day)
- Calculate: Total Billed, Total Collected, Outstanding, Collection %
- By Term, Program, Boarding Type
- Unpaid students list (sortable, filterable)
- Query Student Fee & Student Ledger Entry

**Task 4.2: Fee Dashboard UI** (1.5 days)
- Website page: `/headmaster-dashboard/`
- Summary cards: Total Billed, Collected, Outstanding, Collection Rate
- Charts: Billing by program (pie), Collection trend (line), Status breakdown (pie)
- Unpaid students table (sortable, paginated)
- Filter by term, program

**Task 4.3: Testing & Docs** (0.5 days)
- Test calculations
- Test charts render correctly
- Update USER_QUICKSTART.md

### Feature #5: Batch Report Printing (Estimated 3-4 days)

**Task 5.1: Batch Print API** (1.5 days)
- Method: `generate_batch_report_cards(criteria)`
- Query: Class/All, Term, Status
- Generate individual PDFs
- Merge into single PDF
- Return file path

**Task 5.2: Batch Print UI** (1.5 days)
- Website page: `/headmaster-batch-print/`
- Form: Select Class (dropdown), Select Term, Status filter
- Preview: "50 report cards will be printed"
- "Generate PDF" button
- Progress bar
- Download link when complete

**Task 5.3: Testing & Docs** (1 day)
- Test with 20+ report cards
- Test PDF merge
- Test performance
- Update USER_QUICKSTART.md

---

## 📊 Phase 2 Timeline

### Week 1: Features #2 & #3 (Billing)
- Mon-Tue: Feature #2 API + Config (Task 2.1-2.2)
- Wed: Feature #2 UI (Task 2.3)
- Thu-Fri: Feature #3 API + Fee List (Task 3.1-3.2)

### Week 2: Feature #3 Complete & Feature #4 Start
- Mon-Tue: Feature #3 Edit & Payment (Task 3.3)
- Wed: Feature #3 Testing + Feature #4 API (Task 3.4 + 4.1)
- Thu-Fri: Feature #4 UI (Task 4.2)

### Week 3: Feature #4 Complete & Feature #5
- Mon: Feature #4 Testing (Task 4.3)
- Tue-Wed: Feature #5 API + UI (Task 5.1-5.2)
- Thu-Fri: Feature #5 Testing + Integration (Task 5.3)

### Week 4: Integration & Final QA (Optional)
- Final integration testing (all features together)
- Performance optimization
- Final documentation

**Total: 3-4 weeks (3 weeks core + 1 week optional polish)**

---

## 🔄 Dependency Chain

```
Phase 1 (Complete) ✅
  ├─ CSV Import ✅
  └─ Student Management ✅
       ├─ Enrolled Students
       ├─ Guardian Links
       └─ Bulk Data
       
Phase 2 (Starting)
  ├─ Feature #2: Batch Billing ← Needs: Enrolled Students, Fee Rates
  ├─ Feature #3: Fee Portal ← Needs: Student Fees (from #2)
  ├─ Feature #4: Fee Dashboard ← Needs: Student Fees (from #2)
  └─ Feature #5: Batch Printing ← Needs: Published Reports
```

**No blocking dependencies between Phase 2 features** → Can work in parallel if needed.

---

## 💾 Database Impact (New/Modified)

**New DocTypes:**
- `Billing Configuration` — Fee rates per term/program/boarding
- `Student Fee` — Already exists (Phase 1), will be used
- `Student Ledger Entry` — Already exists (Phase 1), will be used

**Modified DocTypes:**
- `Student Fee` — Add: payment_status, payment_date fields
- `Student Ledger Entry` — Add: payment_method field

**New Website Pages:**
- `/bursar-billing/` — Batch billing UI
- `/bursar-fees/` — Fee entry portal
- `/headmaster-dashboard/fees/` — Fee dashboard (add to existing)
- `/headmaster-batch-print/` — Batch print UI

---

## 🧪 Testing Strategy

### Unit Tests
- Batch billing calculation (correct # of fees, correct amounts)
- Fee editing (fee updates, ledger entries created)
- Dashboard calculations (totals, percentages, filters)
- PDF generation (proper formatting, all pages included)

### Integration Tests
- Full billing workflow: Set rates → Bill all → Verify fees created
- Full fee entry: Create fee → Edit → Record payment → Verify ledger
- Dashboard + actual fees: Create fees → Check dashboard shows correct totals
- Batch print + real reports: Publish reports → Batch print → Verify PDF

### Performance Tests
- Batch billing: 500 students in <10 seconds
- Dashboard load: <2 seconds with 1000+ fees
- Batch print: 50 reports merged in <30 seconds

---

## 📝 Documentation Plan

**INSTALLATION_GUIDE.md** → Add sections:
- Billing Configuration setup
- Fee rate entry

**USER_QUICKSTART.md** → Add sections:
- Bursar: Batch Billing workflow
- Bursar: Fee entry & payment recording
- Headmaster: Fee dashboard overview
- Headmaster: Batch printing reports

**NEW: BILLING_GUIDE.md** (optional)
- Complete billing workflow
- Best practices
- Troubleshooting fees

---

## 🎯 Acceptance Criteria

### Feature #2: Batch Billing DONE when:
- [ ] Billing Configuration DocType works
- [ ] Batch billing creates fees for all students
- [ ] Fees have correct amounts based on rates
- [ ] No duplicates created on re-run
- [ ] Rollback works on error
- [ ] UI shows preview + results
- [ ] Tests pass (100+ students)
- [ ] Documentation complete

### Feature #3: Bursar Fee Portal DONE when:
- [ ] Fee list displays all student fees
- [ ] Search & filter work (by name, status, etc.)
- [ ] Edit fee form works (amount, charges)
- [ ] Payment recording works (date, method)
- [ ] Student Ledger updated automatically
- [ ] Fee statement PDF generates
- [ ] 50+ fees load in <2 seconds
- [ ] Documentation complete

### Feature #4: Fee Dashboard DONE when:
- [ ] Totals calculated correctly (billed, collected, outstanding)
- [ ] Collection % accurate
- [ ] Charts render correctly (pie, line, bar)
- [ ] Unpaid students list shows correctly
- [ ] Filters work (by term, program)
- [ ] Loads in <2 seconds
- [ ] Works with 1000+ fees
- [ ] Documentation complete

### Feature #5: Batch Printing DONE when:
- [ ] Criteria form works (class, term, status)
- [ ] Preview shows correct count
- [ ] PDF generated successfully
- [ ] All report cards in one PDF
- [ ] PDF downloads/opens correctly
- [ ] 50 reports merge in <30 seconds
- [ ] Print quality verified
- [ ] Documentation complete

---

## 🚀 Next Actions

1. **User Review** → Approve this Phase 2 plan
2. **Decide Priority** → Start with all 4 features or focus on one first?
3. **Set Start Date** → Ready to begin now or prepare first?
4. **Identify Risks** → Any concerns with the approach?

---

**Document Version:** 1.0  
**Date:** July 5, 2026  
**Status:** 🟡 READY FOR REVIEW & APPROVAL
