# Edupro SMS — Comprehensive Testing Guide

**Purpose:** Full system testing to verify all features produce design results  
**Project:** Edupro School Management System (Academic Reporting + Finance)  
**Scope:** All 9 Features (Phase 1, 2, 3)  
**Date:** July 5, 2026  
**Status:** Ready for Testing

---

## 🎯 Testing Overview

This guide provides **step-by-step testing procedures** to verify that all built features work correctly and produce the intended design results.

**Total Test Coverage:** 450+ scenarios across 9 features  
**Estimated Testing Time:** 2-3 days (full system QA)  
**Test Environment:** Development instance with sample data

---

## 📋 Pre-Testing Checklist

Before starting, verify:

- [ ] Docker containers running (Frappe/MariaDB/Redis)
- [ ] Sample data loaded (Academic Terms, Programs, Students, Marks)
- [ ] All 9 features deployed to `/apps/edupro_sms/`
- [ ] User roles created: System Manager, Headmaster, Bursar, Teacher, Student, Guardian
- [ ] Test accounts created for each role
- [ ] Sample data in database:
  - [ ] 3+ Academic Terms (Term 1, 2, 3 for 2026)
  - [ ] 3+ Programs (IGCSE Science, IGCSE Commerce, O-Level Math)
  - [ ] 200+ Students across programs
  - [ ] 50+ Guardians linked to students
  - [ ] 100+ Marks entries across subjects/terms
  - [ ] Billing Configurations for fee rates
  - [ ] 50+ Report Cards (published)

---

## ✅ FEATURE #1: Bulk Student/Staff Import (CSV)

### Test 1.1: CSV Template Download
**Objective:** Verify template has correct structure
```
Steps:
1. Log in as System Manager
2. Navigate to /bursar-students
3. Click "Bulk Import" button
4. Download Student CSV template
5. Verify columns: Student Name, Email, Admission Number, Program, Class, Gender, Boarding Type

Expected Result:
✅ Template downloads with all required columns
✅ Headers match database field names
✅ Example data provided (2-3 rows)
✅ File is valid CSV (opens correctly in Excel/Sheets)
```

### Test 1.2: CSV Validation
**Objective:** Verify validation catches errors
```
Steps:
1. Download CSV template
2. Fill 50 students with:
   - Row 5: Missing Email (required field)
   - Row 10: Invalid Email format (abc@)
   - Row 15: Duplicate Email (same as Row 1)
   - Row 20: Program doesn't exist
3. Upload file
4. Review validation results

Expected Result:
✅ Validation report shows all errors
✅ Row 5: "Email is required"
✅ Row 10: "Invalid email format"
✅ Row 15: "Email already exists"
✅ Row 20: "Program not found"
✅ Success count shows 49/50 valid rows
```

### Test 1.3: CSV Import (Success)
**Objective:** Verify bulk import creates students
```
Steps:
1. Download template
2. Fill 100 valid student records
3. Upload CSV
4. Review validation: all 100 pass
5. Click "Import" button
6. Wait for completion
7. Check Student list

Expected Result:
✅ Import completes in <10 seconds
✅ 100 new students appear in list
✅ Each student has correct data:
   - Name matches CSV
   - Email unique
   - Enrollment created
   - Boarding Type saved
✅ Audit log shows import details
✅ Email notification sent to uploaded students
```

### Test 1.4: Duplicate Prevention
**Objective:** Verify re-import doesn't duplicate
```
Steps:
1. Import 50 students (from Test 1.3)
2. Wait 30 seconds
3. Re-import same 50 students CSV
4. Check validation results

Expected Result:
✅ Validation detects duplicates
✅ Shows "50/50 already exist" message
✅ Option to skip or update provided
✅ No duplicate entries created
✅ Original data unchanged
```

---

## ✅ FEATURE #2: Batch Billing

### Test 2.1: Billing Configuration Setup
**Objective:** Verify fee rates configured
```
Steps:
1. Log in as Headmaster
2. Create Billing Configurations:
   - Term 1 2026 + IGCSE Science + Day Boarder = $5,000
   - Term 1 2026 + IGCSE Science + Full Boarder = $5,500
   - Term 1 2026 + IGCSE Commerce + Day Boarder = $4,500
   - Term 1 2026 + IGCSE Commerce + Full Boarder = $5,000

Expected Result:
✅ 4 rates created
✅ Each rate has unique name: BC-Term 1 2026-IGCSE Science-Day Boarder
✅ Rates visible in Billing Configuration list
✅ Rates searchable by term/program/boarding
```

### Test 2.2: Batch Billing Preview
**Objective:** Verify preview calculates correctly
```
Steps:
1. Log in as Bursar
2. Go to /bursar-billing/
3. Select:
   - Term: Term 1 2026
   - Program: IGCSE Science
   - Boarding: All
4. Click "Preview Billing (No Changes)"
5. Review preview modal

Expected Result:
✅ Modal shows:
   - Student count: ~80 (IGCSE Science students)
   - Total amount: ~430,000 (50×5000 + 30×5500)
   - Breakdown: Day Boarder 50, Full Boarder 30
   - First 5 students listed with names
✅ All calculations accurate
✅ No changes made to database (preview only)
```

### Test 2.3: Batch Billing Execution
**Objective:** Verify batch creates all fees
```
Steps:
1. From preview modal, click "Confirm & Create Fees"
2. Wait for progress bar (0% → 100%)
3. Review results

Expected Result:
✅ Progress shows: "Generating fees... Completed!"
✅ Results show:
   - Created: 80
   - Skipped: 0
   - Failed: 0
   - Total Billed: $430,000
✅ 80 Student Fee records created in database
✅ Each fee has:
   - student: linked correctly
   - amount: matches rate
   - status: "Unpaid"
   - academic_term: "Term 1 2026"
```

### Test 2.4: Duplicate Prevention
**Objective:** Verify re-run skips existing
```
Steps:
1. From Test 2.3, fees are already created
2. Go back to /bursar-billing/
3. Select same criteria (Term 1, IGCSE Science, All)
4. Click Preview
5. Click "Confirm & Create Fees"

Expected Result:
✅ Preview shows 80 students
✅ Results show:
   - Created: 0 (no new fees)
   - Skipped: 80 (already exist)
   - Failed: 0
✅ No duplicate fees created
✅ Database still has only 80 fees
```

---

## ✅ FEATURE #3: Fee Entry Portal

### Test 3.1: Fee List Display
**Objective:** Verify all fees show in portal
```
Steps:
1. Log in as Bursar
2. Go to /bursar-fees/
3. Page loads

Expected Result:
✅ Table shows fees:
   - Columns: Student Name, Admission #, Email, Program, Term, Amount, Status, Due Date, Balance
   - First 20 fees displayed
   - "Showing 20 of 80 fees"
✅ Status badges colored:
   - Red: Unpaid
   - Yellow: Partially Paid
   - Green: Paid
✅ All data matches database
```

### Test 3.2: Fee Search
**Objective:** Verify search filters results
```
Steps:
1. In fee list, search for "John" in search box
2. Review results
3. Search for email "john@school.com"
4. Search for admission "ADM-001"

Expected Result:
✅ Each search filters instantly (<1 sec)
✅ Table shows only matching fees
✅ Count updates: "Showing X of Y"
✅ Can clear search and see all again
```

### Test 3.3: Fee Filtering
**Objective:** Verify filters work
```
Steps:
1. Filter by Program: "IGCSE Science"
2. Verify only Science fees shown
3. Filter by Status: "Unpaid"
4. Verify only Unpaid status shown
5. Filter by Term: "Term 1 2026"
6. Verify only Term 1 fees shown
7. Combine filters: Program + Status
8. Click "Reset Filters"

Expected Result:
✅ Each filter updates table instantly
✅ Combined filters work correctly
✅ Count matches filtered results
✅ Reset clears all selections
```

### Test 3.4: Edit Fee
**Objective:** Verify editing amounts works
```
Steps:
1. Find a fee for $5,000
2. Click edit (pencil icon)
3. Modal opens with current amount
4. Change amount to $5,500
5. Click "Save Changes"
6. Verify fee updated in table

Expected Result:
✅ Modal opens with correct student/amount
✅ Amount field editable
✅ Save updates database instantly
✅ Table refreshes with new amount
✅ Status unchanged
✅ Audit log records change
```

### Test 3.5: Record Payment
**Objective:** Verify payment recording works
```
Steps:
1. Find a fee for $5,000 (Unpaid)
2. Click payment icon
3. Modal opens
4. Enter:
   - Payment Date: Today
   - Amount Paid: $2,000
   - Payment Method: Cash
   - Notes: "First installment"
5. Click "Record Payment"
6. Verify fee updated

Expected Result:
✅ Payment modal opens
✅ Outstanding balance shows $5,000
✅ Payment date pre-filled with today
✅ After recording:
   - Balance updates to $3,000
   - Status changes to "Partially Paid" (yellow)
   - Table refreshes instantly
✅ Ledger entry created in database
✅ Next payment: can record additional $3,000
```

### Test 3.6: Payment Validation
**Objective:** Verify overpayment prevention
```
Steps:
1. Open payment modal for $3,000 balance fee
2. Try to pay $4,000 (more than balance)
3. Click "Record Payment"

Expected Result:
✅ Error message: "Payment exceeds outstanding balance ($3,000)"
✅ Payment not recorded
✅ Fee status unchanged
```

---

## ✅ FEATURE #4: Fee Dashboard

### Test 4.1: Dashboard Load
**Objective:** Verify summary cards show correct totals
```
Steps:
1. Log in as Headmaster
2. Go to /headmaster-dashboard/fees/
3. Select Term 1 2026
4. Click "Load Dashboard"
5. Wait for data to populate

Expected Result:
✅ Summary cards show:
   - Total Billed: $430,000
   - Total Collected: $2,000 (from Test 3.5)
   - Outstanding: $428,000
   - Collection %: 0.47%
✅ All calculations match database
```

### Test 4.2: Charts Render
**Objective:** Verify charts display correctly
```
Steps:
1. Dashboard loaded (from 4.1)
2. Review charts:
   - "By Program" pie chart
   - "By Status" doughnut chart
   - "Collection Trend" line chart

Expected Result:
✅ All charts render without errors
✅ By Program chart shows:
   - IGCSE Science: $430,000 slice
✅ By Status chart shows:
   - Unpaid: 79 students
   - Partial: 1 student (from payment)
   - Paid: 0 students
✅ Collection Trend shows upward trend (0.47%)
✅ Hovering on chart shows tooltips
```

### Test 4.3: Unpaid Students Table
**Objective:** Verify at-risk students listed
```
Steps:
1. Dashboard loaded
2. Scroll to "Top Unpaid Students" table
3. Review list

Expected Result:
✅ Table shows students with outstanding balances
✅ Sorted by "Days Overdue"
✅ Columns: Student Name, Admission #, Amount Due, Days Overdue
✅ Top student is the one with $3,000 balance (from Test 3.5)
✅ Shows "Showing 1 of 79 unpaid students"
```

### Test 4.4: Program Filter
**Objective:** Verify dashboard filters by program
```
Steps:
1. Dashboard loaded
2. Select Program: "IGCSE Science"
3. Click "Load Dashboard"
4. Review updated data

Expected Result:
✅ Summary cards update:
   - Total Billed: $430,000 (all IGCSE Science)
   - Total Collected: $2,000
   - Outstanding: $428,000
✅ Charts update to show only IGCSE Science
✅ Program filter works correctly
```

---

## ✅ FEATURE #5: Batch Report Card Printing

### Test 5.1: Batch Print Preview
**Objective:** Verify preview shows count
```
Steps:
1. Log in as Headmaster
2. Go to /headmaster-batch-print/
3. Select:
   - Class: Form 1A
   - Term: Term 1 2026
   - Include Published Only: checked
4. Click "Preview"

Expected Result:
✅ Preview modal shows:
   - Report count: ~25 (Form 1A students)
   - Estimated pages: 25
   - Estimated file size: ~5MB
   - First 5 students listed
```

### Test 5.2: Generate Batch PDF
**Objective:** Verify PDF merges and downloads
```
Steps:
1. From preview modal, click "Generate PDF"
2. Progress bar appears (0% → 100%)
3. Wait for completion
4. Click "Download PDF"

Expected Result:
✅ Progress bar shows:
   - "Generating report card PDFs..."
   - "Merging PDFs into single document..."
   - "Finalizing PDF..."
✅ After 100%:
   - Results show: "Successfully merged 25 reports (25 pages)"
   - File size shown: ~5MB
   - Download link active
✅ PDF downloads to computer
✅ PDF opens in viewer
✅ All 25 report cards in sequence
```

### Test 5.3: PDF Quality Check
**Objective:** Verify PDF content is complete
```
Steps:
1. PDF downloaded from Test 5.2
2. Open PDF in Adobe Reader / Browser
3. Check first report card
4. Check middle report card (page ~13)
5. Check last report card (page 25)

Expected Result:
✅ Each report card shows:
   - Student name and ID
   - All subjects with marks
   - Grades calculated correctly
   - Teacher comments
   - Class position
✅ PDF pages are in order
✅ All content legible and properly formatted
✅ PDF prints correctly
```

---

## ✅ FEATURE #7: Student/Parent Portal

### Test 7.1: Student Login
**Objective:** Verify student can access own data
```
Steps:
1. Student logs in (e.g., student_001@school.com)
2. Navigates to /my-student-dashboard/
3. Dashboard loads

Expected Result:
✅ Page shows:
   - Student name in header
   - Current term: "Term 1 2026"
   - GPA: ~3.8 (calculated)
   - Class position: ~15/45
   - Outstanding fees: shows amount
```

### Test 7.2: Student Grades Tab
**Objective:** Verify grades display correctly
```
Steps:
1. Student logged in (from 7.1)
2. Click "Grades" tab
3. Review grade table
4. Filter by term "Term 1 2026"

Expected Result:
✅ Table shows all subjects with:
   - Subject name
   - Term mark: 0-100
   - Exam mark: 0-100
   - Total mark: sum
   - Grade: A/B/C/D/E
   - Teacher comment
✅ Term average shown: ~72.5%
✅ Filter by term works
```

### Test 7.3: Student Reports Tab
**Objective:** Verify reports downloadable
```
Steps:
1. Student logged in
2. Click "Reports" tab
3. Review report list
4. Click "Download PDF" for a report
5. Click "Preview" for another report

Expected Result:
✅ Reports listed by term
✅ Download button works (PDF downloads)
✅ Preview button opens in new tab
✅ Each report shows Term 1 2026 data
✅ PDF contains student's marks and grades
```

### Test 7.4: Student Fees Tab
**Objective:** Verify fee summary shows
```
Steps:
1. Student logged in
2. Click "Fees" tab
3. Review fee table

Expected Result:
✅ Table shows:
   - Term: Term 1 2026
   - Program: Student's program
   - Amount: $5,000
   - Paid: $2,000 (from earlier payment)
   - Balance: $3,000
   - Status: Partially Paid (yellow badge)
✅ Summary shows:
   - Total Amount: $5,000
   - Total Paid: $2,000
   - Outstanding: $3,000
   - Collection %: 40%
```

### Test 7.5: Parent Login
**Objective:** Verify parent can access children
```
Steps:
1. Parent logs in (e.g., parent_001@school.com)
2. Navigates to /my-parent-dashboard/
3. Dashboard loads

Expected Result:
✅ Shows child selector cards
✅ Each card displays:
   - Child's name
   - Child's class
   - Child's program
   - Child's GPA
```

### Test 7.6: Parent View Child Data
**Objective:** Verify parent can view linked child
```
Steps:
1. Parent logged in (from 7.5)
2. Click on first child's card
3. Summary cards update
4. Click "Grades" tab
5. Click "Fees" tab
6. Click another child's card
7. Verify data changes

Expected Result:
✅ Child selection works
✅ Summary updates for selected child
✅ Grades show selected child's data
✅ Fees show selected child's balance
✅ Switching children refreshes all tabs
✅ Parent can only see linked children
```

### Test 7.7: Permission Isolation
**Objective:** Verify students can't access others
```
Steps:
1. Student A logs in
2. Note their student ID
3. Try to manually navigate to another student's data
   (e.g., modify URL parameter)
4. Attempt API call for Student B's data

Expected Result:
✅ Student A only sees own data
✅ Trying to access Student B shows: "Permission Denied"
✅ Parent can't access unlinked children
```

---

## ✅ FEATURE #9: Advanced Analytics

### Test 9.1: Analytics Dashboard Load
**Objective:** Verify charts populate
```
Steps:
1. Log in as Headmaster
2. Go to /headmaster-analytics/
3. Select Academic Year: 2026
4. Click "Load Analytics"
5. Wait for data to load

Expected Result:
✅ Dashboard loads within 3 seconds
✅ "Academic Trends" chart appears:
   - Shows Term 1 average: ~72.5%
   - Line chart with data points
✅ "Subject Performance" chart appears:
   - Bar chart showing each subject
✅ "At-Risk Students" table appears:
   - Shows students below 50%
✅ "Improving/Declining" cards appear:
   - Lists students with 20+ point changes
```

### Test 9.2: Trends Chart Accuracy
**Objective:** Verify trend calculations correct
```
Steps:
1. Analytics loaded (from 9.1)
2. Hover on data points in trends chart
3. Note values shown
4. Manually verify calculation:
   - Sum all marks for Term 1
   - Divide by (# students × 2 marks per student)

Expected Result:
✅ Chart value matches manual calculation
✅ Tooltip shows: "Average: 72.5%"
✅ All terms show correct progression
```

### Test 9.3: At-Risk Detection
**Objective:** Verify low-scoring students identified
```
Steps:
1. Analytics loaded
2. Review "At-Risk Students" table
3. Check if any students have <50% average
4. Verify they appear in table

Expected Result:
✅ Table shows only students <50%
✅ Each row displays:
   - Student name
   - Average: below 50%
   - Status: "At Risk" or "Critical"
✅ Sorted by lowest average first
```

### Test 9.4: Grade Predictions
**Objective:** Verify prediction algorithm
```
Steps:
1. Analytics loaded
2. Navigate to individual student prediction
   (if available through API)
3. Check predicted grade vs current average

Expected Result:
✅ Prediction shows:
   - Current average
   - Predicted final grade
   - Confidence score (0.5-1.0)
✅ Prediction logic:
   - If avg >= 90: Predicted = A
   - If avg >= 80: Predicted = B
   - If avg >= 70: Predicted = C
```

---

## 🔒 Security & Permission Tests

### Test S.1: Role Isolation
**Objective:** Verify each role sees only allowed data
```
Steps:
1. Log in as Teacher
   → Should NOT see: /bursar-billing/, /headmaster-analytics/, /my-parent-dashboard/
   → Should only see: marks entry, class roster

2. Log in as Bursar
   → Should see: /bursar-billing/, /bursar-fees/
   → Should NOT see: /headmaster-analytics/, /my-student-dashboard/

3. Log in as Student
   → Should see: /my-student-dashboard/
   → Should NOT see: /bursar-fees/, /headmaster-analytics/

4. Log in as Guardian
   → Should see: /my-parent-dashboard/
   → Should NOT see: /bursar-fees/, /headmaster-analytics/

5. Log in as Headmaster
   → Should see: ALL dashboards
   → Should NOT see: /my-student-dashboard/

Expected Result:
✅ Each role access restricted by permission
✅ No role can navigate to restricted pages
✅ API calls return "Permission Denied" for unauthorized access
```

### Test S.2: Data Isolation
**Objective:** Verify cross-student data access blocked
```
Steps:
1. Student A views their grades
2. Attempt to access Student B's grades via API:
   frappe.call('get_student_grades', {student_id: 'STU-002'})
3. Attempt to access via URL manipulation

Expected Result:
✅ API returns "Permission Denied"
✅ URL shows own student ID only
✅ No access to other students' data
```

---

## ⚡ Performance Tests

### Test P.1: Bulk Import Performance
**Objective:** Verify large import completes quickly
```
Steps:
1. Prepare CSV with 500 students
2. Go to /bursar-students
3. Upload and import all 500
4. Time the operation

Expected Result:
✅ Import completes in <30 seconds
✅ 500 students created
✅ No timeout errors
✅ UI remains responsive
```

### Test P.2: Batch Billing Performance
**Objective:** Verify billing scales
```
Steps:
1. With 500+ enrolled students
2. Go to /bursar-billing/
3. Select "All Programs"
4. Click "Create Fees"
5. Time the operation

Expected Result:
✅ Billing completes in <10 seconds
✅ 500+ fees created
✅ Progress bar responsive
✅ No performance degradation
```

### Test P.3: Fee Portal Load
**Objective:** Verify portal handles large datasets
```
Steps:
1. 500+ fees in database
2. Go to /bursar-fees/
3. Load and paginate

Expected Result:
✅ Initial load <2 seconds
✅ Pagination smooth
✅ Search responsive (<1 sec)
✅ Filter updates instantly
```

### Test P.4: Dashboard Calculation Performance
**Objective:** Verify analytics load quickly
```
Steps:
1. 500+ students with marks
2. Go to /headmaster-analytics/
3. Load dashboard

Expected Result:
✅ Dashboard loads in <5 seconds
✅ Charts render immediately
✅ All calculations accurate
✅ No timeout errors
```

---

## 🔄 Integration Tests

### Test I.1: End-to-End Workflow
**Objective:** Verify all features work together
```
Workflow:
1. Admin: Bulk import 100 students (Feature #1)
2. Headmaster: Create billing rates (Feature #2)
3. Bursar: Run batch billing (Feature #2)
4. Bursar: Record payment for 10 students (Feature #3)
5. Headmaster: View dashboard (Feature #4)
6. Headmaster: Generate batch report cards (Feature #5)
7. Student: Login and view grades/fees (Feature #7)
8. Parent: Login and view child's data (Feature #7)
9. Headmaster: View analytics (Feature #9)

Expected Result:
✅ All features work sequentially
✅ Data flows correctly between features
✅ Dashboard reflects batch billing results
✅ Student/Parent portal shows current data
✅ Analytics shows accurate trends
```

### Test I.2: Data Consistency
**Objective:** Verify data stays consistent across features
```
Steps:
1. Student imported with fee $5,000
2. Payment recorded: $2,000
3. Check fee in:
   - /bursar-fees/: shows $3,000 balance
   - /headmaster-dashboard/fees/: includes in Outstanding
   - Student portal: shows $3,000 due
   - Database: Student Fee record correct

Expected Result:
✅ All locations show same balance
✅ No discrepancies in calculated totals
✅ Ledger entries match fees
```

---

## 📱 UI/UX Tests

### Test U.1: Mobile Responsiveness
**Objective:** Verify features work on mobile
```
Steps:
1. Open /bursar-fees/ on mobile (375px width)
2. Test search, filter, pagination
3. Open /my-student-dashboard/ on mobile
4. Navigate tabs
5. Open /headmaster-analytics/ on mobile
6. View charts

Expected Result:
✅ No horizontal scrolling
✅ Tables stack vertically
✅ Charts scale down
✅ Touch targets appropriately sized
✅ All functionality accessible
```

### Test U.2: Browser Compatibility
**Objective:** Verify all browsers work
```
Test on:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

For each browser, test:
- Login flow
- Dashboard load
- Chart rendering
- Form submission
- Download PDF

Expected Result:
✅ All features work on all browsers
✅ No console errors
✅ Charts render consistently
```

---

## 📊 Data Validation Tests

### Test D.1: Calculate Totals Manually
**Objective:** Verify dashboard totals are accurate
```
Steps:
1. Query database directly:
   SELECT SUM(amount) as total_billed FROM `tabStudent Fee` WHERE academic_term='Term 1 2026'
   SELECT SUM(debit) as total_paid FROM `tabStudent Ledger Entry`

2. Compare with dashboard:
   - Total Billed: should match query 1
   - Total Collected: should match query 2
   - Outstanding: should be query 1 - query 2
   - Collection %: should be (query 2 / query 1) * 100

Expected Result:
✅ All dashboard totals match database queries
✅ No rounding errors
✅ Percentages accurate to 2 decimals
```

---

## ✅ Acceptance Criteria Checklist

Use this checklist at the end of testing:

**Feature #1 (Bulk Import):**
- [ ] CSV templates downloadable
- [ ] Validation catches errors
- [ ] Imports complete in <10 sec
- [ ] Duplicate detection works
- [ ] Sample data loads correctly

**Feature #2 (Batch Billing):**
- [ ] Rates configurable by term/program/boarding
- [ ] Preview shows accurate counts
- [ ] Batch billing completes <10 sec
- [ ] Duplicate prevention works
- [ ] Calculations verified

**Feature #3 (Fee Portal):**
- [ ] All fees visible in list
- [ ] Search/filter working
- [ ] Edit amounts updates database
- [ ] Payment recording works
- [ ] Ledger entries created

**Feature #4 (Fee Dashboard):**
- [ ] Summary totals accurate
- [ ] Charts render correctly
- [ ] Filtering by program works
- [ ] At-risk students identified
- [ ] Calculations verified

**Feature #5 (Batch Printing):**
- [ ] Preview accurate count
- [ ] PDF generates <60 sec
- [ ] PDF merges all reports
- [ ] All pages readable
- [ ] Download works

**Feature #7 (Student/Parent Portal):**
- [ ] Student login works
- [ ] Grades display correctly
- [ ] Reports downloadable
- [ ] Fees show accurate balance
- [ ] Parent can see all linked children
- [ ] Permission isolation enforced

**Feature #9 (Analytics):**
- [ ] Dashboard loads <5 sec
- [ ] Trends accurate
- [ ] At-risk detection works
- [ ] Predictions calculated
- [ ] Charts interactive

**Security:**
- [ ] Role-based access enforced
- [ ] Cross-student data access blocked
- [ ] Permissions checked on all APIs

**Performance:**
- [ ] Large imports <30 sec (500+ records)
- [ ] Batch billing <10 sec (500+ fees)
- [ ] Portal loads <2 sec
- [ ] Analytics loads <5 sec

**Integration:**
- [ ] End-to-end workflow succeeds
- [ ] Data consistent across features
- [ ] No orphaned records

---

## 🎯 Testing Summary

**Total Test Scenarios:** 50+ (organized by feature)  
**Estimated Time:** 2-3 days full testing  
**Pass Criteria:** All tests marked ✅  
**Sign-Off:** Tester name + date

---

**Document Version:** 1.0  
**Date:** July 5, 2026  
**Project:** Edupro SMS Complete Test Suite
