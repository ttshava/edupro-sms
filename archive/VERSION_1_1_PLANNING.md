# Edupro SMS v1.1 Planning Document

**Date:** July 5, 2026  
**Status:** Planning Phase (Awaiting Approval)  
**Release Target:** After v1.0 pilot feedback  

---

## 📋 Proposed Features for v1.1

### 1. Excel/CSV Import with Template Download
**Priority:** HIGH  
**User Benefit:** Bulk data entry for IT administrators; reduces manual entry time

**What It Does:**
- Users can download pre-formatted templates (Excel/CSV) for:
  - Students (name, email, DOB, gender, ID, boarding type, class)
  - Teachers/Instructors (name, email, subjects, class teacher flag)
  - Guardian/Parents (name, email, linked students)
  - Assessment Plans (class, subject, term, dates, criteria)
- Users fill templates and upload back to system
- System validates data and imports in bulk
- Shows progress bar and error report if issues found

**Implementation Scope:**
- [ ] Create template generator (Excel & CSV formats)
- [ ] Build CSV/Excel parser
- [ ] Add validation engine (checks for duplicates, missing fields, format errors)
- [ ] Create import progress UI (shows % complete, errors, success count)
- [ ] Add download templates button in each list view (Student, Instructor, Guardian, Assessment Plan)
- [ ] Update documentation

**Technical Changes:**
- New module: `edupro_sms/import_utils.py`
- New DocType method: `generate_import_template(doctype)`
- New whitelisted API: `upload_bulk_data(doctype, file_data)`
- Existing: Student, Instructor, Guardian, Assessment Plan DocTypes

**Benefits:**
- ✅ Reduces data entry time from hours to minutes
- ✅ Eliminates manual typing errors
- ✅ School admins can prepare data offline
- ✅ Clear error messages help fix issues quickly

**Workflow Impact:**
```
Current: Manual entry for 1,000 students = 20+ hours
v1.1: Download template → Fill in Excel → Upload → 30 minutes
```

---

### 2. Bursar Portal UI - Fee Entry Form

**Priority:** HIGH  
**User Benefit:** Bursar can manage fees directly from website (no Desk access needed)

**What It Does:**
- New website page: `/bursar-fees` (Bursar role only)
- Create/edit Student Fee records
- Manual payment entry
- View payment history per student
- Generate fee statements
- Export fee report to Excel

**Implementation Scope:**
- [ ] Create `/bursar-fees/` website page (index.html + index.py)
- [ ] Build fee creation form (select student, term, amount, due date)
- [ ] Add payment entry form (student, amount, date, notes)
- [ ] Create fee list view (searchable, filterable by status: Billed/Paid/Partial)
- [ ] Add fee statement generator button
- [ ] Add fee report export to Excel
- [ ] Add permission checks (only Bursar can access)
- [ ] Update documentation

**Technical Changes:**
- New file: `edupro_sms/www/bursar-fees/index.html`
- New file: `edupro_sms/www/bursar-fees/index.py`
- Update: `fee_permissions.py` (add website permission checks)
- No new DocTypes (uses existing Student Fee, Student Ledger Entry)

**Benefits:**
- ✅ Bursar doesn't need Desk access (simpler interface)
- ✅ Website form is more intuitive than Desk form
- ✅ Faster fee entry workflow
- ✅ No IT admin needed for daily fee operations

**Workflow Impact:**
```
Current: Bursar logs into Desk → Finds Student Fee list → Creates new → Fills form
v1.1: Bursar logs into portal → Goes to /bursar-fees → Sees list → Creates new → Same form but website-based
```

---

### 3. Batch Billing Action - "Bill All Students for Term X"

**Priority:** HIGH  
**User Benefit:** One-click billing for entire class/school instead of manual per-student

**What It Does:**
- Bursar selects: Academic Term + Student Group (class) [optional: all classes]
- System creates Student Fee records for all active students in selected group(s)
- Shows summary: "Created 45 fees for Form 1A, skipped 2 already billed"
- Can schedule for specific date or create immediately
- Audit trail shows who ran billing and when

**Implementation Scope:**
- [ ] Create whitelisted function: `bill_students_for_term(academic_term, student_group=None)`
- [ ] Add "Batch Billing" button to Bursar portal (`/bursar-fees`)
- [ ] Create modal form: Select Term → Select Classes → Confirm → Create
- [ ] Add validation: Skip already-billed students, skip inactive students
- [ ] Show progress and results
- [ ] Log action in audit trail
- [ ] Email notification to Headmaster (summary of billing)
- [ ] Update documentation

**Technical Changes:**
- New function in `edupro_sms/fees.py`: `bill_students_for_term()`
- Add button to `/bursar-fees/index.html`
- Update audit logging
- No new DocTypes (uses existing Student Fee)

**Benefits:**
- ✅ Eliminates manual per-student billing (saves hours)
- ✅ Ensures no student missed
- ✅ Repeatable for each term
- ✅ Clear audit trail

**Workflow Impact:**
```
Current: Bursar creates 100 Student Fee records manually = 2+ hours
v1.1: Bursar clicks "Batch Billing" → Selects Term → Selects Classes → Confirms → Done in 30 seconds
```

---

### 4. Fee Dashboard (Headmaster)

**Priority:** MEDIUM  
**User Benefit:** Headmaster can see school-wide fee collection status at a glance

**What It Does:**
- New section on Headmaster `/dashboard`
- Summary cards:
  - Total fees billed this term
  - Total fees collected (paid)
  - Outstanding balance
  - Collection rate (% of fees paid)
- Class performance table (by class):
  - Class name, number of students, fees billed, fees collected, % collection
  - Color-coded status (green: >90%, yellow: 50-90%, red: <50%)
- Click on class → Drill-down view showing per-student fee status
- Export button (fee summary to Excel)

**Implementation Scope:**
- [ ] Add new section to `/dashboard` (Headmaster branch only)
- [ ] Create fee summary SQL query
- [ ] Add class-level fee breakdown query
- [ ] Create drill-down view: `/class-fee-review?class=Form1A`
- [ ] Add color-coded status indicators
- [ ] Add export to Excel button
- [ ] Add refresh button (real-time data)
- [ ] Update documentation

**Technical Changes:**
- Update: `edupro_sms/www/dashboard/index.html` (add fee section)
- Update: `edupro_sms/www/dashboard/index.py` (add fee data queries)
- New file: `edupro_sms/www/class-fee-review/` (drill-down view)
- No new DocTypes (uses existing Student Fee, Student Ledger Entry)

**Benefits:**
- ✅ Headmaster has complete visibility of fee collection
- ✅ Early warning if collection is low (red indicator)
- ✅ Can track collection by class
- ✅ Supports financial planning

**Workflow Impact:**
```
Current: Headmaster must ask Bursar for fee report
v1.1: Headmaster sees fee summary on dashboard automatically, can drill down per class
```

---

### 5. Batch Report Card Printing Per Class

**Priority:** MEDIUM  
**User Benefit:** Print all report cards for a class at once (stack printing)

**What It Does:**
- New button on Headmaster `/dashboard`: "Print Class Reports"
- Select Class + Academic Term
- System generates PDFs for all students in that class
- Shows progress bar
- Provides download link for combined PDF (all reports in one file)
- Also offers individual PDFs if preferred
- Stores PDFs for later download

**Implementation Scope:**
- [ ] Create whitelisted function: `generate_class_reports_pdf(student_group, academic_term)`
- [ ] Add "Batch Print" button to dashboard
- [ ] Create modal: Select Class → Select Term → Generate
- [ ] Show progress bar while generating
- [ ] Create combined PDF (all reports + cover page with summary)
- [ ] Store PDFs in `/tmp` or cloud storage
- [ ] Provide download links
- [ ] Add email option (send combined PDF to Headmaster)
- [ ] Update documentation

**Technical Changes:**
- New function in `edupro_sms/report_card.py`: `generate_class_reports_pdf()`
- Update: `edupro_sms/www/dashboard/index.html` (add print button)
- Use existing PDF generation (wkhtmltopdf)
- No new DocTypes

**Benefits:**
- ✅ Saves time printing individual PDFs
- ✅ Combined PDF easier to organize for distribution
- ✅ Eliminates manual looping
- ✅ Can print to school printer directly

**Workflow Impact:**
```
Current: Headmaster generates 45 individual PDFs → Prints each one manually → Organizes stack
v1.1: Headmaster clicks "Print Class Reports" → Gets combined PDF → Print once
```

---

### 6. Bursar User Management (Add Students, Enroll, Link Parents)

**Priority:** MEDIUM  
**User Benefit:** Bursar can manage student/parent data (enrollment, linking) without IT admin

**What It Does:**
- New section on Bursar `/bursar` portal: "Student Management"
- Bursar can:
  - Add new Student records (name, email, DOB, gender, ID, boarding type)
  - Enroll student in Program (select Program, Academic Year → auto-links courses)
  - Add to Student Group (select class)
  - Link Guardian (select existing or create new parent/guardian)
  - Edit student info (update boarding type, change class, etc.)
  - Deactivate student (set status to Transferred/Graduated)
  - View student list (searchable, filterable)

**Implementation Scope:**
- [ ] Create new Bursar portal page: `/bursar-students/`
- [ ] Add Student creation form
- [ ] Add Student enrollment form
- [ ] Add Student-Guardian linking form
- [ ] Add student search/list view
- [ ] Add edit form (update existing student)
- [ ] Add bulk student upload (via CSV, built on Feature #1)
- [ ] Add permission checks (only Bursar can access)
- [ ] Add audit trail for all changes
- [ ] Update documentation

**Technical Changes:**
- New file: `edupro_sms/www/bursar-students/index.html`
- New file: `edupro_sms/www/bursar-students/index.py`
- Update: `fee_permissions.py` (add student management permissions for Bursar)
- Update: `edupro_sms/doctype/student/student.json` (add Bursar permissions)
- Update: `edupro_sms/doctype/guardian/guardian.json` (add Bursar permissions)
- Update: `edupro_sms/doctype/program_enrollment/program_enrollment.json` (add Bursar permissions)

**Benefits:**
- ✅ Bursar can manage day-to-day student changes (transfers, new admissions)
- ✅ School doesn't need IT admin for routine student data updates
- ✅ Faster onboarding for new students
- ✅ Bursar stays in control of student/parent linking

**Workflow Impact:**
```
Current: New student enrolled → IT admin creates Student → Enrolls → Links parents (3 manual steps)
v1.1: Bursar logs in → Clicks "Add Student" → Fills form → Enrolls → Links parents (1 unified flow)
```

---

## 🔗 Feature Dependencies & Order

### Dependency Graph:
```
Feature #1 (CSV Import)
  ├─ Used by Feature #2 (Bursar can import student fees via CSV)
  ├─ Used by Feature #3 (Bursar can import students, teachers)
  └─ Used by Feature #6 (Bursar bulk-uploads students via CSV)

Feature #2 (Bursar Portal - Fee Entry)
  ├─ Feeds into Feature #3 (batch billing creates fees)
  ├─ Feeds into Feature #4 (dashboard shows this fee data)
  └─ Requires Feature #6 (students must exist to bill them)

Feature #3 (Batch Billing)
  ├─ Requires Feature #2 (fee entry portal must work first)
  ├─ Requires Feature #6 (students must be enrolled)
  └─ Feeds into Feature #4 (dashboard shows billed fees)

Feature #4 (Fee Dashboard)
  ├─ Requires Features #2 & #3 (fees must be created to display)
  └─ Read-only (no dependencies on other features)

Feature #5 (Batch Printing)
  ├─ Independent (works with existing report cards)
  └─ No dependencies

Feature #6 (Bursar Student Management)
  ├─ Required by Feature #2 (students needed to create fees)
  ├─ Required by Feature #3 (students needed for batch billing)
  └─ Used with Feature #1 (bulk CSV import)
```

### Recommended Implementation Order:

1. **Feature #1** (CSV Import) - Foundation for bulk operations
2. **Feature #6** (Bursar Student Management) - Get students into system
3. **Feature #2** (Bursar Portal - Fee Entry) - Create fees
4. **Feature #3** (Batch Billing) - Automate fee creation
5. **Feature #4** (Fee Dashboard) - Monitor collection
6. **Feature #5** (Batch Printing) - Convenience feature (independent)

---

## 📊 Workflow & Functionality Analysis

### Current v1.0 Workflow (Manual, IT-dependent):

```
Workflow: Marks Entry → Approval → Report Cards → Fees (manual)

Academic Staff (Teachers, Headmaster):
  ✓ Enter marks
  ✓ Approve report cards
  ✓ View dashboards
  ✓ Email parents

IT Administrator:
  ✓ Create Student records (manually)
  ✓ Enroll students
  ✓ Link parents
  ✓ Create classes
  ✓ Create assessment plans

Bursar:
  ✓ Create Student Fee records (manually, one by one)
  ✓ Record payments
  ✓ View fee list
  ✗ Cannot access portal (no portal)
  ✗ Cannot manage students
  ✗ Cannot bulk bill
```

### Improved v1.1 Workflow (Bulk operations, Bursar-independent):

```
Workflow: Data Import → Marks Entry → Approval → Report Cards → Batch Billing → Fee Collection

IT Administrator:
  ✓ Prepare data templates (do once per year)
  ✓ Provide to school staff for data entry
  ✓ Focus on infrastructure/troubleshooting

Bursar:
  ✓ Can now add/manage students
  ✓ Can enroll students in classes
  ✓ Can link parents
  ✓ Can bulk bill all students at once
  ✓ Can create fees via portal (no Desk access)
  ✓ Can record payments
  ✓ Can view fee dashboards
  ✓ Can export fee reports
  ✓ Does NOT need IT admin for daily operations

Headmaster:
  ✓ Can see fee collection dashboard
  ✓ Can drill down by class
  ✓ Can batch print report cards
  ✓ Can see real-time fee status

School Data Manager (new role, optional):
  ✓ Uploads bulk student/teacher CSV files
  ✓ Manages enrollment data
  ✓ Coordinate with Bursar
```

### Benefits Summary:

| Current State (v1.0) | Improved State (v1.1) | Impact |
|---|---|---|
| Manual student entry (1 at a time) | CSV bulk import (100 at once) | **✅ 90% time savings** |
| IT admin adds every student | Bursar can add students | **✅ IT freed up for infrastructure** |
| Bursar can't do daily fees | Bursar has full fee portal | **✅ Complete autonomy** |
| Manual per-student billing | One-click batch billing | **✅ Eliminates hours of work** |
| No fee visibility for Headmaster | Fee dashboard with drill-down | **✅ Full financial visibility** |
| Print reports individually | Batch print entire class | **✅ Time savings for printing** |

---

## 📈 Business Impact

### Problem Solved:
- **Bottleneck:** IT administrator is required for all data entry (students, teachers, assessments)
- **Solution:** Bursar + bulk import → Admins can do most tasks independently

### Efficiency Gains:
- New student enrollment: 15 minutes → 2 minutes (bulk: 100 students in 5 minutes)
- Monthly billing: 3+ hours → 5 minutes
- Report printing: 1 hour → 5 minutes
- Fee tracking: Manual inquiry → Instant dashboard

### User Satisfaction:
- Bursar: Full autonomy for financial operations
- Headmaster: Real-time financial dashboards
- IT Admin: Freed from routine data entry
- Teachers: No change (continue with existing workflow)

---

## ⚠️ Implementation Risks & Considerations

### Risk 1: Data Validation
**Risk:** Bulk imports with invalid data could corrupt system
**Mitigation:** 
- Strict CSV validation (type-checking, required fields)
- Preview before commit ("Show 5 records to import, are these correct?")
- Rollback on error (if 10 records have errors, show them and let user fix)

### Risk 2: Permission Creep
**Risk:** Giving Bursar too much access (student management) could allow data tampering
**Mitigation:**
- Strict permission matrix (Bursar CAN add/edit Student, but NOT change classes mid-term without approval)
- Audit trail for all changes (who changed what, when)
- Headmaster approval workflow for critical changes (move student between classes)

### Risk 3: Performance
**Risk:** Batch operations could be slow (batch billing 1,000 students)
**Mitigation:**
- Use background jobs (RQ) for long-running operations
- Show progress bar with realistic ETA
- Test performance with real data (1,000+ students)

### Risk 4: Backward Compatibility
**Risk:** Existing v1.0 installations won't have new portal UI for Bursar
**Mitigation:**
- New features don't change existing Desk workflows
- Bursar can still use Desk if needed (both work)
- Phased rollout (make portal optional, encourage migration over time)

---

## 🎯 Approval Checklist

Before proceeding with v1.1 implementation, verify:

- [ ] **Feature Set:** Do all 6 features align with school needs?
- [ ] **Priority:** Is the implementation order correct?
- [ ] **Risk:** Are the mitigation strategies sufficient?
- [ ] **Timeline:** Can these be done in one sprint (2-3 weeks)?
- [ ] **Testing:** Do we have time for proper QA?
- [ ] **Documentation:** Will guides be updated for each feature?
- [ ] **User Training:** Will Bursar/Headmaster need training?

---

## 📝 Next Steps (Pending Approval)

**If all features are approved:**
1. Start with Feature #1 (CSV Import) - foundational
2. Move to Feature #6 (Bursar Student Management)
3. Continue with Features #2, #3, #4, #5 in order
4. Test each feature independently before moving to next
5. Full system test before v1.1 release

**If some features need revision:**
- List which ones
- Request changes
- Re-evaluate dependencies
- Return to planning

---

## ✅ Sign-Off

**Planning Status:** ⏳ AWAITING YOUR APPROVAL

**Questions for You:**

1. **Do all 6 features align with your school's needs?**
2. **Are there any features you'd like to remove, add, or modify?**
3. **Is the implementation order correct?**
4. **Any concerns about the risk mitigation strategies?**
5. **Timeline:** Can this be done in 1-2 months?

**Once Approved:**
- We'll proceed to detailed design
- Create task breakdown for each feature
- Begin implementation

---

**Document Version:** 1.0  
**Date Created:** July 5, 2026  
**Status:** 🟡 AWAITING APPROVAL
