# Phase 1 Testing & Acceptance Criteria

**Status:** Ready for Testing  
**Date:** July 5, 2026  
**Features:** CSV Import (#1) + Bursar Student Management (#6)

---

## 1. CSV IMPORT TESTING (Feature #1)

### 1.1 Template Generation Tests

```
Test 1.1.1: Student Template Download
  Steps:
    1. Navigate to /import-data
    2. Click "Student Template" download button
    3. Verify Excel file downloads
    4. Open file in Excel/LibreOffice
  Expected:
    ✓ File downloads with name pattern: student_import_template_*.xlsx
    ✓ Header row: Student Name, Email, DOB, Gender, Admission Number, Boarding Type, Program, Student Group
    ✓ Blue header with white text
    ✓ 3 sample data rows
    ✓ Instructions sheet included
  Status: [ ]
```

```
Test 1.1.2: All Four Templates Available
  Steps:
    1. On /import-data
    2. Verify 4 download buttons: Student, Instructor, Guardian, Assessment Plan
  Expected:
    ✓ All 4 templates download successfully
    ✓ Each has correct headers for its type
    ✓ Each has sample data & instructions
  Status: [ ]
```

### 1.2 File Upload & Validation Tests

```
Test 1.2.1: CSV File Upload & Validation
  Steps:
    1. Download Student template
    2. Fill 5 rows with valid data
    3. Save as CSV
    4. On /import-data, select "Student" type
    5. Upload CSV file
    6. Click "Validate"
  Expected:
    ✓ Progress bar appears
    ✓ Validation completes in <10 seconds
    ✓ Shows: Total=5, Valid=5, Invalid=0
    ✓ Preview table shows all 5 records
    ✓ "Proceed with Import" button enabled
  Status: [ ]
```

```
Test 1.2.2: Excel File Upload & Validation
  Steps:
    1. Download Student template (already Excel)
    2. Fill 10 rows with valid data
    3. On /import-data, select "Student" type
    4. Upload XLSX file
    5. Click "Validate"
  Expected:
    ✓ File uploads and validates
    ✓ Total=10, Valid=10, Invalid=0
    ✓ Preview shows first 5 of 10
    ✓ Import button enabled
  Status: [ ]
```

```
Test 1.2.3: Error Detection - Invalid Email
  Steps:
    1. Template: Fill 3 rows, row 2 has invalid email (no @)
    2. Validate
  Expected:
    ✓ Total=3, Valid=2, Invalid=1
    ✓ Error table shows row 2
    ✓ Error message: "Invalid email format"
    ✓ Field value shown in error
  Status: [ ]
```

```
Test 1.2.4: Error Detection - Duplicate Email
  Steps:
    1. Template: Fill 3 rows, rows 1 and 2 have same email
    2. Validate
  Expected:
    ✓ Row 2 flagged as error
    ✓ Error message: "Email already exists"
  Status: [ ]
```

```
Test 1.2.5: Error Detection - Missing Required Fields
  Steps:
    1. Template: Fill 2 rows, row 1 missing "Student Name"
    2. Validate
  Expected:
    ✓ Row 1 flagged as error
    ✓ Error: "Required field 'Student Name' is missing"
  Status: [ ]
```

```
Test 1.2.6: Error Detection - Invalid Enum Values
  Steps:
    1. Template: Row 1 has Boarding Type = "Half Boarder" (invalid)
    2. Validate
  Expected:
    ✓ Row 1 flagged
    ✓ Error: "Boarding Type must be 'Day Boarder' or 'Full Boarder'"
  Status: [ ]
```

### 1.3 Preview Mode Tests

```
Test 1.3.1: Preview Shows 5 Sample Records
  Steps:
    1. Upload CSV with 20 valid records
    2. Validate
    3. Check preview table
  Expected:
    ✓ Preview table shows first 5 records only
    ✓ All 5 columns visible (Student Name, Email, DOB, Gender, Admission #)
    ✓ Message shows: "Total Valid: 20"
    ✓ "Proceed with Import" button available
  Status: [ ]
```

```
Test 1.3.2: No Data Changes in Preview Mode
  Steps:
    1. Upload CSV with 10 records
    2. Validate (preview mode)
    3. Query Student table directly
  Expected:
    ✓ No students created during preview
    ✓ Database unchanged
    ✓ Only after user clicks "Proceed" does import happen
  Status: [ ]
```

### 1.4 Actual Import Tests

```
Test 1.4.1: Successful Import - 10 Students
  Steps:
    1. Upload CSV with 10 valid students
    2. Validate (shows preview)
    3. Click "Proceed with Import"
  Expected:
    ✓ Progress shows import in progress
    ✓ Completes in <5 seconds
    ✓ Message: "Import complete: 10 imported, 0 skipped, 0 failed"
    ✓ Import results card shows:
      - Imported: 10
      - Skipped: 0
      - Failed: 0
    ✓ Query DB: All 10 students created with correct data
  Status: [ ]
```

```
Test 1.4.2: Import with Duplicates - Skip Existing
  Steps:
    1. Create Student A manually in system
    2. Upload CSV with Student A (duplicate email)
    3. Import
  Expected:
    ✓ Import message: "X imported, 1 skipped, 0 failed"
    ✓ Error log shows: "Email already exists"
    ✓ No duplicate created
  Status: [ ]
```

```
Test 1.4.3: Large File Import (1,000+ Records)
  Steps:
    1. Generate CSV with 1,000 valid students
    2. Upload & validate
    3. Import
  Expected:
    ✓ Validation completes in <30 seconds
    ✓ Import completes in <5 minutes
    ✓ All 1,000 students created
    ✓ No timeouts or errors
  Status: [ ]
```

```
Test 1.4.4: Rollback on Error - All or Nothing
  Steps:
    1. CSV with 100 valid students but row 50 invalid
    2. Upload & import (should fail mid-way)
  Expected:
    ✓ Import fails at row 50
    ✓ Message: "Import failed and rolled back"
    ✓ Database check: 0 students created (rollback worked)
    ✓ No partial data in system
  Status: [ ]
```

### 1.5 Permission Tests

```
Test 1.5.1: Only Bursar/Admin Can Import
  Steps:
    1. Log in as Teacher
    2. Navigate to /import-data
  Expected:
    ✓ Permission error: "You do not have permission to access this page"
  Status: [ ]
```

---

## 2. STUDENT MANAGEMENT TESTING (Feature #6)

### 2.1 Student Creation Tests

```
Test 2.1.1: Create Student via Form
  Steps:
    1. Navigate to /bursar-students
    2. Click "Add Student"
    3. Fill form: Name, Email, DOB, Gender, Admission #, Boarding Type
    4. Click "Create Student"
  Expected:
    ✓ Form validates before submit
    ✓ Student created in database
    ✓ Success message: "Student created successfully"
    ✓ Redirects to /bursar-students
    ✓ New student appears in list
  Status: [ ]
```

```
Test 2.1.2: Email Uniqueness Validation
  Steps:
    1. Create Student A with email test@school.edu
    2. Try to create Student B with same email
  Expected:
    ✓ Error: "Email test@school.edu already exists"
    ✓ Student B not created
  Status: [ ]
```

```
Test 2.1.3: Admission Number Uniqueness
  Steps:
    1. Create Student A with admission # STU001
    2. Try to create Student B with STU001
  Expected:
    ✓ Error: "Admission number STU001 already exists"
  Status: [ ]
```

```
Test 2.1.4: Required Fields Validation
  Steps:
    1. Try to submit form with empty "Student Name"
  Expected:
    ✓ Form shows validation error
    ✓ Submit button disabled
  Status: [ ]
```

### 2.2 Student List & Search Tests

```
Test 2.2.1: Student List Displays All Students
  Steps:
    1. Create 25 students
    2. Navigate to /bursar-students
  Expected:
    ✓ First 20 students shown (paginated)
    ✓ Counter shows: Total=25, Active=25, Inactive=0
    ✓ Next page button enabled
  Status: [ ]
```

```
Test 2.2.2: Search by Name
  Steps:
    1. 5 students: John Doe, Jane Smith, Bob Wilson, Alice Brown, Charlie Davis
    2. In search box, type "John"
  Expected:
    ✓ Table filtered to show only "John Doe"
    ✓ Others hidden
  Status: [ ]
```

```
Test 2.2.3: Search by Email
  Steps:
    1. Type in search: "jane@"
  Expected:
    ✓ Table shows only Jane Smith
  Status: [ ]
```

```
Test 2.2.4: Filter by Status
  Steps:
    1. 10 Active, 5 Inactive students exist
    2. Filter Status = "Inactive"
  Expected:
    ✓ Table shows only 5 Inactive
    ✓ Counter shows: Total=5
  Status: [ ]
```

```
Test 2.2.5: Pagination Navigation
  Steps:
    1. 50 students created
    2. On page 1, click "Next"
  Expected:
    ✓ Shows records 21-40
    ✓ "Previous" button enabled
    ✓ Page indicator: "Page 2"
  Status: [ ]
```

### 2.3 Student Edit Tests

```
Test 2.3.1: Edit Student Name
  Steps:
    1. Create Student: "John Doe"
    2. Go to /bursar-students
    3. Click Edit on John Doe
    4. Change name to "Jonathan Doe"
    5. Save
  Expected:
    ✓ Form pre-fills with current data
    ✓ Change saves successfully
    ✓ List reflects new name
  Status: [ ]
```

```
Test 2.3.2: Edit Email with Uniqueness Check
  Steps:
    1. Student A email: john@school.edu
    2. Student B email: jane@school.edu
    3. Edit Student B, try to change to john@school.edu
  Expected:
    ✓ Error: "Email already used by another student"
    ✓ Not saved
  Status: [ ]
```

```
Test 2.3.3: Only Changed Fields Are Saved
  Steps:
    1. Edit Student, change only Name field
    2. Save
  Expected:
    ✓ Only Name is updated in DB
    ✓ Other fields unchanged
    ✓ Audit log records only Name change
  Status: [ ]
```

### 2.4 Student Enrollment Tests

```
Test 2.4.1: Enroll Student in Program
  Steps:
    1. Create Student
    2. On student list, click "Enroll" button
    3. Select Program: "IGCSE Science"
    4. Confirm
  Expected:
    ✓ Modal appears with programs dropdown
    ✓ Enrollment created in database
    ✓ Success message: "Student enrolled in IGCSE Science"
  Status: [ ]
```

```
Test 2.4.2: Auto-Current Academic Year
  Steps:
    1. Enroll student without specifying academic year
  Expected:
    ✓ System auto-uses current academic year
    ✓ No manual year selection needed
  Status: [ ]
```

```
Test 2.4.3: Prevent Duplicate Enrollment
  Steps:
    1. Enroll Student A in IGCSE Science
    2. Try to enroll Student A in IGCSE Science again
  Expected:
    ✓ Message: "Already enrolled in IGCSE Science"
    ✓ No duplicate enrollment created
  Status: [ ]
```

### 2.5 Guardian Linking Tests

```
Test 2.5.1: Link Existing Guardian
  Steps:
    1. Create Guardian (manually)
    2. Create Student
    3. Click "Link Guardian" on student
    4. Select existing guardian
  Expected:
    ✓ Modal shows list of guardians
    ✓ Linking successful
    ✓ Message: "Guardian linked to student"
  Status: [ ]
```

```
Test 2.5.2: Create New Guardian Inline
  Steps:
    1. Create Student
    2. Click "Link Guardian"
    3. Switch to "Create New" tab
    4. Fill: Guardian Name, Email
    5. Confirm
  Expected:
    ✓ New Guardian created
    ✓ Linked to student
    ✓ Success message
  Status: [ ]
```

```
Test 2.5.3: Prevent Duplicate Guardian Link
  Steps:
    1. Link Guardian G1 to Student S1
    2. Try to link Guardian G1 to S1 again
  Expected:
    ✓ Message: "Guardian already linked"
    ✓ No duplicate link
  Status: [ ]
```

### 2.6 Student Deactivation Tests

```
Test 2.6.1: Deactivate Student
  Steps:
    1. Create Active Student
    2. Click "Deactivate" on student
    3. Confirm with reason (optional)
  Expected:
    ✓ Confirmation modal appears
    ✓ Student status changes to "Inactive"
    ✓ List shows status badge as "Inactive"
    ✓ Audit log records deactivation + reason
  Status: [ ]
```

```
Test 2.6.2: Soft Delete (Not Hard Delete)
  Steps:
    1. Deactivate Student
    2. Query database directly
  Expected:
    ✓ Student record still exists
    ✓ Only status = "Inactive"
    ✓ All student data preserved
  Status: [ ]
```

### 2.7 Permission Tests

```
Test 2.7.1: Only Bursar Can Access Student Management
  Steps:
    1. Log in as Teacher
    2. Navigate to /bursar-students
  Expected:
    ✓ Permission error: "You do not have permission"
  Status: [ ]
```

```
Test 2.7.2: Bursar Can't See Other Schools' Students
  Steps:
    1. Create two schools (multi-tenancy)
    2. School A: Create 5 students
    3. School B Bursar: Logs in
    4. Check /bursar-students
  Expected:
    ✓ School B Bursar sees 0 students
    ✓ Row-level scoping prevents cross-school access
  Status: [ ]
```

---

## 3. INTEGRATION TESTS

```
Test 3.1: Full Workflow - Bulk Import → Student Management → Enrollment
  Steps:
    1. Generate CSV with 50 students
    2. Import via /import-data (Feature #1)
    3. Go to /bursar-students (Feature #6)
    4. Search for imported student
    5. Click Enroll
    6. Select program
  Expected:
    ✓ All 50 students appear in student list
    ✓ Search finds them by name/email
    ✓ Enrollment workflow works
    ✓ Student now enrolled in program
  Status: [ ]
```

```
Test 3.2: End-to-End: CSV Import + Enrollment + Guardian + Portal
  Steps:
    1. Import 10 students (CSV)
    2. Enroll all in program (Bursar UI)
    3. Link to guardians (Bursar UI)
    4. Student logs into portal
    5. Student sees grades area
  Expected:
    ✓ All steps succeed without error
    ✓ No permission issues
    ✓ Student data flows through system
  Status: [ ]
```

---

## 4. PERFORMANCE TESTS

```
Test 4.1: CSV Validation Speed
  Scenario: 1,000 student records
  Expected:
    ✓ Validation completes in <30 seconds
    ✓ No timeout errors
  Status: [ ]
```

```
Test 4.2: Import Speed
  Scenario: 100 students
  Expected:
    ✓ Import completes in <5 seconds
  Status: [ ]
```

```
Test 4.3: Student List Performance
  Scenario: 500 students in system
  Expected:
    ✓ List page loads in <2 seconds
    ✓ Search filters instantly (<1 sec)
  Status: [ ]
```

---

## 5. EDGE CASE TESTS

```
Test 5.1: Empty CSV Upload
  Steps:
    1. Upload empty CSV (headers only, no data)
  Expected:
    ✓ Validation completes
    ✓ Message: "No records to import"
  Status: [ ]
```

```
Test 5.2: Special Characters in Names
  Steps:
    1. Student name: "José María Pérez-López"
    2. Create/Import
  Expected:
    ✓ Data saved correctly with accents/hyphens
    ✓ Search works
  Status: [ ]
```

```
Test 5.3: Very Long Email
  Steps:
    1. Email: "student.with.very.long.email.address.test@school.edu"
    2. Create
  Expected:
    ✓ Saves successfully
    ✓ No truncation
  Status: [ ]
```

---

## ACCEPTANCE CRITERIA - SIGN OFF

Both features are DONE when:

### Feature #1 (CSV Import)
- [ ] All Template tests pass (1.1)
- [ ] All Upload & Validation tests pass (1.2)
- [ ] All Preview tests pass (1.3)
- [ ] All Import tests pass (1.4)
- [ ] Permission tests pass (1.5)
- [ ] Performance: 1000-row file validates in <30s
- [ ] Performance: 100-row import completes in <5s
- [ ] Integration test 3.1 passes
- [ ] Documentation updated (INSTALLATION_GUIDE.md)

### Feature #6 (Student Management)
- [ ] All Student Creation tests pass (2.1)
- [ ] All List & Search tests pass (2.2)
- [ ] All Edit tests pass (2.3)
- [ ] All Enrollment tests pass (2.4)
- [ ] All Guardian Linking tests pass (2.5)
- [ ] All Deactivation tests pass (2.6)
- [ ] All Permission tests pass (2.7)
- [ ] Integration test 3.2 passes
- [ ] Performance: 500-student list loads in <2s
- [ ] Documentation updated (USER_QUICKSTART.md)

---

## Testing Notes

- Run all tests in fresh database
- Test with Chrome, Firefox, Safari (if available)
- Test on desktop and mobile viewport
- Verify audit trail for all operations
- Check error messages are user-friendly
- Verify redirects work correctly

---

**Testing Date:** _______________  
**Tester Name:** _______________  
**Overall Result:** ✅ PASS / ❌ FAIL  

**Sign-Off:**
- Developer: _______________  Date: _______________
- QA: _______________  Date: _______________
