# Phase 1: Implementation Tasks — CSV Import + Student Management

**Phase:** 1 of 6  
**Target Duration:** 2 weeks  
**Features:** #1 (CSV Import) + #6 (Bursar Student Management)  
**Status:** 🟢 IN PROGRESS  

---

## 📋 Task Breakdown

### FEATURE #1: CSV IMPORT WITH TEMPLATE DOWNLOAD

#### Task 1.1: Create Template Generator Module
**Objective:** Build utility to generate pre-formatted Excel/CSV templates  
**Status:** ✅ COMPLETE  
**Completion Date:** 2026-07-05  

**Files Created:**
- `edupro_sms/template_generator.py` (345 lines) — Main module
  - Function: `generate_student_template()` → Excel file with headers: name, email, DOB, gender, ID, boarding_type, program, student_group
  - Function: `generate_instructor_template()` → Excel file with headers: name, email, subjects (comma-separated), class_teacher_flag
  - Function: `generate_guardian_template()` → Excel file with headers: name, email, student_ids (comma-separated)
  - Function: `generate_assessment_plan_template()` → Excel file with headers: student_group, course, academic_term, schedule_date, criteria_names (comma-separated)
  - Function: `@frappe.whitelist() download_template(template_type)` — Whitelisted download method

**Deliverables:**
- ✅ All 4 template functions implemented with openpyxl
- ✅ Professional styling: blue headers, white fonts, proper column widths
- ✅ Sample data rows (3 per template) showing correct format
- ✅ Instructions sheet on each template with validation rules
- ✅ Handles ImportError gracefully (openpyxl check)
- ✅ Returns file path for Frappe to serve

**Subtasks:**
- ✅ Install openpyxl library (Excel generation)
- ✅ Create function stubs
- ✅ Generate test templates
- ✅ Add sample data rows (showing format)
- ✅ Test Excel file generation structure

**Actual Time:** 1 hour (well ahead of 2-3 day estimate)

---

#### Task 1.2: Create CSV/Excel Parser & Validator
**Objective:** Parse uploaded CSV/Excel files and validate data integrity  
**Status:** ✅ COMPLETE  
**Completion Date:** 2026-07-05  

**Files Created:**
- `edupro_sms/import_parser.py` (549 lines) — Main module
  - Class: `ValidationError` — Single error object with row/field/message
  - Class: `RecordValidator` (base) — Common validation methods
  - Class: `StudentValidator` — Student-specific validation
  - Class: `InstructorValidator` — Instructor-specific validation
  - Class: `GuardianValidator` — Guardian-specific validation
  - Class: `AssessmentPlanValidator` — Assessment plan-specific validation
  - Function: `parse_csv_file(file_path)` → Returns headers, records, parse_errors
  - Function: `parse_excel_file(file_path, sheet_name)` → Handles xlsx with openpyxl
  - Function: `@frappe.whitelist() parse_and_validate_file(file_path, doctype)` → Complete validation

**Validation Features:**
- ✅ Student: email uniqueness, program/class existence, boarding type enum
- ✅ Instructor: email uniqueness, class teacher logic, subject validation
- ✅ Guardian: email uniqueness, student ID existence, comma-separated parsing
- ✅ Assessment Plan: class/subject/term existence, date format validation
- ✅ Email format validation for all
- ✅ Date format (YYYY-MM-DD) validation
- ✅ Gender enum (M/F) validation
- ✅ Required field checking
- ✅ Detailed error reports with row numbers & messages
- ✅ Skips empty rows in Excel
- ✅ Skips "Instructions" sheet in Excel files
- ✅ Large file support (efficient iteration)

**Subtasks:**
- ✅ Create validation rules for each DocType
- ✅ Handle missing/invalid data gracefully
- ✅ Create error report structure (shows which rows have errors)
- ✅ Support CSV and Excel parsing
- ✅ Database integration for existence checks

**Actual Time:** 2 hours (well ahead of 3-4 day estimate)

---

#### Task 1.3: Build Import API (Whitelisted Server Method)
**Objective:** Create whitelisted server-side method that accepts file upload and processes import  
**Status:** ✅ COMPLETE  
**Completion Date:** 2026-07-05  

**Files Created:**
- `edupro_sms/import_handler.py` (404 lines) — Main module
  - Class: `ImportLog` — Audit trail for import operations (timestamps, user, success/skip/error counts)
  - Function: `create_student_from_record()` — Create Student with enrollment
  - Function: `create_instructor_from_record()` — Create User + Instructor + class teacher assignment
  - Function: `create_guardian_from_record()` — Create Guardian with student links
  - Function: `create_assessment_plan_from_record()` — Create Assessment Plan
  - Function: `@frappe.whitelist() import_bulk_data()` — Main API with preview/import modes
  - Function: `get_import_history()` — Retrieves recent imports

**Core Features:**
- ✅ Preview mode (shows first 5 records, valid/invalid counts, no database changes)
- ✅ Actual import mode (creates DocType instances with transaction rollback on error)
- ✅ Duplicate detection per DocType (email, student group, etc.)
- ✅ Automatic Program Enrollment for students
- ✅ Class teacher assignment for instructors
- ✅ Guardian-to-student linking with multiple students
- ✅ Audit logging (user, timestamp, records imported/skipped/failed)
- ✅ Permission checks (requires 'create' permission)
- ✅ Transaction rollback on any error (all-or-nothing import)
- ✅ Detailed error tracking per row with reasons

**Subtasks:**
- ✅ Create preview mode (shows first 5 records, total count)
- ✅ Implement rollback on error (frappe.db.begin/commit/rollback)
- ✅ Add progress tracking (ImportLog class)
- ✅ Handle duplicate detection per DocType
- ✅ Support DocType-specific business logic (enrollments, class teachers, etc.)

**Actual Time:** 1.5 hours (well ahead of 3-4 day estimate)

---

#### Task 1.4: Build Import UI (Website Page)
**Objective:** Create website page for users to download templates and upload files  
**Status:** ✅ COMPLETE  
**Completion Date:** 2026-07-05  

**Files Created:**
- `edupro_sms/www/import-data/index.html` (478 lines) — Frontend form
  - Download template buttons (Student, Instructor, Guardian, Assessment Plan) with icons
  - Data type selector dropdown
  - File upload input (accepts .csv, .xlsx)
  - Validate button (triggers parse_and_validate_file API call)
  - Progress bar (shown during validation)
  - Validation summary (Total, Valid, Invalid counts)
  - Preview table (first 5 records)
  - Error table (first 10 errors with row/field/value/message)
  - Proceed with Import button (disabled until validation passes)
  - Complete card (shows success/skip/fail counts)
  - Professional styling with Edupro brand colors (red/gray)

- `edupro_sms/www/import-data/index.py` (61 lines) — Backend context
  - Function: `get_context()` returns available doctypes for import
  - Permission check: Only users with 'create' permission on Student
  - Data types metadata: Student, Instructor, Guardian, Assessment Plan
  - Page metadata: title, description, no_cache flag

**Frontend Features:**
- ✅ 4 template download buttons with icons
- ✅ Data type selector with 4 options
- ✅ File upload with format validation (.csv, .xlsx)
- ✅ Validate button triggers backend validation
- ✅ Progress bar during validation
- ✅ Validation summary: Total/Valid/Invalid counts
- ✅ Preview table: Shows first 5 valid records
- ✅ Error table: Shows first 10 errors with details (row, field, value, message)
- ✅ Proceed with Import button (only enabled if valid records exist)
- ✅ Confirmation dialog before actual import
- ✅ Import complete card with detailed results
- ✅ Start Over button to reset form
- ✅ Responsive design (works on desktop & tablet)
- ✅ Professional styling with Edupro brand (red/gray palette)

**Subtasks:**
- ✅ Create HTML form with 4 download buttons
- ✅ Implement file upload handler with validation
- ✅ Add AJAX calls to both parser (preview) and import APIs
- ✅ Display progress bar during validation
- ✅ Show error messages with row numbers & details
- ✅ Add confirmation modal before actual import

**Actual Time:** 2 hours (well ahead of 2-3 day estimate)

---

#### Task 1.5: Testing & Documentation
**Objective:** Test entire import flow and document for users  
**Subtasks:**
- [ ] Test with 100+ student records
- [ ] Test with intentional errors (bad email, missing name, etc.)
- [ ] Test rollback on failure
- [ ] Performance test (how fast for 1,000 records?)
- [ ] Update INSTALLATION_GUIDE.md with CSV import instructions
- [ ] Create FAQ: "What if import fails?"

**Estimated Time:** 2-3 days

---

### FEATURE #6: BURSAR STUDENT MANAGEMENT

#### Task 6.1: Create Student Management API (Whitelisted Methods)
**Objective:** Build server-side methods for Bursar to manage students  
**Status:** ✅ COMPLETE  
**Completion Date:** 2026-07-05  

**Files Created:**
- `edupro_sms/bursar_student_management.py` (508 lines) — Main module
  - Function: `create_student(student_name, email, dob, gender, admission_number, boarding_type)` (whitelisted)
  - Function: `enroll_student(student_id, program, student_group, academic_year)` (whitelisted)
  - Function: `link_guardian(student_id, guardian_id, create_new, guardian_name, guardian_email)` (whitelisted)
  - Function: `edit_student(student_id, field_name, field_value)` (whitelisted)
  - Function: `deactivate_student(student_id, reason)` (whitelisted)
  - Function: `get_student_list(status, limit)` (whitelisted)
  - Helper: `has_bursar_permission()` - Permission check wrapper
  - Helper: `log_audit()` - Audit trail logging

**Validation & Features:**
- ✅ create_student: Email/admission uniqueness, gender enum, boarding type enum
- ✅ enroll_student: Auto-link to Program, handles duplicate enrollments, auto-current academic year
- ✅ link_guardian: Create new guardian or link existing, email uniqueness, duplicate prevention
- ✅ edit_student: Limited to non-security fields (name, email, dob, gender, boarding_type, status)
- ✅ deactivate_student: Soft delete with reason logging
- ✅ get_student_list: Filtered by status, paginated
- ✅ All functions permission-checked (Bursar role required)
- ✅ All functions audit-logged (user, action, changes)
- ✅ Duplicate detection (email, admission number, enrollments)
- ✅ Comprehensive error handling & user-friendly messages
- ✅ Field validation (email format, date, enums)
- ✅ Transaction safety (rollback on error)

**Subtasks:**
- ✅ Create validation for each function (email, enums, uniqueness)
- ✅ Check Bursar permissions on each function
- ✅ Add audit logging (log_audit helper function)
- ✅ Handle errors gracefully (duplicate email, invalid class, etc.)
- ✅ Support guardian creation inline (create_new parameter)

**Actual Time:** 1.5 hours (well ahead of 3-4 day estimate)

---

#### Task 6.2: Update DocType Permissions
**Objective:** Grant Bursar CRUD permissions on Student, Guardian, Program Enrollment  
**Status:** ✅ COMPLETE  
**Completion Date:** 2026-07-05  

**Files Modified:**
- `edupro_sms/fixtures/role.json` (added Bursar role)
  - New entry: Bursar role with desk_access=1

- `edupro_sms/fixtures/custom_docperm.json` (added 3 permission rules)
  - Bursar on Student: create, read, write, print (no delete/report/share)
  - Bursar on Guardian: create, read, write, print (no delete/report/share)
  - Bursar on Program Enrollment: create, read, print (no write/delete after creation)

**Permission Details:**
- ✅ Student: Bursar can create, read, write (including name, email, dob, gender, etc.)
- ✅ Guardian: Bursar can create, read, write
- ✅ Program Enrollment: Bursar can create, read but cannot modify after creation
- ✅ All: No delete permission (prevents accidental purging)
- ✅ All: Audit logging via existing row-level permission scoping

**Validation:**
- ✅ Bursar role created with desk_access enabled (can access Frappe Desk)
- ✅ Row-level scoping already in place (student_permissions.py includes Bursar in unrestricted roles)
- ✅ Non-Bursar roles unaffected (existing permissions preserved)
- ✅ Field-level restrictions via bursar_student_management.py (edit_student only allows safe fields)

**Subtasks:**
- ✅ Add Bursar role to role.json
- ✅ Add Bursar permissions to custom_docperm.json
- ✅ Verify row-level scoping includes Bursar (already in student_permissions.py)
- ✅ Bursar can create but not delete
- ✅ Bursar cannot edit security-sensitive fields (enforced in API)

**Actual Time:** 0.5 hours (quick setup)

---

#### Task 6.3: Build Bursar Student Management UI
**Objective:** Create website pages for Bursar to manage students  
**Status:** ✅ COMPLETE  
**Completion Date:** 2026-07-05  

**Files Created:**
- `edupro_sms/www/bursar-students/index.html` (613 lines) — Main page
  - Student list table (searchable, filterable, paginated)
  - Search by name, email, admission number
  - Filter by status (Active/Inactive), boarding type
  - Quick actions: Add Student, Bulk Import, Filters
  - Pagination (20 records per page)
  - Row counts: Total, Active, Inactive
  - Action buttons per student: Edit, Enroll, Link Guardian, Deactivate
  - Modals for enrollment, guardian linking, deactivation

- `edupro_sms/www/bursar-students/index.py` (32 lines) — Backend
  - Permission check (Bursar role required)
  - Page metadata & context setup
  - no_cache flag

- `edupro_sms/www/bursar-students/add-student.html` (289 lines) — Add student form
  - Form fields: Name, Email, DOB, Gender, Admission Number, Boarding Type, Program (optional), Class (optional)
  - Real-time program/class dropdown loading
  - Form validation (email format, required fields)
  - Auto-enrollment if program selected
  - Success message with redirect

- `edupro_sms/www/bursar-students/edit-student.html` (336 lines) — Edit student form
  - Pre-filled data from existing student
  - Edit fields: Name, Email, DOB, Gender, Admission Number, Boarding Type, Status
  - Back link to student list
  - Separate deactivate card with confirmation modal
  - Field change detection (only save changed fields)
  - Read-only Student ID field

**UI Features:**
- ✅ Student list with real-time filtering/search
- ✅ Pagination (20 records/page)
- ✅ Quick action buttons (Edit, Enroll, Link Guardian, Deactivate)
- ✅ Add student form with validation
- ✅ Edit student form with change detection
- ✅ Enrollment modal (select program & class)
- ✅ Guardian linking modal (link existing or create new inline)
- ✅ Deactivate confirmation modal with reason capture
- ✅ Responsive design (mobile & desktop)
- ✅ Edupro brand styling (red/gray palette)
- ✅ Status badges (Active/Inactive)
- ✅ Pagination controls with next/prev

**Integration:**
- ✅ Calls bursar_student_management API methods
- ✅ Links to CSV import feature (/import-data)
- ✅ Uses Frappe client.get_list for programs/classes/guardians

**Subtasks:**
- ✅ Create student list table (searchable, filterable, paginated)
- ✅ Create add student form with validation
- ✅ Create edit student form with pre-filled data
- ✅ Add AJAX calls to backend API
- ✅ Show success/error messages (frappe.msgprint)
- ✅ Add enrollment modal (select program & class)
- ✅ Add guardian linking modal (link or create)
- ✅ Add deactivate confirmation modal

**Actual Time:** 3 hours (well ahead of 4-5 day estimate)

---

#### Task 6.4: Testing & Documentation
**Objective:** Test entire student management flow and document for Bursar  
**Subtasks:**
- [ ] Test creating 10+ students
- [ ] Test enrolling student in program
- [ ] Test linking guardian to student
- [ ] Test editing student info
- [ ] Test deactivating student (verify soft delete, not hard delete)
- [ ] Test bulk import (Feature #1 + Feature #6 together)
- [ ] Update USER_QUICKSTART.md with Bursar student management guide
- [ ] Create FAQ: "How to add a new student?"

**Estimated Time:** 2-3 days

---

## 📊 Overall Task Summary

### Feature #1: CSV Import (Tasks 1.1-1.5)
- **Total Time:** 12-17 days
- **Critical Path:** Template Generator → Parser → API → UI → Testing
- **Dependencies:** openpyxl library (pip install)

### Feature #6: Student Management (Tasks 6.1-6.4)
- **Total Time:** 10-13 days
- **Critical Path:** API → Permissions → UI → Testing
- **Dependencies:** Feature #1 should complete first (for bulk import in Bursar UI)

### **Phase 1 Total: 22-30 days (~3-4 weeks, single developer)**

---

## 🔄 Implementation Sequence

**Week 1:** Features #1 (CSV Import)
- Days 1-3: Template Generator + Parser
- Days 4-5: Import API + UI
- Days 5-7: Testing & Docs

**Week 2:** Feature #6 (Student Management)
- Days 8-10: Student Management API + Permissions
- Days 11-14: Student Management UI
- Days 14-15: Testing & Docs

**Week 3:** Integration & Testing
- Days 16-17: Integration testing (CSV import in Bursar UI)
- Days 18-20: Bug fixes from testing
- Days 20-22: Final QA & documentation

---

## ✅ Acceptance Criteria

### Feature #1 (CSV Import) - DONE when:
- [ ] Templates downloadable for Student, Instructor, Guardian, Assessment Plan
- [ ] Files can be uploaded and validated
- [ ] Preview shows 5 sample records before import
- [ ] Import executes and shows success/error count
- [ ] Large files (1,000+ rows) process in <5 minutes
- [ ] Errors are clear and actionable
- [ ] Documentation complete in INSTALLATION_GUIDE.md

### Feature #6 (Student Management) - DONE when:
- [ ] Bursar can add new students via form
- [ ] Bursar can enroll student in program
- [ ] Bursar can link student to guardian
- [ ] Bursar can edit student info
- [ ] Bursar can deactivate student
- [ ] Bursar can bulk import students via CSV
- [ ] All changes logged in audit trail
- [ ] Documentation complete in USER_QUICKSTART.md
- [ ] Unit tests pass (12+ tests minimum)

---

## 🐛 Known Issues & Notes

- **Issue:** File upload size limit — may need to configure server
  - Mitigation: Test with 10MB+ files, adjust if needed

- **Issue:** Email uniqueness — must check system-wide
  - Mitigation: Query Frappe's User + Student tables before allowing create

- **Issue:** Performance — parsing 10,000 rows might be slow
  - Mitigation: Use background job (RQ) for imports >5,000 rows

---

## 📝 Files to Create/Modify

**New Files:**
```
edupro_sms/template_generator.py
edupro_sms/import_parser.py
edupro_sms/import_handler.py
edupro_sms/bursar_student_management.py
edupro_sms/www/import-data/index.html
edupro_sms/www/import-data/index.py
edupro_sms/www/bursar-students/index.html
edupro_sms/www/bursar-students/index.py
edupro_sms/www/bursar-students/add-student.html
edupro_sms/www/bursar-students/edit-student.html
```

**Modified Files:**
```
edupro_sms/fixtures/permission.json (add Bursar permissions)
edupro_sms/doctype/student/student.json (add Bursar perms)
edupro_sms/doctype/guardian/guardian.json (add Bursar perms)
edupro_sms/doctype/program_enrollment/program_enrollment.json (add Bursar perms)
docs/11_Roles_And_Permissions.md (update Bursar capability matrix)
USER_QUICKSTART.md (add Bursar guides)
INSTALLATION_GUIDE.md (add CSV import guide)
```

---

## 🚀 Getting Started (Next Steps)

1. ✅ **Task 1.1 (Template Generator)** — Start here
   - Create `template_generator.py`
   - Implement `generate_student_template()` function
   - Test Excel file generation

2. Parallel: **Task 6.1 (Student Management API)**
   - Create `bursar_student_management.py`
   - Implement validation functions

---

**Document Version:** 1.0  
**Date:** July 5, 2026  
**Status:** 🟢 READY TO IMPLEMENT
