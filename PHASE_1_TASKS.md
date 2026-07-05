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
**Files to Create:**
- `edupro_sms/import_parser.py` — Main module
  - Function: `parse_csv_file(file_path, doctype)` → Returns list of validated records
  - Function: `validate_student_record(record)` → Checks required fields, email format, date format, etc.
  - Function: `validate_instructor_record(record)` → Checks email, subjects exist
  - Function: `validate_guardian_record(record)` → Checks email, student IDs exist
  - Function: `validate_assessment_plan_record(record)` → Checks class/subject/term exist

**Subtasks:**
- [ ] Create validation rules for each DocType
- [ ] Handle missing/invalid data gracefully
- [ ] Create error report (shows which rows have errors)
- [ ] Test with intentional bad data
- [ ] Test with large files (1,000+ rows)

**Estimated Time:** 3-4 days

---

#### Task 1.3: Build Import API (Whitelisted Server Method)
**Objective:** Create whitelisted server-side method that accepts file upload and processes import  
**Files to Modify:**
- `edupro_sms/import_handler.py` — New file
  - Function: `import_bulk_data(doctype, file_data, preview=True)` (whitelisted)
    - If preview=True: returns preview of 5 records + error count (user confirms before actual import)
    - If preview=False: performs actual import, returns success/failure count per record

**Subtasks:**
- [ ] Create preview mode (shows first 5 records, total count)
- [ ] Implement rollback on error (if validation fails, don't save anything)
- [ ] Add progress tracking (save import log with timestamp, user, record count)
- [ ] Handle duplicate detection (skip if student email already exists)
- [ ] Test end-to-end with mock data

**Estimated Time:** 3-4 days

---

#### Task 1.4: Build Import UI (Website Page)
**Objective:** Create website page for users to download templates and upload files  
**Files to Create:**
- `edupro_sms/www/import-data/index.html` — Frontend form
  - Download template buttons (Student, Instructor, Guardian, Assessment Plan)
  - File upload input (accepts .csv, .xlsx)
  - Progress bar (shows import progress)
  - Results display (success count, error count, error details)

- `edupro_sms/www/import-data/index.py` — Backend context
  - Function: `get_context()` returns available doctypes for import
  - Permission check: Only System Manager and Admin can import

**Subtasks:**
- [ ] Create HTML form with download buttons
- [ ] Implement file upload handler
- [ ] Add AJAX calls to import API
- [ ] Display progress bar with real-time updates
- [ ] Show error messages clearly (red text, line numbers)
- [ ] Add confirmation modal before actual import

**Estimated Time:** 2-3 days

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
**Files to Create:**
- `edupro_sms/bursar_student_management.py` — Main module
  - Function: `create_student(name, email, dob, gender, admission_number, boarding_type)` (whitelisted)
  - Function: `enroll_student(student_id, program, academic_year)` (whitelisted)
  - Function: `add_to_class(student_id, student_group)` (whitelisted)
  - Function: `link_guardian(student_id, guardian_id_or_create_new)` (whitelisted)
  - Function: `edit_student(student_id, fields_to_update)` (whitelisted)
  - Function: `deactivate_student(student_id, reason)` (whitelisted)

**Subtasks:**
- [ ] Create validation for each function
- [ ] Check Bursar permissions on each function
- [ ] Add audit logging (who changed what, when)
- [ ] Handle errors gracefully (duplicate email, invalid class, etc.)
- [ ] Test each function with mock data

**Estimated Time:** 3-4 days

---

#### Task 6.2: Update DocType Permissions
**Objective:** Grant Bursar CRUD permissions on Student, Guardian, Program Enrollment  
**Files to Modify:**
- `edupro_sms/edupro_sms/doctype/student/student.json`
  - Add Bursar role: create, read, write (no delete)
  - Fields Bursar can edit: name, email, dob, gender, admission_number, boarding_type, status
  - Fields Bursar CANNOT edit: user (security), student_id (auto-generated)

- `edupro_sms/edupro_sms/doctype/guardian/guardian.json`
  - Add Bursar role: create, read, write (no delete)

- `edupro_sms/edupro_sms/doctype/program_enrollment/program_enrollment.json`
  - Add Bursar role: create, read (no write/delete after created)

**Subtasks:**
- [ ] Update all three DocType permission JSONs
- [ ] Test that Bursar can create but not delete
- [ ] Test that Bursar cannot edit security-sensitive fields
- [ ] Verify non-Bursar roles unaffected

**Estimated Time:** 1 day

---

#### Task 6.3: Build Bursar Student Management UI
**Objective:** Create website pages for Bursar to manage students  
**Files to Create:**
- `edupro_sms/www/bursar-students/index.html` — Main page
  - Student list (searchable, filterable by status)
  - "Add New Student" button
  - "Bulk Import Students" button (uses CSV import from Feature #1)
  - Each student row shows: Name, Email, Class, Status, Actions (Edit, Deactivate)

- `edupro_sms/www/bursar-students/index.py` — Backend
  - Function: `get_context()` returns list of active students
  - Permission check: Only Bursar can access

- `edupro_sms/www/bursar-students/add-student.html` — Add student form
  - Form fields: Name, Email, DOB, Gender, Admission Number, Boarding Type
  - Submit button
  - Form validation (email format, DOB is date, etc.)

- `edupro_sms/www/bursar-students/edit-student.html` — Edit student form
  - Same fields as add
  - Deactivate button (with confirmation)

**Subtasks:**
- [ ] Create student list table (sortable, searchable)
- [ ] Create add student form with validation
- [ ] Create edit student form with pre-filled data
- [ ] Add AJAX calls to backend API
- [ ] Show success/error messages
- [ ] Add enrollment form (select program, academic year → shows courses)
- [ ] Add guardian linking form (select or create)

**Estimated Time:** 4-5 days

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
